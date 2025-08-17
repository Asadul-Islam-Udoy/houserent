import random
import string

def generate_transaction_id(prefix="TXN"):
    """Generate a dummy unique transaction ID"""
    return f"{prefix}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"

def stripe(data):
    txn_id = generate_transaction_id("NAGAD")
    print(f"Nagad payment processed: {txn_id} for amount {amount}")
    return txn_id