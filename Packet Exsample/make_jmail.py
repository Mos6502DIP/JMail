import json

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

print(load_jdoc("example.jdoc"))