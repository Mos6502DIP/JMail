import socket
import json
import os
import getpass

version = "1.0"
print(f"You are running JMail v{version}")
ip = input("custom server ip leave blank for default:")
if ip == "":
    ip = socket.gethostbyname("jmail.serverpit.com")
elif ip == "@":
        ip = "127.0.0.1"
port = 90
cSct = socket.socket()  # creating the socket
print("Connecting")
cSct.connect((ip, port))# connecting to the server
print(cSct.recv(1024).decode())
print("Now checking Version!")
cSct.send(bytes(version, "utf-8"))
if cSct.recv(1024).decode() == "badver":
    print("Now Updating")
    exit()
else:
    print("Client Version Is Compatible!")
cSct.send(bytes(input("UserName:>"), "utf-8"))
cSct.send(bytes(getpass.getpass("Password:>"), "utf-8"))
if cSct.recv(1024).decode() == "1969":
    print("You have entered the matrix!")
    while True:
        mail = json.loads(cSct.recv(1024).decode())
        os.system("cls")

        for sender in mail:
            print("")
            print(f"""{sender}
{mail[sender]}""")
            print("")
        while True:
            message = input("Message:> ")
            if len(message) == 300:
                print("Message too long")
            elif message == "":
                cSct.send(bytes("Banky", "utf-8"))
                break
            else:
                cSct.send(bytes(message, "utf-8"))
                break
else:
    print(cSct.recv(1024).decode())


