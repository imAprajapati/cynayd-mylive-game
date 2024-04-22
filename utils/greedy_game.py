import random
from config.db import db
table_collection = db['greedies']
from bson import ObjectId
from pymongo import ReturnDocument
def greedy_game_boat(winner:str,game_id:str):
    random_user_id = random.randint(555555, 666666)
    random_amount = random.randrange(1, 21, 10)  # generates a random multiple of 1000 between 1000 and 10000
    random_amount = random_amount if random_amount != 10000 else 100000  # replaces 10000 with 100000
    TopUserWinner={f'{random_user_id}':random_amount*5.0}
    WiningAmount={f'{random_user_id}':{"WinAmount":random_amount*5.0},"BetAmount":f'{random_amount}'}
    dataToUpdate={
        "game_status": "ended",
        "winnerAnnounced": "yes",
        "winnedSeat":winner,
        "TopUserWinner": [TopUserWinner],
        "WiningAmount": WiningAmount,
        }
    result=table_collection.update_one({'_id': ObjectId(game_id)}, {"$set": dataToUpdate})
    if result.acknowledged:
        return {
            "success": True,
            "msg": "Winner declared",
            "winnerSeat":winner,
            "TopUserWinner":[TopUserWinner],
            "WiningAmount":WiningAmount,
            "data":winner
        }
    else:
        return{
            "success": False,
            "msg": "Something went wrong"
        }