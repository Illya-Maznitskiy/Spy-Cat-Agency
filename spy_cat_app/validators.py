import requests
from django.core.exceptions import ValidationError

CAT_API_URL = "https://api.thecatapi.com/v1/breeds"


def validate_breed(breed_name):
    """Validate the breed using TheCatAPI (public API, no key required)."""
    response = requests.get(CAT_API_URL)

    if response.status_code != 200:
        raise ValidationError("Error contacting the breed validation service")

    breeds = response.json()
    breed_names = [breed["name"].lower() for breed in breeds]

    if breed_name.lower() not in breed_names:
        raise ValidationError(f"Invalid breed: {breed_name}")
