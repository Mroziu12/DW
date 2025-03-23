from utils.settings import *
import random
from datetime import datetime, timedelta
import random
from utils.settings import LOAN_PAYMENT_MAX_PROB, LOAN_PAYMENT_MIN_PROB
from faker import Faker
from utils.settings import LOAN_APPROVAL_PROB, DEFAULT_GRACE_DAYS
from utils.credit_bias_config import *
from utils.counters import *

def simulate_day(current_date, customers, employees, accounts, loans, payments, transactions, questionnaires, account_links):
    # --- 1. Losowe transakcje przychodzące/wychodzące ---
    for acc in accounts:
        if random.random() < DAILY_TRANSACTION_PROB:
            simulate_random_transaction(acc, accounts, current_date, transactions, account_links)

    # --- 2. Formularz kredytowy ---
    for cust in customers:
        if random.random() < CREDIT_APPLICATION_PROB:
            form, decision = create_credit_questionnaire(cust, employees, current_date)
            questionnaires.append(form)
            if decision == "Accepted":
                loan, new_payments = create_loan_and_schedule(cust, form, current_date, employees)
                loans.append(loan)
                payments.extend(new_payments)

    # --- 3. Spłata rat kredytów ---
    for loan in loans:
        simulate_loan_payment(current_date, loan, payments)
        check_if_loan_defaulted(current_date,loan,payments)

def simulate_random_transaction(source_account, all_accounts, date, transactions, account_links):
    global transaction_ctr
    # Avoid self-transfers
    target_account= random.choice(all_accounts)
    if source_account == target_account:
        return




    amount = round(random.uniform(10, 500), 2)
    if source_account["Balance"] < amount:
        return

    # Create transaction
    transaction_ctr = len(transactions)
    tx_id = transaction_ctr + 1
    transaction_ctr +=1
    transactions.append({
        "TransactionID": tx_id,
        "Amount": amount,
        "Date": date.strftime("%Y-%m-%d")
    })

    account_links.append({
        "TransactionID": tx_id,
        "Sender_AccountID": source_account["Account_Number"],
        "Receiver_AccountID": target_account["Account_Number"]
    })

    # Update balances
    source_account["Balance"] = round(source_account["Balance"] - amount, 2)
    target_account["Balance"] = round(target_account["Balance"] + amount, 2)


fake = Faker("pl_PL")

EDU_LEVELS = ["Secondary", "Higher education", "Incomplete higher education"]
HOUSING = ["Rented apartment", "Owned house", "Living with parents"]
OCCUPATIONS = ["Laborer", "Manager", "Self-employed"]

def create_credit_questionnaire(customer, employees, current_date):
    global quest_ctr
    form = {
        "Q_ID": quest_ctr +1,
        "CL_ID": customer["Pesel"],
        "CL_GENDER": random.choice(["M", "F"]),
        "CL_CHILDREN": random.randint(0, 4),
        "CL_M_INCOME": round(random.uniform(2000, 15000), 2),
        "DES_CRED_VAL": round(random.uniform(1000, 30000), 2),
        "CL_EDU": random.choice(EDU_LEVELS),
        "CL_HOUSE_SIT": random.choice(HOUSING),
        "CL_OCCUPATION": random.choice(OCCUPATIONS),
        "Q_DATE": current_date.strftime("%Y-%m-%d"),
        "CR_RET_DATE": (current_date + timedelta(days=30 * random.randint(6, 24))).strftime("%Y-%m-%d"),
        "E_ASSIST": random.choice([e["EmployeeID"] for e in employees] + [0,0,0,0])  # 0 = no help
    }
    quest_ctr +=1
    # Calculate risk + decision
    risk_score = calculate_risk(form)
    form["RISK_CALC"] = risk_score
    form["CR_DECISION"] = "Accepted" if risk_score < 6.0 else "Rejected"

    age = get_age_from_pesel(str(form["CL_ID"]))
    if age >60 and random.random() < 0.95 and form["E_ASSIST"] == 0:
        form["E_ASSIST"] = random.choice([e["EmployeeID"] for e in employees])
    elif age <30 and random.random() < 0.80:
        form["E_ASSIST"] = 0

    return form, form["CR_DECISION"]

def create_loan_and_schedule(customer, form, current_date, employees):
    global loan_payment_ctr
    global loan_ctr
    loan_id = loan_ctr +1
    loan_ctr +=1
    amount = form.get("DES_CRED_VAL")
    ret_date = datetime.strptime(form["CR_RET_DATE"], "%Y-%m-%d")
    months = max(3, (ret_date.year - current_date.year) * 12 + (ret_date.month - current_date.month))
    payment_amount = round(amount / months, 2)

    loan = {
        "LoanID": loan_id,
        "Type": "Standard",
        "Amount": amount,
        "Interest_Rate": round(random.uniform(3.0, 8.0), 2),
        "Approval_Date": current_date.strftime("%Y-%m-%d"),
        "Final_Repayment_Date": (current_date + timedelta(days=30 * months)).strftime("%Y-%m-%d"),
        "Date_Of_Credit_Closing": None,
        "Status": "Active",
        "Customer_ID": customer["Pesel"],
        "Employee_ID": random.choice(employees)["EmployeeID"]
    }

    payments = []
    for i in range(months):
        due_date = current_date + timedelta(days=30 * (i + 1))
        payments.append({
            "PaymentID": loan_payment_ctr+1,
            "Amount": payment_amount,
            "Date": None,
            "Status": "to-be-made",
            "Date_of_expected_payment": due_date.strftime("%Y-%m-%d"),
            "LoanID": loan_id
        })
        loan_payment_ctr+=1

    return loan, payments

def calculate_risk(form):
    risk = random.uniform(*BASE_RISK_RANGE)

    # Gender bias
    gender = form.get("CL_GENDER")
    risk += GENDER_RISK_ADJUSTMENT.get(gender, 0)

    # Children bias
    children = int(form.get("CL_CHILDREN", 0))
    risk += CHILDREN_RISK_ADJUSTMENT.get(children, CHILDREN_RISK_ADJUSTMENT["default"])

    # Education bias
    edu = form.get("CL_EDU")
    risk += EDUCATION_RISK_ADJUSTMENT.get(edu, EDUCATION_RISK_ADJUSTMENT["default"])

    # Income bias (scaling)
    income = float(form.get("CL_M_INCOME", 0))
    income_adjustment = max(INCOME_RISK_SCALING["max_adjustment"],
                            income * INCOME_RISK_SCALING["scale_factor"])
    risk += income_adjustment

    age = get_age_from_pesel(str(form["CL_ID"]))

    for rule in AGE_RISK_ADJUSTMENT:
        if rule["min"] <= age <= rule["max"]:
            risk += rule["adjustment"]
            break

    # Clamp risk to [1, 10]
    return round(max(1.0, min(10.0, risk)), 2)



  # after which it becomes 'defaulted'

def simulate_loan_payment(current_date, loan, payments):
    if loan["Status"] != "Active":
        return

    # Sort pending payments by due date
    pending = sorted(
        [p for p in payments if p["LoanID"] == loan["LoanID"] and p["Status"] == "to-be-made"],
        key=lambda p: p["Date_of_expected_payment"]
    )

    if not pending:
        return
    payment = pending[0]
    due_date = datetime.strptime(payment["Date_of_expected_payment"], "%Y-%m-%d")
    days_until_due = (due_date - current_date).days
    days_overdue = (current_date - due_date).days




    # Determine probability based on how close we are to due date
    if days_until_due < 0:
        scale = 1.0
    else:
        scale = max(0, min(1, 1 - days_until_due / 30))  # closer to due = higher prob

    prob = (LOAN_PAYMENT_MIN_PROB + (LOAN_PAYMENT_MAX_PROB - LOAN_PAYMENT_MIN_PROB) * scale)

    if random.random() < prob:
        payment["Status"] = "on-time" if current_date <= due_date else "late"
        payment["Date"] = current_date.strftime("%Y-%m-%d")
        if len(pending)==1:
            loan["Status"] = "Closed"
            loan["Date_Of_Credit_Closing"] = current_date.strftime("%Y-%m-%d")
            return

def check_if_loan_defaulted(current_date,loan,payments):
    due_date = datetime.strptime(loan["Final_Repayment_Date"], "%Y-%m-%d")
    days_overdue = (current_date - due_date).days
    if days_overdue > DEFAULT_GRACE_DAYS:
        loan["Status"] = "defaulted"
        for payment in payments:
            if payment["LoanID"] == loan["LoanID"]:
                if payment["Status"] == "to-be-made":
                    payment["Status"] = "defaulted"


def get_birthdate_from_pesel(pesel: str) -> datetime:
    year = int(pesel[0:2])
    month = int(pesel[2:4])
    day = int(pesel[4:6])

    # Rozszyfrowanie stulecia
    if 1 <= month <= 12:
        century = 1900
    elif 21 <= month <= 32:
        century = 2000
        month -= 20
    elif 41 <= month <= 52:
        century = 2100
        month -= 40
    elif 61 <= month <= 72:
        century = 2200
        month -= 60
    elif 81 <= month <= 92:
        century = 1800
        month -= 80
    else:
        raise ValueError("Niepoprawny PESEL")

    full_year = century + year
    return datetime(full_year, month, day)

def get_age_from_pesel(pesel: str) -> int:
    birth_date = get_birthdate_from_pesel(pesel)
    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

