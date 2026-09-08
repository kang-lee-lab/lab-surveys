"""Identity persistence: who gets a row, and who can read it."""

import json

from django.test import TestCase, override_settings

from surveys.models import Participant, Response

from .tokens import AUDIENCE, DOMAIN, bearer, stub_jwks

RESULTS = "/surveys/results"
MY_RESPONSES = "/surveys/participants/me/responses"


@override_settings(AUTH0_DOMAIN=DOMAIN, AUTH0_AUDIENCE=AUDIENCE)
class ParticipantPersistenceTests(TestCase):
    def submit(self, header=None, number1=1, number2=1):
        body = {
            "survey": "sample_survey",
            "data": {
                "Number1": number1,
                "Number2": number2,
                "experience_rating": 7,
                "gender": "1",
            },
            "duration": 12,
        }
        extra = {"HTTP_AUTHORIZATION": header} if header else {}
        with stub_jwks():
            return self.client.post(
                RESULTS, data=json.dumps(body), content_type="application/json", **extra
            )

    def counts(self):
        return Participant.objects.count(), Response.objects.count()

    def test_guest_submission_is_calculated_but_not_stored(self):
        self.assertEqual(self.submit().status_code, 200)
        self.assertEqual(self.counts(), (0, 0))

    def test_repeat_submissions_reuse_one_participant(self):
        """The participant count staying at 1 is the assertion.

        It proves the get-or-create matched the existing row rather than
        inserting a duplicate -- the thing most likely to be silently wrong.
        """
        alice = bearer(sub="auth0|alice")
        self.submit(alice)
        self.assertEqual(self.counts(), (1, 1))
        self.submit(alice)
        self.assertEqual(self.counts(), (1, 2))

    def test_second_user_gets_their_own_participant(self):
        self.submit(bearer(sub="auth0|alice"))
        self.submit(bearer(sub="auth0|bob"))
        self.assertEqual(self.counts(), (2, 2))

    def test_guest_submission_after_a_signed_in_one_stores_nothing(self):
        self.submit(bearer(sub="auth0|alice"))
        self.submit()
        self.assertEqual(self.counts(), (1, 1))

    def test_response_is_attributed_to_the_participant(self):
        self.submit(bearer(sub="auth0|alice"))
        participant = Participant.objects.get(auth0_sub="auth0|alice")
        self.assertEqual(participant.responses.count(), 1)


@override_settings(AUTH0_DOMAIN=DOMAIN, AUTH0_AUDIENCE=AUDIENCE)
class ResponseIsolationTests(TestCase):
    def submit(self, header, number1, number2):
        body = {
            "survey": "sample_survey",
            "data": {
                "Number1": number1,
                "Number2": number2,
                "experience_rating": 7,
                "gender": "1",
            },
            "duration": 12,
        }
        with stub_jwks():
            return self.client.post(
                RESULTS,
                data=json.dumps(body),
                content_type="application/json",
                HTTP_AUTHORIZATION=header,
            )

    def list_for(self, header):
        with stub_jwks():
            return self.client.get(MY_RESPONSES, HTTP_AUTHORIZATION=header)

    def test_requires_authentication(self):
        with stub_jwks():
            self.assertEqual(self.client.get(MY_RESPONSES).status_code, 401)

    def test_each_participant_sees_only_their_own(self):
        alice = bearer(sub="auth0|alice")
        bob = bearer(sub="auth0|bob")
        # 20 + 22 gives Alice a distinctive score of 42.
        self.submit(alice, 20, 22)
        self.submit(alice, 1, 1)
        self.submit(bob, 3, 4)

        self.assertEqual(len(self.list_for(alice).json()), 2)

        bobs_response = self.list_for(bob)
        self.assertEqual(len(bobs_response.json()), 1)
        # Assert on content, not just the count: a status code and a length
        # both pass even when another participant's data is in the body.
        self.assertNotIn("42", bobs_response.content.decode())
