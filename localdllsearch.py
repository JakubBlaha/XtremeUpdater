import os

with open('availabledlls.txt', 'w') as f:
    f.writelines(
        [item + '\n' for item in os.listdir(os.path.join(os.getcwd(), 'dll'))])
