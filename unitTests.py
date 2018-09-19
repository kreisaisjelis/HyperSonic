from hyper import GameState
from hyper import GlobalState
import sys
import filecmp

with open('unitTest1.out', 'w') as f, open('unitTest1.in') as fIn:
	sys.stderr = f
	sys.stdin = fIn


	gameState = GameState(GlobalState().LoadGlobals())
	gameState.ReadField()
	gameState.ReadEntities()
	gameState.ChainBombs()
	gameState.PredictExplosions()
	bomb_target,next_move = gameState.GetNewTarget(True)

	print(f'Reachables {gameState.Reachable((1,1),3)}', file=sys.stderr)
	print(f'Bombs {gameState.bombs}', file=sys.stderr)
	print(f'Danger field {gameState.PredictExplosions()}', file=sys.stderr)

print(filecmp.cmp('unitTest1.out','unitTest1.exp', False))