"""Auth0 access-token validation for the surveys API.

Django has no dependency-injection layer, so the three access tiers are exposed
as view decorators. Each one attaches an ``AuthUser`` (or ``None``) to
``request.auth_user`` so the view can read the caller's identity without
re-parsing the token.

    @require_auth                       protected; 401 without a valid token
    @optional_auth                      guests allowed; a *bad* token still 401s
    @require_permission("read:x")       protected + RBAC permission check

Failure modes are deliberately distinct: a bad token is a 401, an unreachable
JWKS endpoint is a 503, and a backend missing its own Auth0 configuration is a
500. A misconfigured server must fail loudly rather than accept every token.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, List, Optional

import jwt
from django.conf import settings
from django.http import JsonResponse

# Pinned. Never read `alg` from the token itself -- that lets an attacker pick
# `none` or downgrade to HS256 and sign with a value they control.
ALGORITHMS = ["RS256"]


@dataclass(frozen=True)
class AuthUser:
    """A verified caller. ``claims`` is the decoded, validated token payload."""

    sub: str
    claims: Dict[str, Any]

    @property
    def permissions(self) -> List[str]:
        """RBAC permissions, present only when the API has RBAC enabled."""
        return list(self.claims.get("permissions", []))

    @property
    def email(self) -> Optional[str]:
        return self.claims.get("email")


class AuthError(Exception):
    """Base class for anything that should short-circuit a view with a response."""

    status = 401

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail

    def as_response(self) -> JsonResponse:
        response = JsonResponse({"message": self.detail}, status=self.status)
        if self.status == 401:
            response["WWW-Authenticate"] = "Bearer"
        return response


class AuthUnauthorized(AuthError):
    """The credential is missing, malformed, expired or forged."""

    status = 401


class AuthForbidden(AuthError):
    """The caller is authenticated but lacks the required permission."""

    status = 403


class AuthUnavailable(AuthError):
    """The Auth0 JWKS endpoint could not be reached."""

    status = 503


class AuthMisconfigured(AuthError):
    """This server is missing AUTH0_DOMAIN / AUTH0_AUDIENCE."""

    status = 500


def _auth0_settings() -> tuple[str, str]:
    domain = (getattr(settings, "AUTH0_DOMAIN", "") or "").strip()
    audience = (getattr(settings, "AUTH0_AUDIENCE", "") or "").strip()
    if not domain or not audience:
        raise AuthMisconfigured(
            "Auth0 is not configured. Set AUTH0_DOMAIN and AUTH0_AUDIENCE."
        )
    return domain, audience


@lru_cache(maxsize=4)
def _jwks_client(domain: str) -> jwt.PyJWKClient:
    """Cached per tenant; PyJWKClient also caches the keys it fetches."""
    return jwt.PyJWKClient(f"https://{domain}/.well-known/jwks.json")


def verify_access_token(token: str) -> AuthUser:
    """Validate an Auth0 RS256 access token and return the verified caller."""
    domain, audience = _auth0_settings()

    try:
        signing_key = _jwks_client(domain).get_signing_key_from_jwt(token)
    except jwt.PyJWKClientConnectionError as exc:
        raise AuthUnavailable("Could not fetch Auth0 signing keys.") from exc
    except jwt.PyJWKClientError as exc:
        raise AuthUnauthorized("Invalid token: no matching signing key.") from exc
    except jwt.DecodeError as exc:
        raise AuthUnauthorized("Invalid token.") from exc

    try:
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=ALGORITHMS,
            audience=audience,
            # The trailing slash is part of the issuer. Without it every token
            # fails validation for a reason that reads like a signature problem.
            issuer=f"https://{domain}/",
            # Require the claims to be *present*, not merely correct: a token
            # with no `aud` at all must be rejected, not have the check skipped.
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthUnauthorized("Token has expired.") from exc
    except jwt.InvalidAudienceError as exc:
        raise AuthUnauthorized("Invalid token audience.") from exc
    except jwt.InvalidIssuerError as exc:
        raise AuthUnauthorized("Invalid token issuer.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthUnauthorized("Invalid token.") from exc

    sub = claims.get("sub")
    if not sub:
        raise AuthUnauthorized("Token is missing the sub claim.")
    return AuthUser(sub=sub, claims=claims)


def _bearer_token(request) -> Optional[str]:
    """Pull the bearer token out of the Authorization header.

    Returns None only when no credential was offered at all. A malformed header
    raises, because a bad credential and an absent one are different things --
    on optional-auth routes the first must 401 while the second is a guest.
    """
    header = request.META.get("HTTP_AUTHORIZATION", "").strip()
    if not header:
        return None

    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthUnauthorized("Authorization header must be 'Bearer <token>'.")
    if not parts[1].strip():
        raise AuthUnauthorized("Missing bearer token.")
    return parts[1]


def require_auth(view: Callable) -> Callable:
    """Protected: 401 unless the request carries a valid access token."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            token = _bearer_token(request)
            if token is None:
                raise AuthUnauthorized("Missing bearer token.")
            request.auth_user = verify_access_token(token)
        except AuthError as exc:
            return exc.as_response()
        return view(request, *args, **kwargs)

    return wrapper


def optional_auth(view: Callable) -> Callable:
    """Anonymous allowed; identity is used when a valid token is sent.

    An invalid token is still a 401. If a forged token silently downgraded to
    "guest", the scheme would be decorative -- an attacker just sends garbage.
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        try:
            token = _bearer_token(request)
            request.auth_user = verify_access_token(token) if token else None
        except AuthError as exc:
            return exc.as_response()
        return view(request, *args, **kwargs)

    return wrapper


def require_permission(permission: str) -> Callable:
    """Protected + RBAC: the token must carry ``permission``.

    Requires the Auth0 API to have RBAC and "Add Permissions in the Access
    Token" enabled, otherwise no token carries permissions and every call 403s.
    """

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        @require_auth
        def wrapper(request, *args, **kwargs):
            if permission not in request.auth_user.permissions:
                return AuthForbidden(
                    f"This account is missing the '{permission}' permission."
                ).as_response()
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


def require_user_sub(request) -> str:
    """The caller's Auth0 subject. Only valid inside a @require_auth view."""
    return request.auth_user.sub
