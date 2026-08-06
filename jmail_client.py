import hashlib
import json

DOMAIN = "127.0.0.1" #Enter domain or ip

def hash_password(string: str) -> str:
    """Simple SHA-256 hash (use bcrypt/argon2 in production)."""
    return hashlib.sha256(string.encode()).hexdigest()

def load_json(file:str):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return False
    
def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

def logon(username, password):
    json = load_json(f"/jmail/{username}")
    if not json:
        return False
    
    if json["password"] ==  hash_password(password):
        return True
    
    else:
        return False


def jmail_client(client):
    client.print("Server Started Correctly")
    client.print(f"Logon (Contact sysadmin for acount)")
    username = client.input("Username :>")
    password = client.hidden_input("Password :>")

    if not logon(username, password):
        client.print("Details incorrect")