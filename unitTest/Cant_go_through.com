gameState = GameState(GlobalState().LoadGlobals())
gameState.ReadField()
gameState.ReadEntities()
gameState.ChainBombs()
gameState.PredictExplosions()
bomb_target,next_move, some = gameState.GetNewTarget(True)

print(f'Bomb target, next_move {bomb_target},{next_move}', file=sys.stderr)