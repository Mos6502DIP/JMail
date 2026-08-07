import hashlib
import json
import shlex

DOMAIN = "127.0.0.1" #Enter domain or ip

def hash_password(string: str) -> str:
    """Simple SHA-256 hash (use bcrypt/argon2 in production)."""
    return hashlib.sha256(string.encode()).hexdigest()

def load_json(file:str):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        return False

def load_tdoc(file_name):
    with open(file_name, "r") as fp:
        lines = fp.readlines()
        doc = []
        page = []
        for line in lines:
            
            if line.strip() == "#":
                doc.append(page)
                page = []
            else:
                page.append(line.strip())
        doc.append(page)
        return doc

def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

def logon(username, password):
    json = load_json(f"jmail/{username}.json")
    if not json:
        return False
    
    if json["password"] ==  hash_password(password):
        return True
    
    else:
        return False

def send_jmail(username, recipient, subject, tdoc):
    
    jmail = {
        "datetime" :
        "sender" : f"{username}:{DOMAIN}",
        "receiver" : recipient,
        "subject" : subject,
        "tdoc" : tdoc
    }

def jmail_client(client):
    client.print("Server Started Correctly")
    client.print(f"Logon (Contact sysadmin for acount) DOMAIN:{DOMAIN}")
    client.print(f"IF you did not connect via this domain disconnect.")
    username = client.input("Username :>")
    password = client.hidden_input("Password :>")

    if not logon(username, password):
        client.print("Details incorrect")

    while True:
        jmails = load_json(f'jmail/{username}.json')
        for jmail in jmails["unread"]:
            client.print(f"({jmails["unread"].index(jmail)}) [{jmail["datetime"]}] From : {jmail["sender"]} Subject : {jmail["subject"]}")

        command = client.input(":>")
        load_jdoc
        send_jmail(username, "fractal:127.0.0.1", "Extract from the book you asked for!", tdoc)
        
        