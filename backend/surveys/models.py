from django.db import models


class Participant(models.Model):
    """A person who has signed in, keyed on their Auth0 subject.

    There is no registration step: the first authenticated request for an
    unseen `auth0_sub` creates the row.

    Only identity lives here. `auth0_sub` is the join key -- never email, which
    users change, which providers reissue to different accounts, and which not
    every connection returns at all.
    """

    id = models.BigAutoField(primary_key=True)
    # The UNIQUE constraint is what makes get-or-create safe under concurrent
    # first requests, and it is painful to add later once duplicates exist.
    auth0_sub = models.CharField(max_length=255, unique=True, db_index=True)
    # Display only, and only ever populated when the access token actually
    # carries the claim -- by default an Auth0 access token does not.
    email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.auth0_sub


class Response(models.Model):
    id = models.AutoField(primary_key=True)
    # Null for rows recorded before sign-in existed. New responses are only
    # saved for signed-in participants, so nothing written from here on is
    # unattributed. Cascade so erasing a participant erases their data.
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="responses",
        null=True,
        blank=True,
    )
    response_type = models.CharField(max_length=100)
    response_answers = models.JSONField()
    response_results = models.JSONField()
    response_date = models.DateField()
    response_time = models.TimeField()
    response_duration = models.DurationField(null=True, blank=True)
