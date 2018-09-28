gameState = GameState(GlobalState().LoadGlobals())
gameState.ReadField()
gameState.ReadEntities()
gameState.ChainBombs()
gameState.PredictExplosions()
bomb_target,next_move, some = gameState.GetNewTarget(True)

print(f'Bomb target, next_move {bomb_target},{next_move}', file=sys.stderr)

predictedState = copy.deepcopy(gameState)
predictedState.AdvanceTime(1) 
predictedState.AddMyBomb(gameState.current_position)
predictedState.ChainBombs()
predictedState.PredictExplosions()
bomb_target,next_move, some = predictedState.GetNewTarget(True)


print(f'Validate safety in predicted state {predictedState.validateTargetForSafety(0,2,1, True)}', file=sys.stderr)
print(f'Next bomb target, next_move {bomb_target},{next_move}', file=sys.stderr)