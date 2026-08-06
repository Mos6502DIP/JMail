import sys
import socket
import datetime
import time
import json
import time
import threading
import signal 
import sys
import traceback

running = True

buffer = 0

settings = {}

active_terminal_clients = set()
active_terminal_clients_lock = threading.Lock()

start_time = None

def shutdown(signum, frame): 
    print("Shutting down cleanly...") 
    sys.exit(0)

def load_config():
    global settings
    with open('config.json', "r") as f:
       settings = json.load(f)

def load_json(name):
    global settings
    with open(f'{name}.json', "r") as f:
        return json.load(f)       

def get_info(server_ip):
    try:
        server = server_ip.split(':')
        port = 1998
        if len(server) == 2:

            server_ip = server[0]

            port = int(server[1])

        Sct = socket.socket()
        Sct.connect((server_ip, port))
        Sct.send(bytes('json', "utf-8"))
        server_json = Sct.recv(6000).decode()
        Sct.close()
        return json.loads(server_json)
    
    except (socket.timeout, socket.error) as e:
        return False

def ping(server_ip):
    server = server_ip.split(':')
    port = 1998
    if len(server) == 2:

        server_ip = server[0]

        port = int(server[1])

    try:
        Sct = socket.socket()
        Sct.settimeout(5)  # Optional: timeout after a few seconds

        start_time = time.time()
        Sct.connect((server_ip, port))
        
        Sct.send(b'ping')  # Send "ping"
        
        response = Sct.recv(1024).decode()
        end_time = time.time()

        Sct.close()

        if response.strip().lower() == "pong":
            ping_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            return ping_ms
        else:
            return False

    except (socket.timeout, socket.error) as e:
        return False 


def date():
    current_datetime = datetime.datetime.now()
    return current_datetime.date()

def run_server(name, func, *args):
    """Wrapper so server crashes don't silently kill the thread."""
    while running:
        try:
            print(f"[{name}] Starting on port {args[1]}")
            func(*args)
            print(f"[{name}] Server stopped.")
            break

        except Exception:
            print(f"[{name}] Server crashed!")
            traceback.print_exc()

            # Prevent rapid restart loops
            time.sleep(5)

def shutdown(signum=None, frame=None):
    global running
    print("\nStopping servers...")
    running = False

def start(client_side, dev_mode=False):
    global running

    if dev_mode:
        import TelePy.dev as dvt
        dvt.dev(client_side)
        return

    import TelePy.ssh as sshmod
    import TelePy.tele as tele
    import TelePy.telnet as telnet

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    load_config()

    server_map = {
        "telepy": tele.start_telepy,
        "ssh": sshmod.start_ssh,
        "telnet": telnet.start_bbs_server,
    }

    threads = []

    for name, config in settings.items():

        if not config.get("enabled", False):
            continue

        if name not in server_map:
            print(f"Unknown server type '{name}'")
            continue

        thread = threading.Thread(
            target=run_server,
            args=(
                name,
                server_map[name],
                client_side,
                config["port"]
            ),
            name=f"{name}-server"
        )

        thread.start()
        threads.append(thread)

    print("All enabled servers started.")

    try:
        while running:

            # Watch for dead threads
            for thread in threads:
                if not thread.is_alive():
                    print(f"WARNING: {thread.name} has stopped.")

            time.sleep(5)

    finally:
        print("Waiting for servers to finish...")

        for thread in threads:
            thread.join(timeout=2)

        print("Shutdown complete.")
          

