#PRODUCTION
from pydantic import BaseModel
import datetime
class Seat(BaseModel):
    A_total_amount: int=0
    B_total_amount: int=0
    C_total_amount: int=0




class Fruit(BaseModel):
    game_id: str
    seat: Seat
    game_last_count: int = 20
    users: list = []
    game_status: str = "active"
    winnerAnnounced: str = "no"
    winnedSeat: str = None
    WiningAmount: dict = {}
    TopUserWinner: list = []
    created_at: str = datetime.datetime.now()