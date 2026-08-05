import json
import os

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

def tprint(string):
    if string[0:1] == 'c:':
        cprint(string[2:])

doc = load_jdoc("example.tdoc")
for page in doc:
    for line in page:
        jprint(line)
    input(f"Page {doc.index(page)+1} of {len(doc)}")