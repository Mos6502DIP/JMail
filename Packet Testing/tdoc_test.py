import json
import os
import regex as re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def load_jdoc(file_name):
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

def cprint(text, cap=" ", start=" ", end=" ", fill=" ", out_end="new", left_shift=0):
    # Regex to strip ANSI sequences for visual length calculation
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    visible_text = ansi_escape.sub('', str(text))
    
    width = 80
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

    if out_end == "new":
        print(output)
    else:
        print(output, end=out_end)

def tprint(doc):
    margin = 0
    for page in doc:
        for line in page:
            if line[0:2] == 'c:':
                cprint(line[2:])
            elif line[0:2] == 'm:':
                margin = int(line[2:])
            elif line == "@":
                print(" ")
            else:
                print((margin*" ")+line)
        input(f"Page {doc.index(page)+1} of {len(doc)}")
    
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


jmail = {
    "sender" : "miku:lab.telepy.net",
    "reciver" : "fractal:telepy.net",
    "subject" : "Extract from the book you asked for!",
    "tdoc" : load_jdoc("example.tdoc")
}



segments = segment_dictionary(jmail)

made_mail = reassemble_segments(segments)

tprint(made_mail["tdoc"])
