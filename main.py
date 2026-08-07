import socket
import threading
import json
import time
import datetime
import TelePy as tp
import jmail_client as jim
import ipaddress

active_terminal_clients = set()
active_terminal_clients_lock = threading.Lock()

start_time = None

def segment_dictionary(data_dict, max_packet_size=1024, header_size=32):
    # 1. Convert dictionary to UTF-8 bytes
    raw_bytes = json.dumps(data_dict).encode('utf-8')
    
    # 2. Calculate maximum payload per chunk
    max_payload_size = max_packet_size - header_size
    
    # 3. Calculate total segments required
    total_bytes = len(raw_bytes)
    total_segments = (total_bytes + max_payload_size - 1) // max_payload_size
    
    segments = []
    for seq_num in range(total_segments):
        start = seq_num * max_payload_size
        end = start + max_payload_size
        chunk = raw_bytes[start:end]
        
        # 4. Create a fixed-size header (e.g., "SEQ:0001/0010|")
        # Format: 4-digit sequence, 4-digit total, padded to header_size
        header_str = f"SEQ:{seq_num + 1:04d}/{total_segments:04d}|"
        header_bytes = header_str.encode('utf-8').ljust(header_size, b' ')
        
        # 5. Combine header and payload
        packet = header_bytes + chunk
        segments.append(packet)
        
    return segments

def reassemble_segments(received_packets, header_size=32):
    # Sort by sequence number read from header
    def get_seq(packet):
        header = packet[:header_size].decode('utf-8').strip()
        # Header format: "SEQ:0001/0010|"
        seq_part = header.split('|')[0].replace('SEQ:', '')
        curr_seq, _ = seq_part.split('/')
        return int(curr_seq)
    
    sorted_packets = sorted(received_packets, key=get_seq)
    
    # Strip headers and reassemble raw payload
    raw_bytes = b"".join(packet[header_size:] for packet in sorted_packets)
    
    # Deserialize back into dictionary
    return json.loads(raw_bytes.decode('utf-8'))


def load_json(file):
    global settings
    with open(file, "r") as f:
        return json.load(f)    


def setup(port):
    global settings
    Sct = socket.socket()  # creating the socket
    
    Sct.bind(("", int(port)))  # Bind port
    Sct.listen(5)  # listens for clients
    print(f'J-Mail server started on port:{port}')
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


def check_domain(sender_domain, client_address):
    try:
        target_ip = str(ipaddress.ip_address(client_address))

        addr_info = socket.getaddrinfo(sender_domain, None)
        resolved_ips = {info[4][0] for info in addr_info}

        return target_ip in resolved_ips

    except (socket.gaierror, ValueError):
        return False


def handle_jmail(client_socket, client_address, header):
    try:
        sender_domain = header["sender"].split(":")[1]
        username = header["receiver"].split(":")[0]

        if not check_domain(sender_domain, client_address):
            if not(sender_domain == "127.0.0.1"):
                client_socket.close()
        
        if not jim.load_json(f'jmail/{username}.json'):
            client_socket.close()


        client_socket.send(bytes("ACK", "utf-8"))


        jmail_segments = []
        total_segments = 1 

        while len(jmail_segments) < total_segments:
            packet = client_socket.recv(1056)  # 1024 payload + 32 header
            client_socket.send(b"ACK")

            total_segments = int(packet[9:13])
            jmail_segments.append(packet)

        jmail = reassemble_segments(jmail_segments)

        if jim.hash_password(json.dumps(jmail)) == header["hash"]:
            user_json = jim.load_json(f'jmail/{username}.json')
            user_json["unread"].insert(0, jmail)
            jim.write_json(f'jmail/{username}.json', user_json)
            client_socket.send(b'DONE')

            

            
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
            client_socket.settimeout(25)

            try:
                # Receive connection type (like 'terminal') from the client
                
                header = json.loads(client_socket.recv(1024).decode().strip())
            except socket.timeout:
                print(f"Timeout from {client_address}")
                client_socket.close()
                continue
            
            connection_type = header['protocol']
            if connection_type  == 'J-Mail':
                
                ping_thread = threading.Thread(
                    target=handle_jmail,
                    args=(client_socket, client_address, header),
                    name=f"Json-{client_address}"
                )
                ping_thread.start()


            else:
                print(f"Unknown connection protocol '{connection_type}' from {client_address}")
                client_socket.close()

        except Exception as e:
            print(f"Fatal error: {e}")
            raise

if __name__ == '__main__':
    tp.start(jim.jmail_client) 