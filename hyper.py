import sys
import math
import random
import copy
import itertools
import time
from enum import Enum

#control constnts#####################################################################################################
maxTargetDistance = 9      #known optimum range [8;11]
valueOfRangeItem = 1          #known optimum [0.3-1]
valueOfBombItem = 2             #knonw optimum [2]
powerOfDistance =0.5     #known optimums [0.3, 0.5, 0.7]
coefficientOfDiminishingForPotentialItems = 1  #known optimums [0.5-1]

#control constants end#####################################################################################################
      
class TileType(Enum):
    EMPTY = 0
    WALL = 1
    EMPTY_BOX = 2
    BOX_WITH_RANGE_ITEM = 3
    BOX_WITH_BOMB_ITEM = 4
    def Decode(str):
        if str ==".":
            return TileType.EMPTY
        if str =="X":
            return TileType.WALL
        if str =="0":
            return TileType.EMPTY_BOX
        if str =="1":
            return TileType.BOX_WITH_RANGE_ITEM   
        if str =="2":
            return TileType.BOX_WITH_BOMB_ITEM             
class FieldTile:
    Type = TileType.EMPTY
    EndsInN = -1  

class PlayerMove:
    bomb = False
    move = (0,0)
    playerId = 0
    def __init__(self, playerId, x,y,bomb):
        self.bomb = bomb
        self.move = (x,y)
        self.playerId = playerId
    def __str__(self):
        return (self.playerId, self.move, self.bomb).__str__()
    def __repr__(self):
        return (self.playerId, self.move, self.bomb).__str__()        

class PossiblePlayerMoves:
    moves = []
    playerId  = -1
    def __init__(self, player, gameState):
        self.moves = []
        self.playerId = player['id']
        # player can stay in place
        self.moves.append(PlayerMove(player["id"],player["x"],player["y"], False))
        if player['bombsAvailable'] > 0:
            self.moves.append(PlayerMove(player["id"],player["x"],player["y"], True))
        # or he can move to neighbors
        neighbors = NeighborsOfTile(gameState.field,player["x"],player["y"])
        for tile in neighbors:
            if gameState.TileIsPassable(tile[0],tile[1], 1):
                self.moves.append(PlayerMove(player["id"],tile[0],tile[1], False))
                if player['bombsAvailable'] > 0:
                    self.moves.append(PlayerMove(player["id"],tile[0],tile[1], True))
    def __str__(self):
        return (self.playerId,self.moves).__str__()
    def __repr__(self):
        return self.__str__()        
        
class AllPossibleMoves:
    playerMoves = {}
    
    def __init__(self, players, field, bombs):
        self.playerMoves = {}
        for player in players:
            self.playerMoves[player] = PossiblePlayerMoves(players[player],field,bombs)

    def __str__(self):
        return self.playerMoves.__str__()

    
## -------------------------------------------------------------------------------------


    


def SimulateTrapsInOneMove(gameState, myNewPosition):
    predictedState = copy.deepcopy(gameState)
    predictedState.players[predictedState.myId]["x"]=myNewPosition[0] #This duplication is not cool
    predictedState.players[predictedState.myId]["y"]=myNewPosition[1]
    predictedState.current_position = myNewPosition
    
    for player in predictedState.players:
        if predictedState.players[player]["bombsAvailable"]>0 and player != gameState.myId:
            predictedState.bombs.append({'owner':player,'x':predictedState.players[player]["x"], 'y':predictedState.players[player]["y"], 'roundsLeft':8,'explosionRange':predictedState.players[player]["bombRange"]})
    predictedState.ChainBombs()
    predictedState.PredictExplosions()
    #print(f'-> Trap simulation done, about to detect traps...', file=sys.stderr)
    return predictedState.DetectTrap()
    #return 0
    
class GameState:
    
    def __init__(self,width,height, myId):
        self.width = width
        self.height = height
        self.myId = myId
        self.field = []
        self.tileField = []
        self.players = {}
        self.items = {}
        self.bombs = []
        self.dangerField ={}


    def BoxItemValue(self,my_bombs,x,y):
    
        str = self.field[y][x]
        if str == "0": #or str =="1" or str =="2":
            return 0
        elif str =="1":
            return valueOfRangeItem / pow((my_bombs+2),coefficientOfDiminishingForPotentialItems)
        elif str =="2":
            return valueOfBombItem / pow((my_bombs+2),coefficientOfDiminishingForPotentialItems)      
        else:
            return 0        
            
    def TileHasWall(self, str):
        if str == "X":
            return True
        else:
            return False
            
    
    def TileHasItem(self, x,y):
        return (x,y) in self.items

    def TileHasBomb(self, x,y,bombs, afterNTurns = 0):
        return [bomb for bomb in self.bombs if (bomb['x']==x and bomb['y']==y and bomb["roundsLeft"]>=afterNTurns)]
       
    def TileHasBox(self, x,y, afterNTurns =0):
        
        if (self.tileField[x][y][0] in {TileType.EMPTY_BOX, TileType.BOX_WITH_BOMB_ITEM, TileType.BOX_WITH_RANGE_ITEM}) and (self.tileField[x][y][1] >afterNTurns-1): #TODO not sure if -1 or so
            return True
        else:
            return False  
            
    def TileIsPassable(self, x,y, afterNTurns =0):
        
        str = self.field[y][x]
        res = not self.TileHasBox(x,y,afterNTurns) and not self.TileHasWall(str) and not self.TileHasBomb(x,y, afterNTurns)
        return res
        
    def TileIsExplosionPassable(self, x,y, afterNTurns =0):
        return (self.TileIsPassable( x,y, afterNTurns))# and not TileHasItem(x,y,items)) #TODO if tile has items after N turns
        
        
    def TileHasBomb(self, x,y, afterNTurns = 0):
        return [bomb for bomb in self.bombs if (bomb['x']==x and bomb['y']==y and bomb["roundsLeft"]>=afterNTurns)]
    
    def NeighborsOfTile(self,x,y):
        res = []
        if x>0:
            res.append((x-1,y))
        if y>0:
            res.append((x,y-1))
        if y<len(self.field)-1:
            res.append((x,y+1))
        if x<len(self.field[0])-1:
            res.append((x+1,y))         
        return res
    
    def PassableNeighbors(self, x,y, afterNTurns = 0):
        neighbors = self.NeighborsOfTile(x,y)
        return [tile for tile in neighbors if self.TileIsPassable( tile[0], tile[1],afterNTurns)]


    def LineOfEffect(self, from_x,from_y, to_x,to_y, rng, afterNTurns =0):
        #print(f'  Lof from  {(from_x,from_y)} to {(to_x,to_y)}', file=sys.stderr)
        #if (from_x,from_y)==(12,8) and (to_x,to_y)==(4,8):
        #    print(f'  LoE bombs be like {bombs}', file=sys.stderr)
        if from_x== to_x and abs(from_y-to_y)<rng:
            for y in range(min(from_y,to_y)+1, max(from_y,to_y)):
                if not self.TileIsExplosionPassable(to_x,y,afterNTurns):
                    return False
            return True
        if from_y== to_y and abs(from_x-to_x)<rng:
            for x in range(min(from_x,to_x)+1, max(from_x,to_x)):
                if not self.TileIsExplosionPassable(x,to_y,afterNTurns):
                    return False        
            return True
        return False
       
    
    def EvaluateBombingTarget(self, x, y, rng, my_bombs,afterNTurns=0):
        val = 0;
        #print(f' x: {x}, y: {y } has bomb: {TileHasBomb(x,y, bombs)} Tile is passable: {TileIsPassable(field, x, y, bombs)}', file=sys.stderr)
        if not self.TileIsPassable( x, y, afterNTurns): #if position is unpassable, it is worthless
            return -1
        for i in range(-rng+1,rng):
            #print(f' i: {i}', file=sys.stderr)
            if (y+i >=0) and (y+i<len(self.field)) and self.TileHasBox(x, y+i) and self.LineOfEffect(x,y,x,y+i,rng, afterNTurns): #up/down
                val += (1 +self.BoxItemValue(my_bombs,x,y+i))
            if (x+i >=0) and (x+i<len(self.field[0])) and self.TileHasBox(x+i, y) and self.LineOfEffect(x,y,x+i,y,rng, afterNTurns): #left/right
                val +=(1 +self.BoxItemValue(my_bombs,x+i,y ) )             
        #double counting center does not matter, since we know its not a box
        return val


    def GetPathFromReachables(self,reachables, target, pathLength):
        path=[]
        #pathLength = 0
        if target == (-1,-1):
            return [(-1,-1),(-1,-1)]
        #if (not reachables):
        #    return path
        #print(f'We trying to get path to {target} in  {reachables}', file=sys.stderr)
        #print(f'.Found {target} at pathLength {pathLength}', file=sys.stderr)
        step = target
        for stepNumber in range(pathLength,-1,-1):
    
            #print(f'..adding step {step} at stepNumber {stepNumber}', file=sys.stderr)
            path.insert(0,step)
           # print(f'..and next step is {reachables[stepNumber][step]}', file=sys.stderr)
            step = reachables[stepNumber][step]
        #print(f'Returnig path  {path}', file=sys.stderr)
        return path
    
    def ItemValueOfPath(self, path):
        val = 0
        for tile in path:
            if tile in self.items:
                if self.items[tile] == 2:
                    val +=valueOfBombItem
                else:
                    val += valueOfRangeItem
        return val
        
    def EvaluateTarget(self, bombValue, pathLength, itemValue, myBombsLeft):  
        #if (bombValue > 0.5):
        #    print(f'->BombValue {bombValue}, pathLength {pathLength}, itemValue {itemValue}, mybombs left {myBombsLeft}', file=sys.stderr)
        return (bombValue+ itemValue/(myBombsLeft+1))/pow(pathLength,powerOfDistance)


 
    def ReadField(self):
        for row in range(self.height):
            self.field.append(list(input()))
        for x in range(self.width):
            self.tileField.append([])
            for y in range(self.height):
                self.tileField[x].append([TileType.Decode(self.field[y][x]),9999])

        
    def ReadEntities(self):
        entities = int(input())  

        for i in range(entities):
            entity_type, owner, x, y, param_1, param_2 = [int(j) for j in input().split()]
            if entity_type ==0:
                self.players[owner] = {'id':owner, 'x':x, 'y':y, 'bombsAvailable':param_1, 'bombRange':param_2}
            if entity_type ==1:
                self.bombs.append({'owner':owner,'x':x, 'y':y, 'roundsLeft':param_1,'explosionRange':param_2})
            if entity_type ==2:
                self.items[(x,y)] = param_1
           # if (entity_type == 0 ) and (owner == my_id):
        self.current_position = (self.players[my_id]['x'],self.players[my_id]['y'])
        self.my_bombs = self.players[my_id]['bombsAvailable']
        self.my_range = self.players[my_id]['bombRange']
        
    def ChainBombsInternal(self,field, bombs, items):
        while True:
            bombs.sort(key=lambda bomb: bomb['roundsLeft']) # we need this sorted for more efficient chain explosion processing later
            haveChaining = False
            for (bomb1, bomb2) in itertools.combinations(bombs, 2):
                if bomb1['roundsLeft'] < bomb2['roundsLeft'] and self.LineOfEffect(bomb1['x'],bomb1['y'], bomb2['x'],bomb2['y'], bomb1['explosionRange'], bomb1["roundsLeft"]):
                    bomb2['roundsLeft'] = bomb1['roundsLeft']
                    haveChaining = True
            if not haveChaining:
                break
                
        return
    def ChainBombs(self):
        return self.ChainBombsInternal(self.field,self.bombs, self.items)
    

    def PredictExplosions(self):
        self.dangerField={}
        for bomb in self.bombs:
            for x in range(bomb['x']-bomb['explosionRange'],bomb['x']+bomb['explosionRange']):
                if x>=0 and x<self.width:
                    if self.LineOfEffect(bomb['x'],bomb['y'],x,bomb['y'],bomb['explosionRange'],  bomb["roundsLeft"]):
                        if self.TileHasBox(x,bomb['y']):
                            self.tileField[x][bomb['y']][1] = bomb["roundsLeft"] #TODO only the smallest should be applied
                            self.field[bomb['y']][x]="B"
                        elif (x,bomb['y']) in self.dangerField:
                            self.dangerField[(x,bomb['y'])].append(bomb['roundsLeft'])
                        else:
                            self.dangerField[(x,bomb['y'])]=[bomb['roundsLeft']]
            for y in range(bomb['y']-bomb['explosionRange'],bomb['y']+bomb['explosionRange']):
                if y>=0 and y<self.height: 
                    if self.LineOfEffect(bomb['x'],bomb['y'],bomb['x'],y,bomb['explosionRange'], bomb["roundsLeft"]):
                        if self.TileHasBox(bomb['x'],y):                
                            self.field[y][bomb['x']]="B"
                            self.tileField[bomb['x']][y][1] = bomb["roundsLeft"] #TODO only the smallest should be applied
                        elif (bomb['x'],y) in self.dangerField:
                            self.dangerField[(bomb['x'],y)].append(bomb['roundsLeft'])
                        else:
                            self.dangerField[(bomb['x'],y)]=[bomb['roundsLeft']]
        return self.dangerField
        

        
    def Reachable(self, fromPosition, maxDistance = maxTargetDistance):
        return self.ReachableInternal(self.field, self.dangerField, self.bombs, fromPosition, maxDistance)

  
    def ReachableInternal(self, field, dangerField, bombs, fromPosition, maxDistance = maxTargetDistance):

        reachableInAny = {}
        reachableInAny[0]={}
        reachableInAny[0][(fromPosition[0],fromPosition[1])]=((-1,-1))
        
        for NoOfTurns in range(1,maxDistance+1):
            reachableInAny[NoOfTurns]={}
            #by staying put for one turn..
            for tile in reachableInAny[NoOfTurns-1]: 
                if tile not in dangerField or (NoOfTurns+1) not in dangerField[tile]:
                    reachableInAny[NoOfTurns][tile]=tile
            #by moving one step froreachable in N-1
            for sourceTile in reachableInAny[NoOfTurns-1]: 
                for targetTile in self.PassableNeighbors(sourceTile[0],sourceTile[1], NoOfTurns): #TODO update field and bombs with simulated explosions
                    if targetTile not in reachableInAny[NoOfTurns] and (targetTile not in dangerField or (NoOfTurns+1) not in dangerField[targetTile]):
                        reachableInAny[NoOfTurns][targetTile] = sourceTile   
        return reachableInAny
        
    def GetNewTarget(self, withBomb):
        targetingStartTime = time.time()
        bestVal = -1

        nextMove = self.current_position #we default to current position, assuming that not moving is safer, if no good moves are available
        path = ()
        targetList = {}      
        reachable = self.Reachable(self.current_position)
        #print(f'->Bombing target selection...', file=sys.stderr)
        #print(f'--> reachables for targetSelection: {reachable}', file=sys.stderr) 
        #print(f'--> tileField at (9,10) for targetSelection: {self.tileField[9][10]}', file=sys.stderr)
        #print(f'--> field at (10,10) for targetSelection: {self.field[10][10]}', file=sys.stderr)

        for pathLength in reachable:
            if reachable[pathLength]:
                for tile in reachable[pathLength]:
                    path = self.GetPathFromReachables(reachable, tile, pathLength)
                    targetList[(tile,pathLength)] = {'path': path, 'bombingValue':-1,'pathValue':-1,'totalValue':-1, 'canEscapeAfterBombing':False, 'canEscapeButNoBombing':False, 'isEndpointInDangerField':(tile in self.dangerField), 'trapOnPath':-2}
                    if ((self.my_bombs >0) and (withBomb)) or not targetList[(tile,pathLength)]['isEndpointInDangerField']: #(not tile in self.dangerField): #TODO - stil not good
                    #if (not tile in dangerField):
                        targetList[(tile,pathLength)]['bombingValue'] = self.EvaluateBombingTarget(tile[0], tile[1], self.my_range, self.my_bombs)
                        targetList[(tile,pathLength)]['pathValue'] = self.ItemValueOfPath(path)
                        targetList[(tile,pathLength)]['totalValue'] = self.EvaluateTarget(targetList[(tile,pathLength)]['bombingValue'],len(path),targetList[(tile,pathLength)]['pathValue'] ,self.my_bombs)
                        newVal = targetList[(tile,pathLength)]['totalValue']
                        #if (tile == (10,0)) or (tile == (12,1)):
                        #    print(f'->Value of {tile} is {newVal}', file=sys.stderr)
                        #    print(f'->SAafety for {tile} is {self.validateTargetForSafety(tile[0],tile[1], len(path)-1, withBomb = withBomb)}', file=sys.stderr)

                #print(f'->Bombing path of length {pathLength} to target selected. Target {bestTarget}, path: {bestPath}', file=sys.stderr) 
        
        #sortedTargetList = sorted((value['totalValue'], key) for (key,value) in targetList.items())
        sortedTargetList = sorted(targetList.items(), key=lambda x: x[1]['totalValue'], reverse=True)
        bestTarget= (-1,-1)
        bestPath = ((-1,-1))
        
        for ((tile, dist),targetAttr) in sortedTargetList:
            targetAttr['canEscapeAfterBombing']  = self.validateTargetForSafety(tile[0],tile[1], len(targetAttr['path'])-1, withBomb = withBomb)
            if targetAttr['canEscapeAfterBombing']:
                #targetAttr['trapOnPath'] = (SimulateTrapsInOneMove(self,targetAttr['path'][1]) if len(targetAttr['path'])>1 else 0)
                #if targetAttr['trapOnPath'] >=0:
                bestTarget = tile
                bestPath = targetAttr['path']
                break
        print(f'->Top 5 high value targets. {sortedTargetList[:3]}', file=sys.stderr) 

        if len(bestPath)>1:
            nextMove = bestPath[1]
        else:
            nextMove = self.current_position
        #print(f'->Safety of () in {len(bestPath)-1} turns {self.validateTargetForSafety(bestTarget[0],bestTarget[1], len(bestPath)-1, withBomb)} with bomb: {withBomb}', file=sys.stderr) 
        #print(f'->Safety of {bestTarget} in {len(bestPath)-1} turns {self.validateTargetForSafety(bestTarget[0],bestTarget[1], len(bestPath)-1, withBomb)} with bomb: {withBomb}', file=sys.stderr) 
        #print(f'->Bombing target selected. {bestTarget}, next move {nextMove}, path {bestPath}', file=sys.stderr)  
        #if bestTarget != (-1,-1):
        #    print(f'->Target List {targetList}', file=sys.stderr)
        
        targetingEndTime = time.time()
        print(f'!!--->Targeting took {(targetingEndTime-targetingStartTime)*1000} miliseconds', file=sys.stderr)
        return bestTarget, nextMove  
        
    def AdvanceTime(self, NrOfTurns): #TODO
        self.AdvanceBombTimers(NrOfTurns)

    
    def AdvanceBombTimers(self, numberOfTurns):
        
        for bomb in self.bombs:
            bomb['roundsLeft'] -= numberOfTurns
            if bomb['roundsLeft'] < 0:
                self.bombs.remove(bomb)

    def AddMyBomb(self,position):
        return self.AddBomb(self.myId, position, self.my_range)
        
    def AddBomb(self, owner_id, position, rng):
        self.bombs.append({'owner':owner_id,'x':position[0], 'y':position[1], 'roundsLeft':8,'explosionRange':rng})
        return
    def validateTargetForSafety(self,  x, y,numberOfTurns,  withBomb = True):
            #print(f'VAlidating safety of  {x,y} wth Bomb: {withBomb} ....', file=sys.stderr)
            predictedState = copy.deepcopy(self)
            predictedState.AdvanceTime(numberOfTurns)
            
            #predictedBombs = copy.deepcopy(self.bombs)
            #AdvanceBombTimers(predictedBombs, numberOfTurns)
            if withBomb:
                predictedState.AddBomb(0,(x,y),self.my_range)
                #predictedBombs.append({'owner':0,'x':x, 'y':y, 'roundsLeft':8,'explosionRange':self.my_range})
            #predictedField = copy.deepcopy(self.field)
            predictedState.ChainBombs()  
            #self.ChainBombsInternal(predictedField, predictedBombs, self.items)
            predictedState.PredictExplosions()
            #predictedDangerField = self.PredictExplosionsInternal(predictedField, predictedBombs, self.items)
            #predictedReachables = self.ReachableInternal(predictedField, predictedDangerField, predictedBombs, (x, y))
            predictedReachables = predictedState.Reachable((x,y))
            #print(f'.... SAafety bobs are of  {predictedBombs} ....', file=sys.stderr)
            #print(f'.... SAafety dangerField are of  {predictedDangerField[(4,8)]}... {predictedDangerField[(4,9)]} ....', file=sys.stderr)

            
            if predictedReachables:
                #escapeMoves = #[tile for tile in predictedReachables[maxTargetDistance].keys()]# """if tile not in predictedDangerField.keys()"""]
                if predictedReachables[maxTargetDistance]:
                    #if (x,y)==(4,9):
                    #    print(f'.... SAafety reachables are of  {predictedReachables} ....', file=sys.stderr)
                    return True
                else:
    
                    return False    
            return false
    # trap detection ############################################
    def DetectTrap(self):
        res = 0;           
        if self.DetectTrapForPlayer(self.myId): 
            res = -1
           # print(f'Is TRAAP!', file=sys.stderr)
        elif [player for player in self.players if (self.players[player]["id"] != self.myId) and self.DetectTrapForPlayer(player)]:
            res = 1
        else:
            res = 0
           #print(f'Is no trap..', file=sys.stderr)
        return res #-1 - i am in a trap, 0 - no trap detected, 1 - other player in  a trap
        
    def DetectTrapForPlayer(self, playerId):
        reachables = self.Reachable((self.players[playerId]['x'],self.players[playerId]['y']),maxTargetDistance)
        #print(f'Detect trap reachables, len reachables: {reachables}, {len(reachables)}', file=sys.stderr)
        #return (len(reachables)<1) or (len(reachables)==1 and list(reachables)[0] in dangerField)
        #maxTargetDistance
        return len(reachables[maxTargetDistance])<1
    
# body starts here################################################################################################

width, height, my_id = [int(i) for i in input().split()]
last_position = (-1,-1)
#current_position = (-1,-1)

bomb_target = (-1,-1)
escape_target = (-1,-1)
next_move = (-1,-1)

message= ""



# game loop
while True:

    startTime = time.time()

    gameState = GameState(width, height, my_id)


    gameState.ReadField()
  
    gameState.ReadEntities()

   
    gameState.ChainBombs()
    
    #myMoves = PossiblePlayerMoves(gameState.players[gameState.myId],gameState)
    #allMoves = AllPossibleMoves(gameState.players,gameState.field,gameState.bombs)
    #print(f'My possible moves: {myMoves}', file=sys.stderr)
    #print(f'All possible moves: {allMoves}', file=sys.stderr)
    
    
    #print(f'Chack the field before...{field}', file=sys.stderr)
    gameState.PredictExplosions()
    #dangerField = PredictExplosions(gameState.field, gameState.bombs, gameState.items)
    #print(f'Chack the field after...{field}', file=sys.stderr)    
    #iAmInATrap = DetectTrapForPlayer(field, dangerField, bombs, items, players[my_id])
    isTrap = gameState.DetectTrap() #DetectTrap(gameState.field, gameState.dangerField, gameState.players, gameState.bombs, gameState.items, gameState.myId)
    if isTrap == -1:
        message = "Its a TRAP!" 
 
    bomb_target,next_move = gameState.GetNewTarget(True)
    
    if bomb_target ==(-1,-1):
        escape_target,next_move = gameState.GetNewTarget(False)

    print(f'Position {gameState.current_position}, bomb condition: {gameState.current_position == bomb_target}', file=sys.stderr)
    print(f'Bomb Target: {bomb_target}', file=sys.stderr)
    print(f'Escape Target: {escape_target}', file=sys.stderr)
    print(f'Message: {message}', file=sys.stderr)

    
    #print(f'TargetSafety: at {bomb_target}{validateTargetForSafety(field, bombs,bomb_target[0], bomb_target[1], my_range, 1)}', file=sys.stderr)

    if (gameState.current_position == bomb_target) and (gameState.my_bombs >0): #Simulate the state after one turn if we put bomb here and see if there is a target or ate least an escape
        predictedState = copy.deepcopy(gameState)
        predictedState.AdvanceTime(1) #does nothing yet, but in theory we need to advance/process bomb timers
        predictedState.AddMyBomb(gameState.current_position)
        predictedState.ChainBombs()
        predictedState.PredictExplosions()
        
        bomb_target,next_move = predictedState.GetNewTarget(True)
        if bomb_target ==(-1,-1):
            escape_target,next_move = predictedState.GetNewTarget(False)
            if escape_target ==(-1,-1): #if we are here, means that if we place bomb at this position, we can not escape. 
                escape_target,next_move = gameState.GetNewTarget(False) #maybe we can escape if we do not place bomb here?
                if escape_target ==(-1,-1):
                    print(f'MOVE {gameState.current_position[0]} {gameState.current_position[1]} {message}')
                    print(f'Strike that order, hold position!', file=sys.stderr)
                else:
                    print(f'MOVE {next_move[0]} {next_move[1]} {message}')
                    print(f'Abort plan, run for the hills!!', file=sys.stderr)                    
            else:    
                print(f'BOMB {next_move[0]} {next_move[1]} {message}')
                print(f'Bomb & Escape', file=sys.stderr)
        else:
            print(f'BOMB {next_move[0]} {next_move[1]} {message}')
            print(f'Bombing Bomb', file=sys.stderr)
    else: #if our target is not here, just proceed to the acquired target
        if bomb_target ==(-1,-1):
            if escape_target ==(-1,-1):
                print(f'MOVE {gameState.current_position[0]} {gameState.current_position[1]} {message}')
                print(f'Hold position', file=sys.stderr)
            else:
                print(f'MOVE {escape_target[0]} {escape_target[1]} {message}')
                print(f'Escape move', file=sys.stderr)
                
        else:
            print(f'MOVE {next_move[0]} {next_move[1]} {message}')   
            print(f'Bombing Move', file=sys.stderr)
             

            
    last_position = gameState.current_position
    endTime = time.time()
    print(f'Turn took {(endTime-startTime)*1000} miliseconds', file=sys.stderr)