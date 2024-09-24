import json
import datetime
def load(file):
    with open(file+".txt") as d:
        return json.loads(d.read())

def save(name, data):
    with open(name+".txt", "w") as d:
        d.write(json.dumps(data)) # Writes the dictionary to the first line
    print(f"Data {name} has been saved!")

jmail = load("jmail")

user_name = input("enter username")

mail = jmail[user_name]

for sender in mail:
    print(f"JMail from {sender}:")
    for timec in mail[sender]:
        print(f"At {timec}, {sender} sent: \n{mail[sender][timec]}")