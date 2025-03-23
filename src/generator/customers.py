from faker import Faker
from datetime import datetime, timedelta
import random
from utils.polandNumberProvider import PolandPhoneNumberProvider
from utils.settings import N_CUSTOMERS

fake = Faker("pl_PL")

fake.add_provider(PolandPhoneNumberProvider)


def generate_customers(n_customers=N_CUSTOMERS):
    customers = []

    for i in range(n_customers):
        # Upewnijmy się, że klient ma co najmniej 18 lat
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=75)
        pesel = generate_pesel(birth_date)

        customer = {
            "Pesel": pesel,  # CL_ID i Pesel są takie same
            "Name": fake.first_name(),
            "Surname": fake.last_name(),
            "Date_Of_Birth": birth_date.strftime("%Y-%m-%d"),
            "Phone_Number": fake.poland_phone_number(),
            "Email": fake.email(),
            "Address": fake.address().replace("\n", ", ")
        }

        customers.append(customer)

    return customers

import os
import pandas as pd


def generate_pesel(date_of_birth: datetime) -> str:
    year = date_of_birth.year
    month = date_of_birth.month
    day = date_of_birth.day

    # Zakodowanie wieku w miesiącu
    if 1800 <= year < 1900:
        month += 80
    elif 1900 <= year < 2000:
        month += 0
    elif 2000 <= year < 2100:
        month += 20
    elif 2100 <= year < 2200:
        month += 40
    elif 2200 <= year < 2300:
        month += 60

    # Składanie numeru
    rr = str(year % 100).zfill(2)
    mm = str(month).zfill(2)
    dd = str(day).zfill(2)
    ppppp = str(random.randint(0, 99999)).zfill(5)

    base = f"{rr}{mm}{dd}{ppppp}"
    return base