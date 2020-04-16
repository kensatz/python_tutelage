
#  read file foo.py, return True or False  that has class Life
#  if not there, read main.py, ret line with class Life
#  else look in life.py

def search():
    foundp = False
    for file_name in ['foo.py', 'main.py', 'life.py']:
        try:
            with open(file_name, 'r') as file: 
                foundp = 'class Life' in file.read()
                if foundp: 
                    break
        except FileNotFoundError as e:
            pass
    return foundp

print(search())

