from pydantic import BaseModel
from typing import List

class Transaction(BaseModel):
    transaction_id: str
    transaction_type: str
    transaction_amount: float
    transaction_status: str
    transaction_date: str
    sender_type: str
    receiver_type: str
    sender_id: str
    receiver_id: str
    before_tran_balance: float
    after_tran_balance: float
    user_wallet_type_from: str
    user_wallet_type_to: str
    entity_type: dict
    last_update: str

class CreateTransactionRequest(BaseModel):
    transactions: List[Transaction]
