import hashlib
import json
import shlex
import socket
import datetime
import TelePy as tp

DOMAIN = tp.load_json("config")["jmail"]["domain"] #Enter domain or ip

def rprint(self, text, cap=" ", start=" ", end=" ", fill=" ", out_end="new", right_shift=0, printer=False):
    # Regex to strip ANSI sequences for visual length calculation
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    visible_text = ansi_escape.sub('', str(text))
    
    width = int(getattr(self, "column", 80))
    
    # Determine boundary caps
    prefix = cap if cap != " " else start
    suffix = cap if cap != " " else end
    
    inner = width - len(prefix) - len(suffix)
    
    # Push all padding to the left to align text to the right
    total_padding = max(0, inner - len(visible_text))
    left_padding_len = total_padding
    right_padding_len = 0
    
    # Apply right-shift to push text away from the right border towards the left
    if right_shift > 0:
        shift = min(right_shift, left_padding_len)
        left_padding_len -= shift
        right_padding_len += shift
        
    left_pad = fill * left_padding_len
    right_pad = fill * right_padding_len
    
    output = f"{prefix}{left_pad}{text}{right_pad}{suffix}"

    if printer:
        return output
    else:
        if out_end == "new":
            self.print(output)
        else:
            self.print(output, end=out_end)
    

def cprint(self, text, cap=" ", start=" ", end=" ", fill=" ", out_end="new", left_shift=0, printer=False):
    # Regex to strip ANSI sequences for visual length calculation
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    visible_text = ansi_escape.sub('', str(text))
    
    width = int(getattr(self, "column", 80))
    inner = width - len(start) - len(end)
    
    # Calculate required left and right padding based on VISIBLE characters
    total_padding = max(0, inner - len(visible_text))
    left_padding_len = total_padding // 2
    right_padding_len = total_padding - left_padding_len
    
    # Apply left-shift to slant/offset the text to the left
    if left_shift > 0:
        shift = min(left_shift, left_padding_len)
        left_padding_len -= shift
        right_padding_len += shift
        
    left_pad = fill * left_padding_len
    right_pad = fill * right_padding_len
    
    formatted_inner = f"{left_pad}{text}{right_pad}"
    
    if cap == " ":
        output = start + formatted_inner + end
    else:
        output = cap + formatted_inner + cap

    if printer:
        return output
    else:
        if out_end == "new":
            self.print(output)
        else:
            self.print(output, end=out_end)

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

def print_jmail(client, jmail):
    margin = 0
    tdoc = jmail["tdoc"]
    for page in tdoc:
        for line in page:
            if line[0:2] == 'c:':
                client.cprint(line[2:])
            elif line[0:2] == 'r:':
                client.rprint(line[2:])
            elif line[0:2] == 'm:':
                margin = int(line[2:])
            elif line == "@":
                client.blankline()
            else:
                client.print((margin*" ")+line)

        client.input(f"Page {tdoc.index(page)+1} of {len(tdoc)} Press enter to go to next page ...")

def date():
    current_datetime = datetime.datetime.now()
    return f"{current_datetime.day}/{current_datetime.month}/{current_datetime.year} {current_datetime.hour}:{current_datetime.minute}:{current_datetime.second}"

def hash_password(string: str) -> str:
    """Simple SHA-256 hash (use bcrypt/argon2 in production)."""
    return hashlib.sha256(string.encode()).hexdigest()

def load_json(file:str):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        return False

def load_tdoc(file_name):
    with open(file_name, "r") as fp:
        lines = fp.readlines()
        doc = []
        page = []
        for line in lines:
            
            if line.strip() == "#":
                doc.append(page)
                page = []
            else:
                page.append(line.strip())
        doc.append(page)
        return doc

def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

def logon(username, password):
    json = load_json(f"jmail/{username}.json")
    if not json:
        return False
    
    if json["password"] ==  hash_password(password):
        return True
    
    else:
        return False

def send_jmail(username, recipient, subject, tdoc):
    receiver_domain = recipient.split(":")[1]
    if receiver_domain == DOMAIN:
        receiver_domain = "127.0.0.1"
    jmail = {
        "datetime" : date(),
        "sender" : f"{username}:{DOMAIN}",
        "receiver" : recipient,
        "subject" : subject,
        "tdoc" : tdoc
    }

    jmail_segments = segment_dictionary(jmail)
    jmail_hash = hash_password(json.dumps(jmail))

    header = {
        "protocol" : "J-Mail",
        "jmail_size" : len(jmail_segments),
        "sender" : f"{username}:{DOMAIN}",
        "receiver" : recipient,
        "hash" : jmail_hash
    }

    try:
        Sct = socket.socket()
        Sct.connect((receiver_domain, 2005))

        Sct.send(bytes(json.dumps(header), "utf-8"))

        ACK = Sct.recv(1024).decode()
        if not(ACK == "ACK"):
            return False

        for seg in jmail_segments:
            
            Sct.send(seg)
            ACK = Sct.recv(1024).decode()
            if ACK != "ACK":
                return False

        
        
        COM = Sct.recv(1024).decode()
        if COM == "DONE":
            return True
        else:
            return False
    except (socket.timeout, socket.error) as e:
        print(f"Error: {e}")
        return False

def jmail_client(client):
    client.cprint = cprint.__get__(client)
    client.rprint = rprint.__get__(client)
    client.cls()
    client.print(f"Logon (Contact sysadmin for acount) DOMAIN:{DOMAIN}")
    client.print(f"IF you did not connect via this domain disconnect.")
    username = client.input("Username :>")
    password = client.hidden_input("Password :>")

    if not logon(username, password):
        client.print("Details incorrect")
        client.close("Pingu is swiss propaganda.")

    inbox = "unread"
    while True:
        jmails = load_json(f'jmail/{username}.json')
        client.cls()
        for jmail in jmails[inbox]:
            client.print(f"({jmails[inbox].index(jmail)}) [{jmail["datetime"]}] From : {jmail["sender"]} Subject : {jmail["subject"]}")
        if len(jmails[inbox]) == 0:
            client.input(f"You have no {inbox} jmails.")
        client.print("Enter help for help")
        command = client.input(":>")

        command = shlex.split(command)

        if command[0] == "help":
            client.cls()
            client.print("""
Commands:
jmail [address] "Subject" eg(jmail test:example.com "This is a test")
read [jmail number] eg(read 1)
toggle
""")
            client.input("Press enter to return")

        elif command[0] == "toggle":
            if inbox == "unread":
                inbox = "read"
            else:
                inbox = "unread"

        elif command[0] == "read":
            client.cls()


        