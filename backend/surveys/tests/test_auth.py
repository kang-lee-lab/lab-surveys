"""Token validation and the tier each route sits in."""

import time

import jwt
from django.test import SimpleTestCase, TestCase, override_settings

from .tokens import (
    AUDIENCE,
    DOMAIN,
    FOREIGN_PRIVATE_PEM,
    ISSUER,
    bearer,
    make_token,
    stub_jwks,
)

ME = "/surveys/me"


@override_settings(AUTH0_DOMAIN=DOMAIN, AUTH0_AUDIENCE=AUDIENCE)
class TokenValidationTests(SimpleTestCase):
    """Each case here exists because skipping it is exploitable."""

    def assert_rejected(self, header, message=""):
        with stub_jwks():
            response = self.client.get(ME, HTTP_AUTHORIZATION=header)
        self.assertEqual(response.status_code, 401, message)
        # A 401 must carry the challenge, or clients cannot tell what to do.
        self.assertEqual(response["WWW-Authenticate"], "Bearer")

    def test_valid_token_is_accepted(self):
        with stub_jwks():
            response = self.client.get(ME, HTTP_AUTHORIZATION=bearer())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sub"], "auth0|test-user")

    def test_missing_header(self):
        with stub_jwks():
            response = self.client.get(ME)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["WWW-Authenticate"], "Bearer")

    def test_empty_bearer(self):
        # An empty "Bearer " is an invalid credential, not an absent one.
        self.assert_rejected("Bearer ")

    def test_garbage_token(self):
        self.assert_rejected("Bearer not-a-token")

    def test_wrong_scheme(self):
        self.assert_rejected("Basic dXNlcjpwYXNz")

    def test_expired_token(self):
        self.assert_rejected(bearer(exp=int(time.time()) - 10))

    def test_wrong_audience(self):
        # A token minted for another API must not open this one.
        self.assert_rejected(bearer(aud="urn:some-other-api"))

    def test_wrong_issuer(self):
        self.assert_rejected(bearer(iss="https://attacker.example.com/"))

    def test_issuer_without_trailing_slash(self):
        # The trailing slash is part of the issuer; a frequent silent failure.
        self.assert_rejected(bearer(iss=f"https://{DOMAIN}"))

    def test_missing_sub_claim(self):
        # Claims must be present, not merely correct.
        self.assert_rejected(bearer(sub=None))

    def test_missing_audience_claim(self):
        self.assert_rejected(bearer(aud=None))

    def test_forged_signature_with_a_real_kid(self):
        """The case worth insisting on.

        A token signed with a foreign key but carrying a kid the tenant really
        publishes. Code that parses headers without verifying signatures passes
        every other test here and fails only this one.
        """
        self.assert_rejected(f"Bearer {make_token(private_pem=FOREIGN_PRIVATE_PEM)}")

    def test_hs256_downgrade_is_rejected(self):
        """RS256 is pinned, so an attacker cannot pick the algorithm."""
        token = jwt.encode(
            {
                "sub": "auth0|attacker",
                "iss": ISSUER,
                "aud": AUDIENCE,
                "exp": int(time.time()) + 300,
            },
            "a-symmetric-secret-long-enough-for-hs256",
            algorithm="HS256",
            headers={"kid": "test-signing-key"},
        )
        self.assert_rejected(f"Bearer {token}")

    def test_jwks_unreachable_is_503_not_401(self):
        error = jwt.PyJWKClientConnectionError("network down")
        with stub_jwks(error=error):
            response = self.client.get(ME, HTTP_AUTHORIZATION=bearer())
        self.assertEqual(response.status_code, 503)


class MisconfiguredBackendTests(SimpleTestCase):
    @override_settings(AUTH0_DOMAIN=DOMAIN, AUTH0_AUDIENCE="")
    def test_missing_audience_fails_loudly(self):
        """A server with no audience configured must not accept everything.

        If a missing AUTH0_AUDIENCE were read as "no audience to check", every
        forged token would validate. It has to be a 500.
        """
        with stub_jwks():
            response = self.client.get(ME, HTTP_AUTHORIZATION=bearer())
        self.assertEqual(response.status_code, 500)

    @override_settings(AUTH0_DOMAIN="", AUTH0_AUDIENCE=AUDIENCE)
    def test_missing_domain_fails_loudly(self):
        with stub_jwks():
            response = self.client.get(ME, HTTP_AUTHORIZATION=bearer())
        self.assertEqual(response.status_code, 500)


@override_settings(AUTH0_DOMAIN=DOMAIN, AUTH0_AUDIENCE=AUDIENCE)
class EndpointTierTests(TestCase):
    """Every route sits in the tier backend/README.md says it does."""

    PUBLIC = [
        "/surveys/",
        "/surveys/wakeup",
        "/surveys/catalog",
        "/surveys/survey/asq",
    ]
    STAFF = [
        "/surveys/history",
        "/surveys/history/asq/",
        "/surveys/download-csv",
    ]

    def test_public_routes_need_no_token(self):
        for path in self.PUBLIC:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_protected_route_requires_a_token(self):
        with stub_jwks():
            self.assertEqual(self.client.get(ME).status_code, 401)
            self.assertEqual(
                self.client.get(ME, HTTP_AUTHORIZATION=bearer()).status_code, 200
            )

    def test_optional_route_admits_guests_but_rejects_bad_tokens(self):
        # A GET reaches the view's own "POST only" 400, which is the proof it
        # got past auth as a guest.
        self.assertEqual(self.client.get("/surveys/results").status_code, 400)
        with stub_jwks():
            forged = make_token(private_pem=FOREIGN_PRIVATE_PEM)
            response = self.client.get(
                "/surveys/results", HTTP_AUTHORIZATION=f"Bearer {forged}"
            )
        # A bad token must not silently downgrade to guest, or an attacker just
        # sends garbage to reach the anonymous path.
        self.assertEqual(response.status_code, 401)

    def test_staff_routes(self):
        for path in self.STAFF:
            with self.subTest(path=path):
                with stub_jwks():
                    self.assertEqual(self.client.get(path).status_code, 401)
                    self.assertEqual(
                        self.client.get(path, HTTP_AUTHORIZATION=bearer()).status_code,
                        403,
                        "signed in without the permission must be 403, not 200",
                    )
                    staff = bearer(permissions=["read:responses"])
                    self.assertEqual(
                        self.client.get(path, HTTP_AUTHORIZATION=staff).status_code,
                        200,
                    )
