from faker import Faker

from src.auth.schemas import CredentialsSchema

_faker = Faker()


def make_credentials():
    return CredentialsSchema(
        username=_faker.user_name(),
        password=_faker.password(),
        email=_faker.email(),
    ).to_dict()


def make_sub():
    return _faker.random_int(1, 100)
