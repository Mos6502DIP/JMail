import socket
import threading
import json
import time
import datetime

active_terminal_clients = set()
active_terminal_clients_lock = threading.Lock()

start_time = None



def load_json(file):
    global settings
    with open(file, "r") as f:
        return json.load(f)    


def setup(port):
    global settings
    Sct = socket.socket()  # creating the socket
    
    Sct.bind(("", int(port)))  # Bind port
    Sct.listen(5)  # listens for clients
    print(f'Telepy server started on port:{port}')
    return Sct

def start_uptime():
    global start_time
    start_time = time.time()

def get_uptime():
    global start_time
    if start_time is None:
        return "Uptime not started."
    elapsed_time = time.time() - start_time
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


        

def handle_client_connection_wrapper(client_side, client):
    try:
        print(f"Handling client {client.client_ip}")
        client.client.settimeout(60)
        client_side(client)

    finally:
        
        with active_terminal_clients_lock:
            active_terminal_clients.discard(threading.current_thread())
        print(f"Client {client.client_ip} disconnected. {len(active_terminal_clients)} terminal clients online.")
        client.client.close()


def handle_ping_connection_wrapper(client_socket):
    try:
        client_socket.send(bytes("pong", "utf-8"))

    finally:

        client_socket.close()


def start_jmail(port):

    # Socket setup
    
    sct = setup(port)
    
   
        
    
    # Main server script
    while True:
        try:
            time.sleep(0.001)
            print('Waiting for J-Mail')
            client_socket, client_address = sct.accept()
            print(f"Connection from {client_address}")
            client_socket.settimeout(5)

            try:
                # Receive connection type (like 'terminal') from the client
                header = json.dumps(client_socket.recv(1024))
            except socket.timeout:
                print(f"Timeout from {client_address}")
                client_socket.close()
                continue
            
            connection_type = header['protocol']
            if connection_type  == 'J-Mail':
                

                print(f"{len(active_terminal_clients)} terminal clients online.")


            else:
                print(f"Unknown connection protocol '{connection_type}' from {client_address}")
                client_socket.close()

        except Exception as e:
            print(f"Fatal error: {e}")
            raise