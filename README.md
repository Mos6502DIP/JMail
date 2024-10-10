# Jmail Server v1.0

Jmail is a simple socket-based mail server that allows clients to send and receive messages between users. The server handles multiple client connections and stores the messages persistently using JSON files.

## Features

- **Socket-Based Server**: Listens for client connections and facilitates communication over a specified port.
- **User Authentication**: Clients must provide a username and password to log in.
- **Messaging System**: Allows users to send and receive messages, which are stored on the server.
- **Multi-threaded**: The server can handle multiple clients simultaneously using threading.
- **Persistent Storage**: User information and messages are stored in JSON files.

## File Structure

- **userdat.txt**: Stores user login information (usernames and passwords).
- **jmail.txt**: Stores messages sent between users.

## How It Works

1. **Server Setup**:
   - The server opens a socket and listens for incoming connections on a specified port.
   - It supports up to 100 simultaneous connections using threading.
   
2. **Client Connection**:
   - Once connected, the client sends its version number for compatibility checks.
   - If the client version is compatible with the server, it proceeds to the login process.
   
3. **Login Process**:
   - Clients must provide a username and password, which are verified against the `userdat.txt` file.
   - If the credentials are incorrect or the user does not exist, the client receives a login failure message.
   - On successful login, the user can access their mailbox and send messages.

4. **Messaging**:
   - Users can refresh their inbox to view new messages.
   - They can send a message to another user by typing the recipient's username and the message. Messages are stored in `jmail.txt`.
   
5. **Error Handling**:
   - The server can handle crashes and displays an error message when it fails.
   
## How to Use

1. **Running the Server**:
   - Ensure Python 3.x is installed.
   - Run the server using the following command:
     ```bash
     python jmail_server.py
     ```
   - You will be prompted to enter a custom port number (e.g., 90).

2. **Connecting a Client**:
   - The client sends its version number and logs in using their username and password.
   - Once authenticated, they can send and receive messages.

3. **Sending a Message**:
   - To send a message, the user should input the recipient’s username followed by the message in the following format:
     ```plaintext
     (username) message
     ```
   - The server will store the message and send it to the recipient when they refresh their inbox.

