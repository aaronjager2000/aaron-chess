# stores all current state information, determines valid moves, and keeps move log
import pygame as p
class GameState():
  def __init__(self):
    p.display.set_caption('Chess')
    self.board = [
      ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
      ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
      ['--', '--', '--', '--', '--', '--', '--', '--'],
      ['--', '--', '--', '--', '--', '--', '--', '--'],
      ['--', '--', '--', '--', '--', '--', '--', '--'],
      ['--', '--', '--', '--', '--', '--', '--', '--'],
      ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
      ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
    
    self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                          'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
    
    self.moveLog = []
    self.whiteToMove = True
    
    self.whiteKingLocation = (7,4)
    self.blackKingLocation = (0,4)
    
    self.inCheck = False
    self.pins = []
    self.checks = []
    
    self.enpassantPossible = ()
    
  
  def makeMove(self, move):
    self.board[move.startRow][move.startCol] = '--'
    self.board[move.endRow][move.endCol] = move.pieceMoved
    self.moveLog.append(move) # log move so we can undo
    self.whiteToMove = not self.whiteToMove
    #update kings pos
    if move.pieceMoved == 'wK':
      self.whiteKingLocation = (move.endRow, move.endCol)
    elif move.pieceMoved == 'bK':
      self.blackKingLocation = (move.endRow, move.endCol)
      
    if move.isPawnPromotion:
      self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
      
    
  def undoMove(self):
    if len(self.moveLog) != 0:
      move = self.moveLog.pop()
      self.board[move.startRow][move.startCol] = move.pieceMoved
      self.board[move.endRow][move.endCol] = move.pieceCaptured
      self.whiteToMove = not self.whiteToMove
      #update kings pos
      if move.pieceMoved == 'wK':
        self.whiteKingLocation = (move.startRow, move.startCol)
      elif move.pieceMoved == 'bK':
        self.blackKingLocation = (move.startRow, move.startCol)
  
  
    """
    all moves considering checks
    """
  def getValidMoves(self):
    moves=[]
    self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
    if self.whiteToMove:
      kingRow = self.whiteKingLocation[0]
      kingCol = self.whiteKingLocation[1]
    else:
      kingRow = self.blackKingLocation[0]
      kingCol = self.blackKingLocation[1]
    if self.inCheck:
      if len(self.checks) == 1: # onlt 1 check, block check or move king
        moves = self.getAllPossibleMoves()
        #to block check you must move piece into square between king and checker
        check = self.checks[0]
        checkRow = check[0]
        checkCol = check[1]
        pieceChecking = self.board[checkRow][checkCol]
        validSquares = []
        #if knight, must capture knight or move king, other pieces can be blocked
        if pieceChecking[1] == 'N':
          validSquares = [(checkRow,checkCol)]
        else:
          for i in range(1,8):
            validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check directions
            validSquares.append(validSquare)
            if validSquare[0] == checkRow and validSquare[1] == checkCol: # once you get to piece end checks
              break
        # remove moves that don't block check or move kings
        for i in range(len(moves)-1,-1,-1):
          if moves[i].pieceMoved[1] != 'K': # move does not move king so it must block or capture
            if not (moves[i].endRow, moves[i].endCol) in validSquares: # move does not block or capture
              moves.remove(moves[i])
      else: # double check, king must move
        self.getKingMoves(kingRow,kingCol,moves)
    else: # not in check
      moves = self.getAllPossibleMoves()

    return moves

      
    """
    all moves without considering checks
    """
  def getAllPossibleMoves(self):
    moves = []
    for r in range(len(self.board)):
      for c in range(len(self.board[r])):
        turn = self.board[r][c][0]
        if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
          piece = self.board[r][c][1]
          self.moveFunctions[piece](r,c,moves)
    return moves
  
  def getPawnMoves(self,r,c,moves):
    piecePinned = False
    pinDirection = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piecePinned = True
        pinDirection = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break
    
    
    
    if self.whiteToMove:
      if self.board[r-1][c] == '--': # 1 square advance
        if not piecePinned or pinDirection == (-1,0):
          moves.append(Move((r,c), (r-1,c), self.board))
          if r == 6 and self.board[r-2][c] == '--': # 2 square advance
            moves.append(Move((r,c), (r-2,c), self.board))
          
      if c-1 >= 0:
        if self.board[r-1][c-1][0] == 'b':
          if not piecePinned or pinDirection == (-1,-1):
            moves.append(Move((r,c), (r-1,c-1), self.board))
        elif (r-1, c-1) == self.enpassantPossible:
          if not piecePinned or pinDirection == (-1,-1):
            moves.append(Move((r,c), (r-1,c-1), self.board, enpassantPossible=True))

      if c+1 <= 7:
        if self.board[r-1][c+1][0] == 'b':
          if not piecePinned or pinDirection == (-1,1):
            moves.append(Move((r,c), (r-1,c+1), self.board))
    
    else:
      if self.board[r+1][c] == '--':
        if not piecePinned or pinDirection == (1,0):
          moves.append(Move((r,c), (r+1,c), self.board))
          if r == 1 and self.board[r+2][c] == '--':
            moves.append(Move((r,c), (r+2,c), self.board))
      
      if c-1 >= 0:
        if self.board[r+1][c-1][0] == 'w':
          if not piecePinned or pinDirection == (1,-1):
            moves.append(Move((r,c), (r+1,c-1), self.board))
      
      if c+1 <= 7:
        if self.board[r+1][c+1][0] == 'w':
          if not piecePinned or pinDirection == (1,1):
            moves.append(Move((r,c), (r+1, c+1), self.board))
       
  def getRookMoves(self,r,c,moves):
    piecePinned = False
    pinDirection = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1]:
        piecePinned = True
        pinDirection = (self.pins[i][2], self.pins[i][3])
        if self.board[r][c][1] != 'Q':
          self.pins.remove(self.pins[i])
        break
        
    directions = ((-1,0), (0,-1), (1,0), (0,1))
    enemyColor = 'b' if self.whiteToMove else 'w'
    for d in directions:
      for i in range(1,8):
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
          if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
            endPiece = self.board[endRow][endCol]
            if endPiece == '--': # empty space valid
              moves.append(Move((r,c), (endRow, endCol), self.board))
            elif endPiece[0] == enemyColor: # enemy piece valid
              moves.append(Move((r,c), (endRow, endCol), self.board))
              break
            else: # friendly piece invalid
              break
        else: # off board
          break
  
  def getKnightMoves(self,r,c,moves):
    piecePinned = False
    pinDirection = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piecePinned = True
        pinDirection = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break
    
    knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
    allyColor = 'w' if self.whiteToMove else 'b'
    for m in knightMoves:
      endRow = r + m[0]
      endCol = c + m[1]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        if not piecePinned:
          endPiece = self.board[endRow][endCol]
          if endPiece[0] != allyColor: # empty or enemy piece
            moves.append(Move((r,c), (endRow, endCol), self.board))
          
  
  def getBishopMoves(self,r,c,moves):
    piecePinned = False
    pinDirection = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1]:
        piecePinned = True
        pinDirection = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break
    
    directions = ((-1,-1), (-1,1), (1,-1), (1,1))
    enemyColor = 'b' if self.whiteToMove else 'w'
    for d in directions:
      for i in range(1,8):
        endRow = r + d[0] * i
        endCol = c + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
          if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
            endPiece = self.board[endRow][endCol]
            if endPiece == '--': # empty space valid
              moves.append(Move((r,c), (endRow, endCol), self.board))
            elif endPiece[0] == enemyColor: # enemy piece valid
              moves.append(Move((r,c), (endRow, endCol), self.board))
              break
            else: # friendly piece invalid
              break
        else: # off board
          break
  
  def getQueenMoves(self,r,c,moves):
    self.getRookMoves(r,c,moves)
    self.getBishopMoves(r,c,moves)

  def getKingMoves(self,r,c,moves):
    rowMoves = (-1,-1,-1,0,0,1,1,1)
    colMoves = (-1,0,1,-1,1,-1,0,1)
    allyColor = 'w' if self.whiteToMove else 'b'
    for i in range(8):
      endRow = r + rowMoves[i]
      endCol = c + colMoves[i]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        endPiece = self.board[endRow][endCol]
        if endPiece[0] != allyColor: #empty or enemy
          # place king on end square check for checks
          if allyColor == 'w':
            self.whiteKingLocation = (endRow, endCol)
          else:
            self.blackKingLocation = (endRow, endCol)
          inCheck, pins, checks = self.checkForPinsAndChecks()
          if not inCheck:
            moves.append(Move((r,c), (endRow, endCol), self.board))
          # place king back on original location
          if allyColor == 'w':
            self.whiteKingLocation = (r,c)
          else:
            self.blackKingLocation = (r,c)
          
  
        
  def checkForPinsAndChecks(self):
    pins = [] # allied pin piece square and directional info (of potential check)
    checks = [] # squares where enemy is applying a check
    inCheck = False
    if self.whiteToMove:
      enemyColor = 'b'
      allyColor = 'w'
      startRow = self.whiteKingLocation[0]
      startCol = self.whiteKingLocation[1]
    else:
      enemyColor = 'w'
      allyColor = 'b'
      startRow = self.blackKingLocation[0]
      startCol = self.blackKingLocation[1]
    # check outward from king for pins and checks, keep track of pins
    directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
    for j in range(len(directions)):
      d = directions[j]
      possiblePin = () # reset possible pins
      for i in range(1,8):
        endRow = startRow + d[0] * i
        endCol = startCol + d[1] * i
        if 0 <= endRow < 8 and 0 <= endCol < 8:
          endPiece = self.board[endRow][endCol]
          if endPiece[0] == allyColor:
            if possiblePin == (): # 1st allied piece can be pinned
              possiblePin = (endRow,endCol,d[0],d[1])
            else: # 2nd allied piece, no pin or check possible in this direciton
              break
          elif endPiece[0] == enemyColor:
            type = endPiece[1]
            # orthogonally away from king and piece is a rook
            # diagonally away and piece is a bishop
            # 1 square away and diagonally and piece is pawn
            # any direction and piece is queen
            # any direction 1 square away and piece is king (this prevents illegal king moves ie moving into a piece controlled by enemy king)
            if (0 <= j <= 3 and type == 'R') or \
                  (4 <= j <= 7 and type == 'B') or \
                  (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                  (type == 'Q') or (i == 1 and type == "K"):
                if possiblePin == ():
                  inCheck = True
                  checks.append((endRow, endCol, d[0], d[1])) 
                  break
                else: # piece blocking pin
                  pins.append(possiblePin)
                  break
            else: # enemy piece not applying check
              break
    
    #check for knight checks gg no re 
    knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
    for m in knightMoves:
      endRow = startRow + m[0]
      endCol = startCol + m[1]
      if 0 <= endRow < 8 and 0 <= endCol < 8:
        endPiece = self.board[endRow][endCol]
        if endPiece[0] == enemyColor and endPiece[1] == 'N':
          inCheck = True
          checks.append((endRow,endCol,m[0],m[1]))    
    return inCheck, pins, checks          
            
      
      
        
  
    
    
class Move():
  
  ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}
  rowsToRanks = {v: k for k, v in ranksToRows.items()} # reverses dictionary using magic
  
  filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
  colsToFiles = {v: k for k, v in filesToCols.items()}
  
  # enpassantPossible passed in as optional parameter since we give it a default value 
  def __init__(self, startSq, endSq, board, enpassantPossible = False):
    self.startRow = startSq[0]
    self.startCol = startSq[1]
    self.endRow = endSq[0]
    self.endCol = endSq[1]
    self.pieceMoved = board[self.startRow][self.startCol]
    self.pieceCaptured = board[self.endRow][self.endCol]
    #pawn promotion
    #self.promotionChoice = 'Q'
    self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
      
    # en passant
    self.isEnpassantMove = enpassantPossible
    
      
    
    self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
  
  
  
  def __eq__(self, other):
    if isinstance(other,Move):
      return self.moveID == other.moveID
    return False
    
  def getChessNotation(self):
    return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
  
  def getRankFile(self, r, c):
    return self.colsToFiles[c] + self.rowsToRanks[r]