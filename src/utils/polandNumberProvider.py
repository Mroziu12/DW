from faker import Faker
from faker.providers.phone_number import Provider

class PolandPhoneNumberProvider(Provider):
    """
    A Provider for phone number.
    """

    def poland_phone_number(self):
        return f'48{self.msisdn()[4:]}'