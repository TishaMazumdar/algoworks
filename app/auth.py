import os
import json
import hashlib

USERS_FILE = "src/models/users.json"
SESSION_FILE = "src/models/session.json"
DATA_DIR = "data"

# Ensure users and session files exist
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "w") as f:
        json.dump({"current_user": None}, f)

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

    with open(SESSION_FILE, "w") as f:
        json.dump({"current_user": username}, f)

    return "Login successful."

def logout() -> str:
    with open(SESSION_FILE, "w") as f:
        json.dump({"current_user": None}, f)
    return "Logged out."

def get_current_user() -> str:
    with open(SESSION_FILE) as f:
        session = json.load(f)
    return session.get("current_user", None)