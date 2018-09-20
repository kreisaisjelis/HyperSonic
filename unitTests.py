from hyper import GameState
from hyper import GlobalState
import sys
import filecmp
import os
from os.path import isfile, join

dirName = 'unitTest/'
tests = set([f.split('.')[0] for f in os.listdir(dirName) if isfile(join(dirName, f))])

print(tests)

for testName in tests:
	inputFName = dirName + testName + '.in'
	outputFName = dirName +  testName + '.out'
	expectedResultFName = dirName +  testName + '.exp'
	commandFName = dirName +  testName + '.com'

	with open(outputFName, 'w+') as fOut, open(inputFName) as fIn, open(expectedResultFName) as fExp, open(commandFName) as fCom:
		sys.stderr = fOut
		sys.stdin = fIn
		commands = fCom.read()
		#print(commands)
		exec(commands)

	with open(outputFName) as fOut, open(expectedResultFName) as fExp:
		if fOut.read() == fExp.read():
			print(f'Test "{testName}" passed')
			fOut.close()
			os.remove(outputFName)
		else:
			print(f'Test "{testName}" FAILED!')

