from pydantic import BaseModel
import datetime
class Seat(BaseModel):
    A_total_amount: int=0
    B_total_amount: int=0
    C_total_amount: int=0
    D_total_amount: int=0
    E_total_amount: int=0
    F_total_amount: int=0
    G_total_amount: int=0
    H_total_amount: int=0
    I_total_amount: int=0
    J_total_amount: int=0

class Greedy(BaseModel):
    seat: Seat
    game_last_count: int = 15
    users = []
    game_status: str = "active"
    winnerAnnounced: str = "no"
    winnedSeat: str = None
    WiningAmount: dict = {}
    TopUserWinner = []
    created_at: str = datetime.datetime.now()