import socket
import json
import datetime
import threading

s_ver = "1.0 "
def load(file):
    with open(file+".txt") as d:
        return json.loads(d.read())

def save(name, data):
    with open(name+".txt", "w") as d:
        d.write(json.dumps(data)) # Writes the dictonary to the first line
    print(f"Data {name} has been saved!")

def substring(string):
    start = string.index('(')
    end = string.index(')',start+1)
    return(string[start+1:end])

def message(string):
    start = string.index(')') + 1
    return (string[start:])

def newclient(client,addr):
    user_name = f"user{addr}"
    users_info = load("userdat")
    client.send(bytes('You have connected to Jmail.', 'utf-8'))
    c_version = client.recv(1024).decode()
    if float(c_version) >= float(s_ver):
        client.send(bytes("good boi UWU","utf-8"))
    else:
        client.send(bytes("badver", "utf-8"))
    user_name_t = client.recv(1024).decode()
    password = client.recv(1024).decode()
    if not(user_name_t in users_info):
        client.send(bytes(f'1234', 'utf-8'))
        client.send(bytes(f'Logon failed', 'utf-8'))
    elif users_info[user_name_t] == password:
        client.send(bytes(f'1969', 'utf-8'))
        user_name = user_name_t
        print(f"Has {user_name} connected as {addr}")
        while True:
            jmail = load("jmail")
            client.send(bytes(json.dumps(jmail[user_name]), 'utf-8'))
            useri = client.recv(1024).decode()
            if  useri == "Banky":
                print(f"{username} has refreshed!")
            elif useri[0] == "(":
                username = substring(useri)

                jmail = load("jmail")
                if not (username in jmail):
                    jmail[username] = {}


                jmail[username][f"{user_name} At:{str(datetime.datetime.now())}"] = message(useri).replace('\\n', '\n')
                save("jmail", jmail)



    else:
        client.send(bytes(f'1234', 'utf-8'))
        client.send(bytes(f'Logon failed', 'utf-8'))
    print(f"Has {user_name} disconnected!")





Sct=socket.socket()
port = int(input("Custom port number. 90 for default:> "))
Sct.bind(("", port))
Sct.listen(100)
print('Started server.')

while True:
    try:
        print("Ready for next connection!")
        client,add=Sct.accept()
        current_time = datetime.datetime.now()
        if add[0] == "172.18.0.2":
            print("Server Status Checked")
        else:
            print(add , "has connected to server" ,current_time)
            threading._start_new_thread(newclient,(client,add))

    except:
        print("Server did a crashy washy UWU!")
Sct.close()