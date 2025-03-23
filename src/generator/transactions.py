from utils.counters import transaction_ctr

def generate_initial_transactions(accounts):
    global transaction_ctr
    transactions = []
    account_transaction_links = []

    transaction_id = transaction_ctr+1

    for account in accounts:
        tx = {
            "TransactionID": transaction_id,
            "Amount": account["Balance"],
            "Date": account["Open_Date"]
        }
        transactions.append(tx)

        link = {
            "TransactionID": transaction_id,
            "Sender_AccountID": 100000,
            "Receiver_AccountID": account["Account_Number"]
        }
        account_transaction_links.append(link)

        transaction_ctr += 1
        transaction_id +=1

    return transactions, account_transaction_links
