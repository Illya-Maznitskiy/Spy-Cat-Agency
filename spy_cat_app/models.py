from django.db import models
from rest_framework.exceptions import ValidationError
from spy_cat_app.validators import validate_breed


class SpyCat(models.Model):
    name = models.CharField(max_length=100)
    years_of_experience = models.IntegerField()
    breed = models.CharField(max_length=100, validators=[validate_breed])
    salary = models.IntegerField()

    def __str__(self):
        return self.name


class Target(models.Model):
    name = models.CharField(max_length=100)
    mission = models.ForeignKey(
        "Mission", related_name="targets", on_delete=models.CASCADE
    )
    country = models.CharField(max_length=100)
    notes = models.TextField()
    complete_state = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Prevent notes from being updated if target is completed
        if self.complete_state and self.pk is not None:  # already exists
            original = Target.objects.get(pk=self.pk)
            if (
                original.complete_state != self.complete_state
                and self.notes != original.notes
            ):
                raise ValidationError(
                    "Notes cannot be updated once the target is complete."
                )
        super().save(*args, **kwargs)


class Mission(models.Model):
    cat = models.OneToOneField(SpyCat, on_delete=models.CASCADE)
    complete_state = models.BooleanField(default=False)

    def __str__(self):
        return self.cat.name

    def clean(self):
        super().clean()
        # Ensure the mission has between 1 and 3 targets
        if not (1 <= len(self.targets.all()) <= 3):
            raise ValidationError(
                "A mission must have between 1 and 3 targets."
            )

    def delete(self, *args, **kwargs):
        if self.cat:
            raise ValidationError("Cannot delete a mission assigned to a cat.")
        super().delete(*args, **kwargs)
