import jmail_client  as jim


username = input("Username :>")
password = input("Password :>")


jmail = {
    "username" : username,
    "password" : jim.hash_password(password),
    "unread" : [],
    "read" : [],
    "sent" : []
}

if jim.load_json(f'jmail/{username}.json'):
    print("User Already exists!")

else:
    jim.write_json(f'jmail/{username}.json', jmail)
    print(f"Added {username}")