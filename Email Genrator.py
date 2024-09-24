import json
import datetime
def load(file):
    with open(file+".txt") as d:
        return json.loads(d.read())

def save(name, data):
    with open(name+".txt", "w") as d:
        d.write(json.dumps(data)) # Writes the dictionary to the first line
    print(f"Data {name} has been saved!")

mail = load("jmail")

while True:
    username = input("? to leave user:>")
    if username == "?":
        break
    else:
        sender = input("Sender (Doesn't need to be real):>")
        message = input("Message :>").replace('\\n', '\n')
        if not(username in mail):
            mail[username] = {}


        mail[username][f"{sender} At:{str(datetime.datetime.now())}"] = message
        save("jmail", mail)