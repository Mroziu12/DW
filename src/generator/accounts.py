from faker import Faker
from datetime import datetime
import random
from utils.settings import SAVINGS_ACCOUNT_PROBABILITY, SIMULATION_START_DATE
from utils.counters import *

fake = Faker("pl_PL")

def generate_accounts(customers):
    global acc_ctr
    accounts = []
    acc_base = 10000
    acc_id = acc_base + acc_ctr +1


    sim_start = datetime.strptime(SIMULATION_START_DATE, "%Y-%m-%d")

    for customer in customers:
        # Konto PERSONAL
        open_date = fake.date_between(start_date=sim_start, end_date="today").strftime("%Y-%m-%d")
        personal_account = {
            "Account_Number": acc_id,
            "Type": "Personal",
            "Open_Date": open_date,
            "Balance": round(random.uniform(1000, 10000), 2),
            "CustomerID": customer["Pesel"]
        }
        accounts.append(personal_account)
        acc_id +=1
        # Konto SAVINGS
        if random.random() < SAVINGS_ACCOUNT_PROBABILITY:
            open_date = fake.date_between(start_date=sim_start, end_date="today").strftime("%Y-%m-%d")
            savings_account = {
                "Account_Number": acc_id,
                "Type": "Savings",
                "Open_Date": open_date,
                "Balance": round(random.uniform(500, 20000), 2),
                "CustomerID": customer["Pesel"]
            }
            accounts.append(savings_account)
            acc_id +=1
    acc_ctr = acc_id - acc_base
    return accounts
