from pydantic import BaseModel

class Wallet_balance(BaseModel):
    user_id:str
    user_diamond:int
    user_rcoin:int