from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
#   client = MongoClient('mongodb://mylive:cynayd123@docdb-2023-09-04-17-01-36.c64xlhozadrj.ap-south-1.docdb.amazonaws.com:27017/mylive?tls=true&tlsCAFile=/home/ec2-user/global-bundle.pem&retryWrites=false',maxPoolSize=150)
    client = MongoClient('mongodb://localhost:27017/myLive')
    # client = MongoClient('mongodb+srv://mylive:cynayd123@mylive.z3zbduk.mongodb.net/myLive?authSource=admin')
    db = client['myLive']
    # If the connection is successful, this code will execute.
    print("Connected to MongoDB successfully")
except ConnectionFailure as e:
    # If there's an error connecting to MongoDB, this code will execute.
    print(f"Error connecting to MongoDB: {e}")
