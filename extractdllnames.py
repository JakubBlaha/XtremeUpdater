import os

with open("htmldlls.html", "r") as html:
    text = html.read()

reading_string = False
strs = []
string = ""

for char in text:
    if char == '"' and not reading_string:
        reading_string = True
    elif char == '"' and reading_string:
        reading_string = False
        strs.append(string)
        string = ""
    elif reading_string:
        string += char

for string in strs:
    if not os.path.splitext(string)[1] == ".dll":
        strs = [x for x in strs if x != string]

input(tuple(strs))
