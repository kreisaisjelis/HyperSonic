import subprocess

myinput = open('input.txt')
myoutput = open('output.txt', 'w')

completed = subprocess.run(['python3', 'hyper.py'], stdin = myinput, stderr=subprocess.DEVNULL, stdout= myoutput )
print('returncode:', completed.returncode)

myoutput.flush()