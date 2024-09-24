import json
import datetime
import getpass
def load(file):
    with open(file+".txt") as d:
        return json.loads(d.read())

def save(name, data):
    with open(name+".txt", "w") as d:
        d.write(json.dumps(data)) # Writes the dictonary to the first line
    print(f"Data {name} has been saved!")

users = load("userdat")

while True:
    lect = input("? to leave Enter User name :>")
    if lect == "?":
        break
    else:
        users[lect] = getpass.getpass("Enter password :?")
        save("userdat", users)
        mail = load("jmail")




        sender = "JMailServer"
        message = (f"Hi {lect} welcome Jmail\ni would like to thankyou for using Jmail\nSincerly Peter.\nTo send a message (username)message eg\n(JMailAdmin)Hello there!")
        if not (lect in mail):
            mail[lect] = {}

        mail[lect][f"{sender} At:{str(datetime.datetime.now())}"] = message
        save("jmail", mail)
