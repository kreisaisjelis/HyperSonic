import subprocess

myinput = open('input.txt')
myoutput = open('output.txt', 'w')
errorstr = open('errors.txt', 'w')

completed = subprocess.run(['python', 'hyper.py'], stdin = myinput, stderr=errorstr, stdout= myoutput )
print('returncode:', completed.returncode)

myoutput.flush()
errorstr.flush()