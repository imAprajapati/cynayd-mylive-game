import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate(r"D:\CYNYAD\CynaydMyLive\MyLiveGame\cynayd-mylive.json")
firebase_admin.initialize_app(cred)
print("Connected to Firebase successfully.")

# Get Firestore client
firestore_db = firestore.client()
print("Firestore database client initialized.")