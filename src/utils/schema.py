# utils/schema.py

DATABASE_SCHEMA = {
    "Branch": ["BranchID", "Localisation"],
    "Employee": ["EmployeeID", "Name", "Surname", "Role", "BranchID"],
    "Customer": ["Pesel", "Name", "Surname", "Date_Of_Birth", "Phone_Number", "Email", "Address"],
    "Account": ["Account_Number", "Type", "Open_Date", "Balance", "CustomerID"],
    "Transactions": ["TransactionID", "Amount", "Date"],
    "Account_Transaction": ["TransactionID", "Sender_AccountID", "Receiver_AccountID"],
    "Loan": ["LoanID", "Type", "Amount", "Interest_Rate", "Approval_Date", "Final_Repayment_Date", "Date_Of_Credit_Closing", "Status", "CustomerID", "EmployeeID"],
    "Loan_Payment": ["PaymentID", "Amount", "Date", "Status", "Date_of_expected_payment", "LoanID"]
}
