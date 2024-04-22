#PRODUCTION
import random
from config.db import db
table_collection = db['teen_pattis']
from bson import ObjectId
from pymongo import ReturnDocument
def teen_patti_boat(winner:str,game_id:str):
    random_user_id = random.randint(555555, 666666)
    random_amount = random.randrange(1000, 10001, 1000)  # generates a random multiple of 1000 between 1000 and 10000
    random_amount = random_amount if random_amount != 10000 else 100000  # replaces 10000 with 100000
    TopUserWinner={f'{random_user_id}':random_amount*3.0}
    WiningAmount={f'{random_user_id}':{"WinAmount":random_amount*3.0},"BetAmount":f'{random_amount}'}
    dataToUpdate={
        "game_status": "ended",
        "winnerAnnounced": "yes",
        "winnedSeat":winner,
        "TopUserWinner": TopUserWinner,
        "WiningAmount": WiningAmount,
        }
    result=table_collection.update_one({'_id': ObjectId(game_id)}, {"$set": dataToUpdate})
    if result.acknowledged:
        return {
            "success": True,
            "msg": "Winner declared",
            "winnerSeat":winner,
            "TopUserWinner":TopUserWinner,
            "WiningAmount":WiningAmount,
            "data":winner
        }
    else:
        return{
            "success": False,
            "msg": "Something went wrong"
        }