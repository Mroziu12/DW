from faker import Faker
import random

fake = Faker("pl_PL")

def generate_branches(n=3):
    branches = []
    for i in range(1, n + 1):
        branch = {
            "BranchID": i,
            "Localisation": fake.city()
        }
        branches.append(branch)
    return branches

def generate_employees(branches, min_employees_per_branch=2, max_employees_per_branch=5):
    roles = ["Clerk", "Loan Advisor", "Manager", "Customer Service", "Teller"]
    employees = []
    emp_id = 1

    for branch in branches:
        num_employees = random.randint(min_employees_per_branch, max_employees_per_branch)
        for _ in range(num_employees):
            employee = {
                "EmployeeID": emp_id,
                "Name": fake.first_name(),
                "Surname": fake.last_name(),
                "Role": random.choice(roles),
                "BranchID": branch["BranchID"]
            }
            employees.append(employee)
            emp_id += 1

    return employees
