gameState = GameState(GlobalState().LoadGlobals())
gameState.ReadField()
gameState.ReadEntities()
gameState.ChainBombs()
gameState.PredictExplosions()
bomb_target,next_move, some = gameState.GetNewTarget(True)

path = [(0,0),(1,0),(2,0),(3,0)]
#print(f'DangerField is:{gameState.dangerField}', file=sys.stderr)
print(f'Path {path} is safe:{gameState.IsPathSafe(path)}', file=sys.stderr)

path = [(0,0),(0,1),(0,2),(0,3)]
print(f'Path {path} is safe:{gameState.IsPathSafe(path)}', file=sys.stderr)
print(f'Bomb target, next_move {bomb_target},{next_move}', file=sys.stderr)