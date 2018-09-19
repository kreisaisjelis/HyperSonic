from hyper import GameState
from hyper import GlobalState
import sys

gameState = GameState(GlobalState().LoadGlobals())
gameState.ReadField()
gameState.ReadEntities()
gameState.ChainBombs()
gameState.PredictExplosions()
bomb_target,next_move = gameState.GetNewTarget(True)

print(f'Reachables {gameState.Reachable((1,1),3)}', file=sys.stderr)
print(f'Bombs {gameState.bombs}', file=sys.stderr)
print(f'Danger field {gameState.PredictExplosions()}', file=sys.stderr)