gameState = GameState(GlobalState().LoadGlobals())
gameState.ReadField()
gameState.ReadEntities()
gameState.ChainBombs()
gameState.PredictExplosions()

print(f'Trap detected {gameState.DetectTrap()}', file=sys.stderr)