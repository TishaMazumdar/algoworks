import os
import json
import hashlib

USERS_FILE = "src/models/users.json"
DATA_DIR = "data"

# Ensure users file and user folders exist
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username: str, password: str) -> str:
    with open(USERS_FILE) as f:
        users = json.load(f)

    if username in users:
        return "Username already exists."

    users[username] = hash_password(password)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    os.makedirs(os.path.join(DATA_DIR, username), exist_ok=True)
    return "Signup successful."

def login(username: str, password: str) -> str:
    with open(USERS_FILE) as f:
        users = json.load(f)

    if username not in users or users[username] != hash_password(password):
        return "Invalid username or password."

    return "Login successful."

def logout() -> str:
    return "Logged out."