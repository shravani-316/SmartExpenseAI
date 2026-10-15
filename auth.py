import json, hashlib, secrets
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"

def _read():
    DATA_DIR.mkdir(exist_ok=True)
    if not USERS_FILE.exists(): USERS_FILE.write_text("{}", encoding="utf-8")
    try: return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except Exception: return {}

def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 180000).hex()

def init_auth():
    _read()

def register_user(name, email, password):
    name, email = name.strip(), email.strip().lower()
    if not name: return False, "Please enter your name."
    if not email or "@" not in email or "." not in email.split("@")[-1]: return False, "Please enter a valid email address."
    if len(password) < 8: return False, "Password must contain at least 8 characters."
    users = _read()
    if email in users: return False, "An account with this email already exists."
    salt = secrets.token_hex(16)
    users[email] = {"name": name, "salt": salt, "password_hash": _hash(password, salt), "created_at": __import__("datetime").datetime.now().isoformat()}
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")
    return True, "Account created."

def login_user(email, password):
    users = _read()
    record = users.get(email.strip().lower())
    if not record: return False, "Email or password is incorrect."
    if not secrets.compare_digest(record["password_hash"], _hash(password, record["salt"])):
        return False, "Email or password is incorrect."
    return True, "Signed in."

def current_user(email):
    return _read().get(email.strip().lower())

def logout_user():
    import streamlit as st
    st.session_state.pop("user_email", None)
