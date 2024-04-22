#PRODUCTION
from fastapi import FastAPI,BackgroundTasks
from routers.r_fruit import router as fruit_router
from routers.r_teen_patti import router as teen_patti_router
from routers.r_new_fruit import router as new_router
from routers.r_greedy import router as greedy_router
from fastapi.exceptions import HTTPException
from config.db import db
import config.firebase_firestore as ffs
from config.firebase_firestore import firestore_db
import asyncio
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(debug=True)
app.include_router(new_router,prefix='/api/new-fruit')
app.include_router(fruit_router,prefix="/api/fruit-game")
app.include_router(teen_patti_router,prefix="/api/teen-pati")
app.include_router(greedy_router,prefix="/api/greedy-game")
table_collection = db["fruits"]
table_teen_patti_collection = db["teen_pattis"]
table_greedy_collection = db["greedies"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your frontend's actual origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from google.cloud.firestore_v1.base_query import FieldFilter
@app.get("/users/{user_id}")
async def find_user_by_id(user_id: str):
    try:
        # Reference the document by user ID
        user_ref = firestore_db.collection("users").document(user_id)
        
        # Get the document data
        user_doc = user_ref.get()
        
        # Check if the document exists
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")

        # Return the user data
        return user_doc.to_dict()
    except Exception as e:
        # Handle any errors
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/")
async def root():
    try:
        # Query users collection and retrieve all documents
        users_docs = firestore_db.collection("users").where(filter=FieldFilter("name", "==", "aditya")).where(filter=FieldFilter("email","==","aditya@gmail.com")).stream()
        # Iterate over documents and print user data
        for doc in users_docs:
            user_data = doc.to_dict()
            print(f"User ID: {doc.id}, Data: {user_data}")

        return {"message": "Hello World"}
    except Exception as e:
        # Handle any errors
        return {"error": str(e)}



@app.get('/insert')
async def insert():
    # Insert a new document to the users collection
    user_data = {
        "name": "nothing",
        "diamond":0
    }
    users_ref = ffs.firestore_db.collection("users")
    _, user_id = users_ref.add(user_data) 

    print(f"User added with ID: {user_id.id}")
    return {"message": "Data inserted successfully"}
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None

# Endpoint to update a user by ID
@app.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    try:
        # Reference the document to be updated
        user_ref = ffs.firestore_db.collection("users").document(user_id)

        # Check if the document exists
        if not user_ref.get().exists:
            raise HTTPException(status_code=404, detail="User not found")

        # Get the existing user data
        existing_user_data = user_ref.get().to_dict()

        # Update the user data with the provided values
        updated_user_data = {key: value for key, value in user_update.dict().items() if value is not None}

        # Update the document in Firestore
        user_ref.update(updated_user_data)

        # Return success message
        return {"message": f"User with ID {user_id} updated successfully"}
    except Exception as e:
        # Handle any errors
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/delete-users/{user_id}")
async def delete_user(user_id: str):
    try:
        # Reference the document to be deleted
        user_ref = ffs.firestore_db.collection("users").document(user_id)
        
        # Check if the document exists
        if not user_ref.get().exists:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete the document
        user_ref.delete()

        # Return success message
        return {"message": f"User with ID {user_id} deleted successfully"}
    except Exception as e:
        # Handle any errors
        raise HTTPException(status_code=500, detail=str(e))
# This is schedular for greedy game

async def task_to_schedule_for_greedy():
    while True:
        data = table_greedy_collection.find_one({"game_status": "active"})
        if data:
            count= data["game_last_count"]
            if count>0:
                table_greedy_collection.find_one_and_update({"game_status": "active"},{'$inc': {'game_last_count': -1}})
        # print("this is task")
        await asyncio.sleep(1)


# This is schedular for fruit game

async def task_to_schedule():
    while True:
        data = table_collection.find_one({"game_status": "active"})
        if data:
            count= data["game_last_count"]
            if count>0:
                table_collection.find_one_and_update({"game_status": "active"},{'$inc': {'game_last_count': -1}})
        # print("this is task")
        await asyncio.sleep(1) 


# This is schedular for teen patti

async def another_task_to_schedule():
    while True:
        data = table_teen_patti_collection.find_one({"game_status": "active"})
        if data:
            count= data["game_last_count"]
            if count>0:
                table_teen_patti_collection.find_one_and_update({"game_status": "active"},{'$inc': {'game_last_count': -1}})
        await asyncio.sleep(1.5) 


def run_scheduled_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_to_schedule)
    background_tasks.add_task(another_task_to_schedule)
    background_tasks.add_task(task_to_schedule_for_greedy)


@app.on_event("startup")
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(run_scheduled_task, background_tasks)
    asyncio.create_task(task_to_schedule())  # Start the task in the background
    asyncio.create_task(another_task_to_schedule())
    asyncio.create_task(task_to_schedule_for_greedy())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
