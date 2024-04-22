#PRODUCTION
from config.db import db
import datetime
import secrets
from bson import ObjectId
from pymongo import ReturnDocument
table_collection = db['fruits']
table_balance_collection = db["user_wallet_balances"]
transaction_collection = db["transactions"]
table_collection_teen_patti = db['teen_pattis']
table_collection_greedy_game = db['greedies']

from config.firebase_firestore import firestore_db
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_admin import firestore

greedy_wining_ratio = 3.0

# 0:15 = A
# 1:5 = B
# 2:25 = C
# 3:45 = D
# 4:5 = E
# 5:5 = F
# 6:10 = G
# 7:5 = H
# 8:1.25 = I
# 9:4.37 = J

def credit_greedy_diamonds(winner:str,winnerUsers:list,game_id:str):
    winnerRatio = {"A": 15, "B": 5, "C": 25, "D": 45, "E": 5, "F": 5, "G": 10, "H": 5, "I": 1.25, "J": 4.37, "S":5,"P":5}
    WinningAmount = {}
    for ele in winnerUsers:
      user_id = str(ele['user_id'])
      amount = float(ele['amount'])
      if user_id in WinningAmount:
         WinningAmount[user_id]['BetAmount'] += amount
         WinningAmount[user_id]['WinAmount'] += amount * winnerRatio[winner]
      else:
          WinningAmount[user_id] = {
            'BetAmount': amount,
            'WinAmount': amount * winnerRatio[winner]
          }
      user=table_balance_collection.find_one_and_update(
         {"user_id":ele['user_id']},
         {'$inc':{"user_diamond":ele["amount"] * winnerRatio[winner]}},
          return_document=ReturnDocument.AFTER
         )
      if user:
         transaction_id = secrets.token_hex(8)
         transaction_data = {
            "transaction_id": transaction_id,
            "transaction_type": "credited",
            "transaction_amount": ele["amount"] * winnerRatio[winner],
            "transaction_status": "success",
            "transaction_date": datetime.datetime.now(),
            "sender_type": "user",
            "receiver_type": "game",
            "sender_id": ele["user_id"],
            "before_tran_balance": user["user_diamond"]-ele["amount"]*winnerRatio[winner],
            "after_tran_balance": user["user_diamond"],
            "receiver_id": game_id,
            "user_wallet_type_from": "diamonds",
            "user_wallet_type_to": "diamonds",
            "entity_type": {
                "type": "game",
                "game_id": game_id,
                "game_name": "greedy"
            }
          }
         transaction_collection.insert_one(transaction_data)
      else:
          transaction_id = secrets.token_hex(8)
          transaction_data = {
            "transaction_id": transaction_id,
            "transaction_type": "credited",
            "transaction_amount": ele["amount"]*winnerRatio[winner],
            "transaction_status": "failed",
            "transaction_date": datetime.datetime.now(),
            "sender_type": "user",
            "receiver_type": "game",
            "sender_id": ele["user_id"],
            "before_tran_balance": user["user_diamond"]- ele["amount"] * winnerRatio[winner],
            "after_tran_balance": user["user_diamond"],
            "receiver_id": game_id,
            "user_wallet_type_from": "diamonds",
            "user_wallet_type_to": "diamonds",
            "entity_type": {
                "type": "game",
                "game_id": game_id,
                "game_name": "greedy"
            }
            }
          transaction_collection.insert_one(transaction_data)
    TopUserWinner = []
    for user_id, data in WinningAmount.items():
      temp = {user_id: data['WinAmount']}
      TopUserWinner.append(temp)
    TopUserWinner.sort(key=lambda x: list(x.values())[0], reverse=True)
    TopUserWinner = TopUserWinner[:3]
    dataToUpdate={
      "game_status": "ended",
      "winnerAnnounced": "yes",
      "winnedSeat":winner,
      "TopUserWinner": TopUserWinner,
      "WiningAmount": WinningAmount,
      }
    result=table_collection_greedy_game.update_one({'_id': ObjectId(game_id)}, {"$set": dataToUpdate})
    if result.acknowledged:
        return {
            "success": True,
            "msg": "Winner declared",
            "winnerSeat":winner,
            "TopUserWinner":TopUserWinner,
            "WiningAmount":WinningAmount,
            "data":winner
          }
    else:
      return{
        "success": False,
        "msg": "Something went wrong"
        }
# def credit_diamonds(winner:str,winnerUsers:list,game_id:str):
#     WinningAmount = {}
#     for ele in winnerUsers:
#       user_id = str(ele['user_id'])
#       amount = float(ele['amount'])
#       if user_id in WinningAmount:
#          WinningAmount[user_id]['BetAmount'] += amount
#          WinningAmount[user_id]['WinAmount'] += amount * 3.0
#       else:
#           WinningAmount[user_id] = {
#             'BetAmount': amount,
#             'WinAmount': amount * 3.0
#           }
#       user=table_balance_collection.find_one_and_update(
#          {"user_id":ele['user_id']},
#          {'$inc':{"user_diamond":ele["amount"]*3.0}},
#           return_document=ReturnDocument.AFTER
#          )
#       if user:
#          transaction_id = secrets.token_hex(8)
#          transaction_data = {
#             "transaction_id": transaction_id,
#             "transaction_type": "credited",
#             "transaction_amount": ele["amount"]*3.0,
#             "transaction_status": "success",
#             "transaction_date": datetime.datetime.now(),
#             "sender_type": "user",
#             "receiver_type": "game",
#             "sender_id": ele["user_id"],
#             "before_tran_balance": user["user_diamond"]-ele["amount"]*3.0,
#             "after_tran_balance": user["user_diamond"],
#             "receiver_id": game_id,
#             "user_wallet_type_from": "diamonds",
#             "user_wallet_type_to": "diamonds",
#             "entity_type": {
#                 "type": "game",
#                 "game_id": game_id,
#                 "game_name": "fruit"
#             }
#           }
#          transaction_collection.insert_one(transaction_data)
#       else:
           
#           transaction_id = secrets.token_hex(8)
#           transaction_data = {
#             "transaction_id": transaction_id,
#             "transaction_type": "credited",
#             "transaction_amount": ele["amount"]*3.0,
#             "transaction_status": "failed",
#             "transaction_date": datetime.datetime.now(),
#             "sender_type": "user",
#             "receiver_type": "game",
#             "sender_id": ele["user_id"],
#             "before_tran_balance": user["user_diamond"]-ele["amount"]*3.0,
#             "after_tran_balance": user["user_diamond"],
#             "receiver_id": game_id,
#             "user_wallet_type_from": "diamonds",
#             "user_wallet_type_to": "diamonds",
#             "entity_type": {
#                 "type": "game",
#                 "game_id": game_id,
#                 "game_name": "fruit"
#             }
#             }
#           transaction_collection.insert_one(transaction_data)
#     TopUserWinner = []
#     for user_id, data in WinningAmount.items():
#       temp = {user_id: data['WinAmount']}
#       TopUserWinner.append(temp)
#     TopUserWinner.sort(key=lambda x: list(x.values())[0], reverse=True)
#     TopUserWinner = TopUserWinner[:3]
#     dataToUpdate={
#       "game_status": "ended",
#       "winnerAnnounced": "yes",
#       "winnedSeat":winner,
#       "TopUserWinner": TopUserWinner, 
#       "WiningAmount": WinningAmount,
#       }
#     result=table_collection.update_one({'_id': ObjectId(game_id)}, {"$set": dataToUpdate})
#     if result.acknowledged:
#         return {
#             "success": True,
#             "msg": "Winner declared",
#             "winnerSeat":winner,
#             "TopUserWinner":TopUserWinner,
#             "WiningAmount":WinningAmount,
#             "data":winner
#           }
#     else:
#       return{
#         "success": False,
#         "msg": "Something went wrong"
#         }
    

def credit_diamonds(winner:str,winnerUsers:list,game_id:str):
    WinningAmount = {}
    for ele in winnerUsers:
      user_id = str(ele['user_id'])
      amount = float(ele['amount'])
      if user_id in WinningAmount:
         WinningAmount[user_id]['BetAmount'] += amount
         WinningAmount[user_id]['WinAmount'] += amount * 3.0
      else:
          WinningAmount[user_id] = {
            'BetAmount': amount,
            'WinAmount': amount * 3.0
          }
      
      user_ref = firestore_db.collection("users").document(user_id) 
      user = user_ref.update({
        "diamond": firestore.Increment(ele["amount"]*3.0)
      })
      user_doc = user_ref.get()
      table_balance = user_doc.to_dict()
      # print("this is in side the credit",table_balance,winner)
      if user:
         transaction_id = secrets.token_hex(8)
         transaction_data = {
            "transaction_id": transaction_id,
            "transaction_type": "credited",
            "transaction_amount": ele["amount"]*3.0,
            "transaction_status": "success",
            "transaction_date": datetime.datetime.now(),
            "sender_type": "user",
            "receiver_type": "game",
            "sender_id": ele["user_id"],
            "before_tran_balance": table_balance["diamond"]-ele["amount"]*3.0,
            "after_tran_balance": table_balance["diamond"],
            "receiver_id": game_id,
            "user_wallet_type_from": "diamonds",
            "user_wallet_type_to": "diamonds",
            "entity_type": {
                "type": "game",
                "game_id": game_id,
                "game_name": "fruit"
            }
          }
         transaction_collection.insert_one(transaction_data)
      else:
           
          transaction_id = secrets.token_hex(8)
          transaction_data = {
            "transaction_id": transaction_id,
            "transaction_type": "credited",
            "transaction_amount": ele["amount"]*3.0,
            "transaction_status": "failed",
            "transaction_date": datetime.datetime.now(),
            "sender_type": "user",
            "receiver_type": "game",
            "sender_id": ele["user_id"],
            "before_tran_balance": table_balance["diamond"]-ele["amount"]*3.0,
            "after_tran_balance": table_balance["diamond"],
            "receiver_id": game_id,
            "user_wallet_type_from": "diamonds",
            "user_wallet_type_to": "diamonds",
            "entity_type": {
                "type": "game",
                "game_id": game_id,
                "game_name": "fruit"
            }
            }
          transaction_collection.insert_one(transaction_data)
    TopUserWinner = []
    for user_id, data in WinningAmount.items():
      temp = {user_id: data['WinAmount']}
      TopUserWinner.append(temp)
    TopUserWinner.sort(key=lambda x: list(x.values())[0], reverse=True)
    TopUserWinner = TopUserWinner[:3]
    dataToUpdate={
      "game_status": "ended",
      "winnerAnnounced": "yes",
      "winnedSeat":winner,
      "TopUserWinner": TopUserWinner, 
      "WiningAmount": WinningAmount,
      }
    result=table_collection.update_one({'_id': ObjectId(game_id)}, {"$set": dataToUpdate})
    if result.acknowledged:
        return {
            "success": True,
            "msg": "Winner declared",
            "winnerSeat":winner,
            "TopUserWinner":TopUserWinner,
            "WiningAmount":WinningAmount,
            "data":winner
          }
    else:
      return{
        "success": False,
        "msg": "Something went wrong"
        }



def credit_diamonds_teen_patti(winner:str,winnerUsers:list,game_id:str):
    WinningAmount = {}
    for ele in winnerUsers:
      user_id = str(ele['user_id'])
      amount = float(ele['amount'])
      if user_id in WinningAmount:
         WinningAmount[user_id]['BetAmount'] += amount
         WinningAmount[user_id]['WinAmount'] += amount * 3.0
      else:
          WinningAmount[user_id] = {
            'BetAmount': amount,
            'WinAmount': amount * 3.0
          }
      user=table_balance_collection.find_one_and_update(
         {"user_id":ele['user_id']},
         {'$inc':{"user_diamond":ele["amount"]*3.0}},
          return_document=ReturnDocument.AFTER
         )
      if user:
         transaction_id = secrets.token_hex(8)
         transaction_data = {
            "transaction_id": transaction_id,
            "transaction_type": "credited",
            "transaction_amount": ele["amount"]*3.0,
            "transaction_status": "success",
            "transaction_date": datetime.datetime.now(),
            "sender_type": "user",
            "receiver_type": "game",
            "sender_id": ele["user_id"],
            "before_tran_balance": user["user_diamond"]-ele["amount"]*3.0,
            "after_tran_balance": user["user_diamond"],
            "receiver_id": game_id,
            "user_wallet_type_from": "diamonds",
            "user_wallet_type_to": "diamonds",
            "entity_type": {
                "type": "game",
                "game_id": game_id,
                "game_name": "fruit"
            }
          }
         transaction_collection.insert_one(transaction_data)
      else:
           
          transaction_id = secrets.token_hex(8)
          transaction_data = {
            "transaction_id": transaction_id,
            "transaction_type": "credited",
            "transaction_amount": ele["amount"]*3.0,
            "transaction_status": "failed",
            "transaction_date": datetime.datetime.now(),
            "sender_type": "user",
            "receiver_type": "game",
            "sender_id": ele["user_id"],
            "before_tran_balance": user["user_diamond"]-ele["amount"]*3.0,
            "after_tran_balance": user["user_diamond"],
            "receiver_id": game_id,
            "user_wallet_type_from": "diamonds",
            "user_wallet_type_to": "diamonds",
            "entity_type": {
                "type": "game",
                "game_id": game_id,
                "game_name": "fruit"
            }
            }
          transaction_collection.insert_one(transaction_data)
    TopUserWinner = []
    for user_id, data in WinningAmount.items():
      temp = {user_id: data['WinAmount']}
      TopUserWinner.append(temp)
    TopUserWinner.sort(key=lambda x: list(x.values())[0], reverse=True)
    TopUserWinner = TopUserWinner[:3]
    dataToUpdate={
      "game_status": "ended",
      "winnerAnnounced": "yes",
      "winnedSeat":winner,
      "TopUserWinner": TopUserWinner, 
      "WiningAmount": WinningAmount,
      }
    result=table_collection_teen_patti.update_one({'_id': ObjectId(game_id)}, {"$set": dataToUpdate})
    if result.acknowledged:
        return {
            "success": True,
            "msg": "Winner declared",
            "winnerSeat":winner,
            "TopUserWinner":TopUserWinner,
            "WiningAmount":WinningAmount,
            "data":winner
          }
    else:
      return{
        "success": False,
        "msg": "Something went wrong"
        }

