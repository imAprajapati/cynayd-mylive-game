#PRODUCTION SERVER

from models.m_teen_patti  import Fruit, Seat
from fastapi import APIRouter, HTTPException
from config.redis import client
from config.db import db
from bson import ObjectId
import secrets
import datetime
import random
from pymongo import ReturnDocument
from pydantic import BaseModel,json
import json as js
from utils.teen_patti_boat import teen_patti_boat
json.ENCODERS_BY_TYPE[ObjectId]=str
router = APIRouter()
table_collection = db['teen_pattis']
table_balance_collection = db["user_wallet_balances"]
transaction_collection = db["transactions"]
from controllers.credit_diamonds import credit_diamonds_teen_patti
class UpdateSeatAmountRequest(BaseModel):
    user_id: str
    amount: int
    seat: str

class UpdateSeatAmountRequest(BaseModel):
    user_id: str
    amount: float
    seat: str


async def check_active_game_and_end():
    try:
        docs = table_collection.find({"game_status": "active"})
        for doc in docs:
            isExist = client.get(f"{doc['_id']}")
            if isExist is None:
                try:
                    print(doc['_id'])
                    await winner_announced(doc['_id'])

                except Exception as error:
                    print(error)
            elif isExist is not None and doc["game_last_count"] <= 0:
                try:
                    await winner_announced(doc['_id'])
                    print("hello")
                except Exception as error:
                    print(error)

    except Exception as err:
        print(err.message)


# @router.get("/new")
# async def create():
#     return {
#         "success": False,
#         "msg": "Under development"
#     }

@router.get("/new")
async def create():
    try:
        teen_patti_game =  client.get("teenPatti_game")
        if teen_patti_game is None:
            game_id = secrets.token_hex(8)
            fruit=Fruit(game_id=game_id,seat=Seat())
            fruit_dict = fruit.dict()
            doc_id=table_collection.insert_one(fruit_dict).inserted_id
            doc=table_collection.find_one({"_id":ObjectId(doc_id)})
            client.setex(str(doc_id), 33, str(doc)),
            client.setex("teenPatti_game", 28, str(doc)),
            await check_active_game_and_end()
            return {
                "success": True,
                "msg": "Game created",
                "data": doc
            }
        else:
            ttl =  client.ttl("teenPatti_game")
            if ttl >= 10:
                await check_active_game_and_end()
                docs = table_collection.find_one({"game_status": "active"}, {"game_last_count": 1})
                return {
                    "success": True,
                    "msg": "Game already created",
                    "data": docs
                }
            else:
                await check_active_game_and_end()
                return {
                    "success": False,
                    "msg": "Game already created but time is less than 15 sec",
                    "wait_time": ttl
                }
    except Exception as err:
        return {
            "success": False,
            "msg": err.message
        }



def randomGenrate(result):
    portUpdate = client.get("teenPatti_portUpdate")
    portUpdate=js.loads(portUpdate)
    port = [100,1000,1000,10000]
    portRndm1 = random.randint(1,3)
    portRndm2 = random.randint(1,3)
    portRndm3 = random.randint(1,3)
    rndmn = random.randint(1, 3)
    if rndmn == 1:
        # add number on port any one
        rndmn1 = random.randint(1,3)
        if rndmn1 == 1:
            portUpdate['A_total_amount']+=port[portRndm1]
            portUpdate['A_total_amount']+=result['seat']['A_total_amount']
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
            return portUpdate
        elif rndmn1 == 2:
            portUpdate['B_total_amount']+=port[portRndm2]
            portUpdate['B_total_amount']+=result['seat']['B_total_amount']
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
            return portUpdate
        else:
            portUpdate['C_total_amount']+=port[portRndm3]
            portUpdate['C_total_amount']+=result['seat']['C_total_amount']
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
            return portUpdate
    elif rndmn == 2:
        # add number on port two A and B or A and C or 
        rndmn2 = random.randint(1,3)
        if rndmn2 == 1:
            portUpdate['A_total_amount']+=port[portRndm1]
            portUpdate['A_total_amount']+=result['seat']['A_total_amount']
            portUpdate['B_total_amount']+=port[portRndm2]
            portUpdate['B_total_amount']+=result['seat']['B_total_amount']
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
            return portUpdate # add here in port A and B
        elif rndmn2 == 2:
            portUpdate['B_total_amount']+=port[portRndm2]
            portUpdate['B_total_amount']+=result['seat']['B_total_amount']
            portUpdate['C_total_amount']+=port[portRndm3]
            portUpdate['C_total_amount']+=result['seat']['C_total_amount']
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
            return portUpdate # add here in port B and C
        else:
            portUpdate['C_total_amount']+=port[portRndm3]
            portUpdate['C_total_amount']+=result['seat']['C_total_amount']
            portUpdate['A_total_amount']+=port[portRndm1]
            portUpdate['A_total_amount']+=result['seat']['A_total_amount']
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
            return portUpdate # add here in port C and A
    else:
        # add here on every port
        portUpdate['C_total_amount']+=port[portRndm3]
        portUpdate['C_total_amount']+=result['seat']['C_total_amount']
        portUpdate['A_total_amount']+=port[portRndm1]
        portUpdate['A_total_amount']+=result['seat']['A_total_amount']
        portUpdate['B_total_amount']+=port[portRndm2]
        portUpdate['B_total_amount']+=result['seat']['B_total_amount']
        client.set("teenPatti_portUpdate",js.dumps(portUpdate))
        return portUpdate


@router.get('/user-bid/{game_id}/{user_id}')
async def user_bid(game_id: str, user_id: str):
    portUpdate = client.get("teenPatti_portUpdate")
    prev_gameId=client.get("teenPatti_prev_gameId")
    if prev_gameId is None:
        prev_gameId=None
    else:
        prev_gameId=js.loads(prev_gameId)
    if portUpdate is None:
        portUpdate={
            "A_total_amount":0,
            "B_total_amount":0,
            "C_total_amount":0
        }
        client.set("teenPatti_portUpdate",js.dumps(portUpdate))
    try:
        pipeline = [
            {"$match": {"_id": ObjectId(game_id)}},
        ]
        result = list(table_collection.aggregate(pipeline))
        sum_A = sum(item['amount'] for item in result[0]['users'] if item['user_id'] == user_id and item['seat'] == 'A')
        sum_B = sum(item['amount'] for item in result[0]['users'] if item['user_id'] == user_id and item['seat'] == 'B')
        sum_C = sum(item['amount'] for item in result[0]['users'] if item['user_id'] == user_id and item['seat'] == 'C')
        if game_id != prev_gameId:
            # prev_gameId=game_id
            client.set("teenPatti_prev_gameId",js.dumps(game_id))
            portUpdate={
            "A_total_amount":0,
            "B_total_amount":0,
            "C_total_amount":0
            }
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
        finalResult = randomGenrate(result[0])
        return {
            "success": True,
            "msg": "User bid found",
            "data": {
                "sum_A": sum_A,
                "sum_B": sum_B,
                "sum_C": sum_C,
                "A_total_amount": finalResult['A_total_amount'],
                "B_total_amount": finalResult['B_total_amount'],
                "C_total_amount": finalResult['C_total_amount']
            },
        } 
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))   
 




@router.put("/newUpdate/{id}")
async def update_seat_amount(id: str, request: UpdateSeatAmountRequest):
    portUpdate = client.get("teenPatti_portUpdate")
    if portUpdate is None:
        portUpdate={
            "A_total_amount":0,
            "B_total_amount":0,
            "C_total_amount":0
        }
        client.set("teenPatti_portUpdate",js.dumps(portUpdate))
    prev_gameId=client.get("teenPatti_prev_gameId")
    if prev_gameId is None:
        prev_gameId=None
    else:
        prev_gameId=js.loads(prev_gameId)
    user_id = request.user_id
    amount = request.amount
    seat = request.seat
    if not user_id or not amount or not seat:
        return{
            "success":False,
            "msg":"Invalid data"
        }

    table = table_collection.find_one({"_id": ObjectId(id)})
    if not table:
        # raise HTTPException(status_code=404, detail="No data found")
        return{
            "success":False,
            "msg":"No data found"
        }

    if table["game_status"] == "ended" or table["winnerAnnounced"] == "yes":
        # raise HTTPException(status_code=400, detail="This game has ended, please wait")
        return{
            "success":False,
            "msg":"This game has ended, please wait"
        }

    table_balance = table_balance_collection.find_one({"user_id": user_id})

    if not table_balance:
        # raise HTTPException(status_code=404, detail="No data found")
        return{
            "success":False,
            "msg":"No data found"
        }

    user_diamond = table_balance["user_diamond"]

    if user_diamond < amount:
        # raise HTTPException(status_code=400, detail="Insufficient balance")
        return{
            "success":False,
            "msg":"Insufficient balance"
        }

    update_obj = {"$push": {"users": {"user_id": user_id, "seat": seat, "amount": amount}}}

    if seat == "A":
        update_obj["$inc"] = {"seat.A_total_amount": amount}
    elif seat == "B":
        update_obj["$inc"] = {"seat.B_total_amount": amount}
    elif seat == "C":
        update_obj["$inc"] = {"seat.C_total_amount": amount}

    updated_balance = table_balance_collection.find_one_and_update(
        {"_id": table_balance["_id"]},
        {"$inc": {"user_diamond": -amount}},
        return_document=ReturnDocument.AFTER
    )
    if not updated_balance or int(updated_balance["user_diamond"]) + int(amount) != user_diamond:
        # raise HTTPException(status_code=500, detail="Something went wrong")
        return{
            "success":False,
            "msg":"Something went wrong"
        }

    updated_table = table_collection.find_one_and_update(
        {"_id": ObjectId(id)},
        update_obj,
        return_document=ReturnDocument.AFTER
    )
    if updated_table:
        transaction_id = secrets.token_hex(8)
        transaction_data = {
            "transaction_id": transaction_id,
            "transaction_type": "debited",
            "transaction_amount": amount,
            "transaction_status": "success",
            "transaction_date": datetime.datetime.now(),
            "sender_type": "user",
            "receiver_type": "game",
            "sender_id": user_id,
            "before_tran_balance": user_diamond,
            "after_tran_balance": updated_balance["user_diamond"],
            "receiver_id": id,
            "user_wallet_type_from": "diamonds",
            "user_wallet_type_to": "diamonds",
            "entity_type": {
                "type": "game",
                "game_id": id,
                "game_name": "teenpatti"
            }
        }
        transaction_collection.insert_one(transaction_data)
        # result = list(table_collection.aggregate(pipeline))
        sum_A = sum(item['amount'] for item in updated_table['users'] if item['user_id'] == user_id and item['seat'] == 'A')
        sum_B = sum(item['amount'] for item in updated_table['users'] if item['user_id'] == user_id and item['seat'] == 'B')
        sum_C = sum(item['amount'] for item in updated_table['users'] if item['user_id'] == user_id and item['seat'] == 'C')
        if id != prev_gameId:
            client.set("teenPatti_prev_gameId",js.dumps(id))
            # prev_gameId=updated_table["_id"]
            portUpdate={
            "A_total_amount":0,
            "B_total_amount":0,
            "C_total_amount":0
            }
            client.set("teenPatti_portUpdate",js.dumps(portUpdate))
        finalResult = randomGenrate(updated_table)
        return {
            "success": True,
            "msg": "Amount added successfully",
            "data":{
                "sum_A": sum_A,
                "sum_B": sum_B,
                "sum_C": sum_C,
                "A_total_amount": finalResult['A_total_amount'],
                "B_total_amount": finalResult['B_total_amount'],
                "C_total_amount": finalResult['C_total_amount']
            },
        }
    else:
        credit_balance = table_balance_collection.find_one_and_update(
            {"_id": table_balance["_id"]},
            {"$inc": {"user_diamond": amount}},
            return_document=ReturnDocument.AFTER
        )
        if not credit_balance or int(credit_balance["user_diamond"]) - int(amount) != user_diamond:
            # raise HTTPException(status_code=500, detail="Something went wrong")
            return{
                "success":False,
                "msg":"Something went wrong"
            }
        # raise HTTPException(status_code=500, detail="Something went wrong")
        return{
            "success":False,
            "msg":"Something went wrong"
        }


@router.get("/winner-announcement/{id}")
async def winner_announced(id: str):
    try:
        doc=table_collection.find_one({'_id': ObjectId(id)})
        if doc is None:
            raise HTTPException(status_code=404, detail="No data found")
        if doc["game_status"] == "ended" or doc["winnerAnnounced"] == "yes":
            return {
                "success": True,
                "msg": "Winner already declared",
                "data":doc["winnedSeat"],
                "WiningAmount":doc["WiningAmount"],
                "TopUserWinner":doc["TopUserWinner"],
                "winnerSeat":doc["winnedSeat"]
            }
        if doc["game_status"] == "active":
            if len(doc["users"]) == 0:
                luck = ['A', 'B', 'C']
                winner = random.choice(luck)
                return teen_patti_boat(winner,id)
            else:
                if client.exists("teenPattiRC"):
                    winnerUsers=[]
                    exist_rc= client.get("teenPattiRC")
                    counter=client.get("teenPattiCounter")
                    total_bidding = int(doc['seat']['A_total_amount'] )+ int(doc['seat']['B_total_amount']) + int(doc['seat']['C_total_amount'])
                    A_winning = total_bidding - int(doc['seat']['A_total_amount']) * 3
                    B_winning = total_bidding - int(doc['seat']['B_total_amount']) * 3
                    C_winning = total_bidding - int(doc['seat']['C_total_amount']) * 3
                    rc_on_port_a = int(A_winning) + int(exist_rc)
                    rc_on_port_b = int(B_winning) + int(exist_rc)
                    rc_on_port_c = int(C_winning) + int(exist_rc)
                    newRC=0
                    counter=int(counter)
                    exist_rc=int(exist_rc)
                    winner=""
                    if counter>=5000:
                        # when counter greater than 5
                        if exist_rc>0:
                            # when rc greater than 0
                            if rc_on_port_a >= 0 and rc_on_port_b >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_a <= rc_on_port_b and rc_on_port_a <= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                elif rc_on_port_b <= rc_on_port_a and rc_on_port_b <= rc_on_port_c:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_a <= 0 and rc_on_port_b >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_b <= rc_on_port_c:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_b <= 0 and rc_on_port_a >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_a <= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_c <= 0 and rc_on_port_a >= 0 and rc_on_port_b >= 0:
                                if rc_on_port_b <= rc_on_port_a:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_a
                                    winner = "A"
                            elif rc_on_port_a <= 0 and rc_on_port_b <= 0 and rc_on_port_c <= 0:
                                if rc_on_port_a >= rc_on_port_b and rc_on_port_a >= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                elif rc_on_port_b >= rc_on_port_c and rc_on_port_b >= rc_on_port_a:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            if winner =="":
                                winner = "A"
                                newRC = rc_on_port_a
                            client.incrby("teenPattiGameRev", int(newRC))
                            client.set("teenPattiRC", 0)
                            client.set("teenPattiCounter", 0)
                            for ele in doc["users"]:
                                if ele["seat"]==winner:
                                    winnerUsers.append(ele)
                            if len(winnerUsers)==0:
                                return teen_patti_boat(winner,id)
                            else:
                                return credit_diamonds_teen_patti(winner,winnerUsers,id)

                        else:
                            # when rc less than 0
                            if A_winning >= B_winning and A_winning >= C_winning:
                                winner = "A"
                                newRC = rc_on_port_a
                            elif B_winning >= C_winning and B_winning >= A_winning:
                                winner = "B"
                                newRC = rc_on_port_b
                            else:
                                winner = "C"
                                newRC = rc_on_port_c

                            if winner =="":
                                winner = "A"
                                newRC = rc_on_port_a
                            client.set("teenPattiRC", int(newRC))
                            client.incrby("teenPattiCounter", 1)
                            for ele in doc["users"]:
                                if ele["seat"]==winner:
                                    winnerUsers.append(ele)
                            if len(winnerUsers)==0:
                                return teen_patti_boat(winner,id)
                            else:
                                return credit_diamonds_teen_patti(winner,winnerUsers,id)
                    else:
                        # when counter less than 5
                        if exist_rc==0:
                            #when rc equal to 0
                            luck = ['A', 'B', 'C']
                            winner = random.choice(luck)
                            total_winning = 0
                            total_bidding =int( doc['seat']['A_total_amount']) + int(doc['seat']['B_total_amount']) + int(doc['seat']['C_total_amount'])
                            if winner == 'A':
                                total_winning = int(doc['seat']['A_total_amount']) * 3.0
                            elif winner == 'B':
                                total_winning = int(doc['seat']['B_total_amount']) * 3.0
                            else:
                                total_winning = int(doc['seat']['C_total_amount']) * 3.0
                            rc=total_bidding-total_winning
                            client.set("teenPattiRC",int(rc))
                            client.incrby("teenPattiCounter", 1)
                            winnerUsers=[]
                            for ele in doc["users"]:
                                if ele["seat"]==winner:
                                    winnerUsers.append(ele)
                            if len(winnerUsers)==0:
                                return teen_patti_boat(winner,id)
                            else:
                                return credit_diamonds_teen_patti(winner,winnerUsers,id)
                        elif exist_rc>0:
                            #when rc greater than 0
                            if rc_on_port_a >= 0 and rc_on_port_b >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_a <= rc_on_port_b and rc_on_port_a <= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                elif rc_on_port_b <= rc_on_port_a and rc_on_port_b <= rc_on_port_c:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_a <= 0 and rc_on_port_b >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_b <= rc_on_port_c:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_b <= 0 and rc_on_port_a >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_a <= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_c <= 0 and rc_on_port_a >= 0 and rc_on_port_b >= 0:
                                if rc_on_port_b <= rc_on_port_a:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_a
                                    winner = "A"
                            elif rc_on_port_a <= 0 and rc_on_port_b <= 0 and rc_on_port_c <= 0:
                                if rc_on_port_a >= rc_on_port_b and rc_on_port_a >= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                elif rc_on_port_b >= rc_on_port_c and rc_on_port_b >= rc_on_port_a:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_a <= 0 and rc_on_port_b <= 0 and rc_on_port_c >= 0:
                                newRC = rc_on_port_c
                                winner = "C"
                            elif rc_on_port_a <= 0 and rc_on_port_b >= 0 and rc_on_port_c <= 0:
                                newRC = rc_on_port_b
                                winner = "B"
                            elif rc_on_port_a >= 0 and rc_on_port_b <= 0 and rc_on_port_c <= 0:
                                newRC = rc_on_port_a
                                winner = "A"
                            if winner=="":
                                newRC = rc_on_port_a
                                winner = "A"
                            client.set("teenPattiRC", int(newRC))
                            client.incrby("teenPattiCounter", 1)
                            for ele in doc["users"]:
                                if ele["seat"]==winner:
                                    winnerUsers.append(ele)
                            if len(winnerUsers)==0:
                                return teen_patti_boat(winner,id)
                            else:
                                return credit_diamonds_teen_patti(winner,winnerUsers,id)
                        elif exist_rc<0:
                            #when rc less than 0
                            if rc_on_port_a <= 0 and rc_on_port_b <= 0 and rc_on_port_c <= 0:
                                if rc_on_port_a >= rc_on_port_b and rc_on_port_a >= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                elif rc_on_port_b >= rc_on_port_a and rc_on_port_b >= rc_on_port_c:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_a >= 0 and rc_on_port_b >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_a <= rc_on_port_b and rc_on_port_a <= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                elif rc_on_port_b <= rc_on_port_a and rc_on_port_b <= rc_on_port_c:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    winner = "C"
                            elif rc_on_port_a >= 0 and rc_on_port_b <= 0 and rc_on_port_c <= 0:
                                newRC = rc_on_port_a
                                winner = "A"
                            elif rc_on_port_b >= 0 and rc_on_port_a <= 0 and rc_on_port_c <= 0:
                                newRC = rc_on_port_b
                                winner = "B"
                            elif rc_on_port_c >= 0 and rc_on_port_a <= 0 and rc_on_port_b <= 0:
                                newRC = rc_on_port_c
                                winner = "C"
                            elif rc_on_port_a <= 0 and rc_on_port_b >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_b <= rc_on_port_c:
                                    newRC = rc_on_port_b
                                    winner = "B"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_b <= 0 and rc_on_port_a >= 0 and rc_on_port_c >= 0:
                                if rc_on_port_a <= rc_on_port_c:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                else:
                                    newRC = rc_on_port_c
                                    winner = "C"
                            elif rc_on_port_c <= 0 and rc_on_port_a >= 0 and rc_on_port_b >= 0:
                                if rc_on_port_a <= rc_on_port_b:
                                    newRC = rc_on_port_a
                                    winner = "A"
                                else:
                                    newRC = rc_on_port_b
                                    winner = "B"

                            if winner == "":
                                newRC = rc_on_port_a
                                winner = "A"
                            client.set("teenPattiRC", int(newRC))
                            client.incrby("teenPattiCounter", 1)
                            for ele in doc["users"]:
                                if ele["seat"]==winner:
                                    winnerUsers.append(ele)
                            if len(winnerUsers)==0:
                                return teen_patti_boat(winner,id)
                            else:
                                return credit_diamonds_teen_patti(winner,winnerUsers,id)

                else:
                    luck = ['A', 'B', 'C']
                    winner = random.choice(luck)
                    total_winning = 0
                    total_bidding = int(doc['seat']['A_total_amount'] )+int( doc['seat']['B_total_amount']) + int(doc['seat']['C_total_amount'])
                    if winner == 'A':
                        total_winning = int(doc['seat']['A_total_amount']) * 3
                    elif winner == 'B':
                        total_winning = int(doc['seat']['B_total_amount']) * 3
                    else:
                        total_winning = int(doc['seat']['C_total_amount'] ) * 3
                    rc=total_bidding-total_winning
                    client.set("teenPattiRC",int(rc))
                    client.set("teenPattiCounter", 1)
                    winnerUsers=[]
                    for ele in doc["users"]:
                        if ele["seat"] == winner:
                            winnerUsers.append(ele)
                    if len(winnerUsers)==0:
                        return teen_patti_boat(winner,id)
                    else:
                        return credit_diamonds_teen_patti(winner, winnerUsers, id)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

@router.get("/resulthistory")
async def result_history(): 
    try:
        result = table_collection.find(
        {"game_status": "ended"},
        {"winnedSeat": 1, "_id": 0}
        ).sort([("_id", -1)]).limit(7)
        if result is None:
            return {
                "success":False,
                "msg": "No result found"
                }
        else:
            return {
                "success":True,
                "msg": "Result found",
                "data": list(result)
            }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/delete-empty-documents")
async def delete_empty_documents():
    try:
        table_collection.delete_many({"users": []})
        return {
            "success": True,
            "msg": "Deleted successfully"
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))