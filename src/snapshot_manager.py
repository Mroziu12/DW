
import os
import pandas as pd
import copy
from utils.schema import DATABASE_SCHEMA

from datetime import datetime, timedelta
from generator.customers import generate_customers
from generator.employees import generate_branches, generate_employees
from generator.accounts import generate_accounts
from generator.transactions import generate_initial_transactions
from utils.settings import *
from simulation import simulate_day


def simulate_and_create_snapshots(date_A: str, date_B: str):
    snapshot_A_date = datetime.strptime(date_A, "%Y-%m-%d")
    snapshot_B_date = datetime.strptime(date_B, "%Y-%m-%d")
    simulation_start = datetime.strptime(SIMULATION_START_DATE, "%Y-%m-%d")

    print("🔧 Generuję dane początkowe...")

    # --- Etap 0: dane bazowe ---
    branches = generate_branches()
    employees = generate_employees(branches)
    customers = generate_customers()
    accounts = generate_accounts(customers)
    transactions, account_links = generate_initial_transactions(accounts)

    loans = []
    payments = []
    questionnaires = []

    # --- Symulacja dni między 0 a A ---
    print("🧪 Symulacja od 0 do A – tutaj będzie logika symulacyjna")

    current_date = simulation_start+ timedelta(days=1)
    while current_date <= snapshot_A_date:
        # Placeholder na przyszłą symulację codzienną
        simulate_day(current_date,customers,employees,accounts,loans,payments,transactions,questionnaires,account_links)
        current_date += timedelta(days=DAY_SPAN)

    # --- Snapshot A ---
    snapshot_A_state = copy.deepcopy({
        "branches": branches,
        "employees": employees,
        "customers": customers,
        "accounts": accounts,
        "transactions": transactions,
        "account_links": account_links,
        "loans": loans,
        "payments": payments,
        "questionnaires": questionnaires
    })

    print("📸 Eksportuję snapshot A")
    export_snapshot("A", snapshot_A_state)

    # --- Symulacja dni między A a B ---
    print("🧪 Symulacja od A do B – tutaj będzie logika symulacyjna")

    current_date = snapshot_A_date + timedelta(days=1)
    while current_date <= snapshot_B_date:
        # Placeholder na przyszłą symulację codzienną
        simulate_day(current_date,customers,employees,accounts,loans,payments,transactions,questionnaires,account_links)
        current_date += timedelta(days=DAY_SPAN)

    # --- Snapshot B ---
    snapshot_B_state = {
        "branches": branches,
        "employees": employees,
        "customers": customers,
        "accounts": accounts,
        "transactions": transactions,
        "account_links": account_links,
        "loans": loans,
        "payments": payments,
        "questionnaires": questionnaires
    }

    print("📸 Eksportuję snapshot B")
    export_snapshot("B", snapshot_B_state, diff_against=snapshot_A_state)

    print("✅ Zakończono tworzenie snapshotów")


def export_snapshot(label, state, diff_against=None):
    output_dir = f"output/snapshot_{label}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"📤 Eksportuję snapshot {label}...")

    # Eksport CSV formularzy
    export_credit_questionnaire_csv(state["questionnaires"], output_dir, label)

    # Eksport SQL-a do bazy
    export_sql_bulk(
        customers=state["customers"],
        loans=state["loans"],
        payments=state["payments"],
        transactions=state["transactions"],
        account_links=state["account_links"],
        employees=state["employees"],
        branches=state["branches"],
        accounts=state["accounts"],
        snapshot_label=label,
        output_dir=output_dir,
        diff_against=diff_against
    )

    print(f"✅ Snapshot {label} gotowy: {output_dir}/")


def export_credit_questionnaire_csv(forms, output_dir, label):
    df = pd.DataFrame(forms)
    filename = f"{output_dir}/credit_questionnaire_{label}.csv"
    df.to_csv(filename, index=False)

def generate_insert_sql(table_name, row_dict, schema):
    values = []
    for col in schema[table_name]:
        val = row_dict.get(col)
        if isinstance(val, str):
            val = val.replace("'", "''")  # Escape apostrofy
            val = f"'{val}'"
        elif val is None:
            val = "NULL"
        else:
            val = str(val)
        values.append(val)

    columns = ", ".join(schema[table_name])
    values_str = ", ".join(values)
    return f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});"


def generate_update_sql(table_name, old_obj, new_obj, key_field, schema):
    set_clauses = []

    for col in schema[table_name]:
        if col == key_field:
            continue
        old_val = old_obj.get(col)
        new_val = new_obj.get(col)
        if old_val != new_val:
            if isinstance(new_val, str):
                new_val = new_val.replace("'", "''")
                val = f"'{new_val}'"
            elif new_val is None:
                val = "NULL"
            else:
                val = str(new_val)
            set_clauses.append(f"{col} = {val}")

    if not set_clauses:
        return None  # Brak zmian

    where_clause = f"{key_field} = '{new_obj[key_field]}'" if isinstance(new_obj[key_field], str) else f"{key_field} = {new_obj[key_field]}"
    return f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {where_clause};"


def export_sql_bulk(
        customers,
        employees,
        branches,
        accounts,
        transactions,
        account_links,
        loans,
        payments,
        snapshot_label,
        output_dir,
        diff_against=None
):
    lines = []

    def export_entities(entities, table_name, key_field, previous_entities=None):
        previous_ids = set()
        if previous_entities:
            previous_ids = {e[key_field] for e in previous_entities}

        for entity in entities:
            if previous_entities and entity[key_field] in previous_ids:
                continue  # Pomijamy jeśli już istniał w snapshot A
            sql = generate_insert_sql(table_name, entity, DATABASE_SCHEMA)
            lines.append(sql)

    # --- INSERTY dla snapshotu A (lub nowe obiekty w B) ---
    export_entities(branches, "Branch", "BranchID", diff_against.get("branches") if diff_against else None)
    export_entities(employees, "Employee", "EmployeeID", diff_against.get("employees") if diff_against else None)
    export_entities(customers, "Customer", "Pesel", diff_against.get("customers") if diff_against else None)
    export_entities(accounts, "Account", "Account_Number", diff_against.get("accounts") if diff_against else None)
    export_entities(transactions, "Transaction", "TransactionID", diff_against.get("transactions") if diff_against else None)
    export_entities(account_links, "Account_Transaction", "TransactionID", diff_against.get("account_links") if diff_against else None)
    export_entities(loans, "Loan", "LoanID", diff_against.get("loans") if diff_against else None)
    export_entities(payments, "Loan_Payment", "PaymentID", diff_against.get("payments") if diff_against else None)

    # --- UPDATE’y tylko dla snapshotu B ---
    if diff_against:
        # Account: Balance
        old_accounts = {a["Account_Number"]: a for a in diff_against.get("accounts", [])}
        for acc in accounts:
            if acc["Account_Number"] in old_accounts:
                sql = generate_update_sql("Account", old_accounts[acc["Account_Number"]], acc, "Account_Number", DATABASE_SCHEMA)
                if sql: lines.append(sql)

        # Loan_Payment: Status
        old_payments = {p["PaymentID"]: p for p in diff_against.get("payments", [])}
        for p in payments:
            if p["PaymentID"] in old_payments:
                sql = generate_update_sql("Loan_Payment", old_payments[p["PaymentID"]], p, "PaymentID", DATABASE_SCHEMA)
                if sql: lines.append(sql)

        # Loan: Status, Date_Of_Credit_Closing
        old_loans = {l["LoanID"]: l for l in diff_against.get("loans", [])}
        for l in loans:
            if l["LoanID"] in old_loans:
                sql = generate_update_sql("Loan", old_loans[l["LoanID"]], l, "LoanID", DATABASE_SCHEMA)
                if sql: lines.append(sql)

    # --- Zapis do pliku SQL ---
    sql_file = os.path.join(output_dir, f"bankoteka_{snapshot_label}.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


