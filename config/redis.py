#PRODUCTION
import redis

try:
    client = redis.Redis(host='localhost', port=6379, db=0)
    # If the connection is successful, this code will execute.
    print("Connected to Redis successfully")
except redis.ConnectionError as e:
    # If there's an error connecting to Redis, this code will execute.
    print(f"Error connecting to Redis: {e}")
