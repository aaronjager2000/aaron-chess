# main driver. handles input and displays current gamestate object
#p.init()
import pygame as p 
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# init global dict of images so we only load them once. this will be called exactly once in main

def loadImages():
  pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'wp']
  for piece in pieces:
    IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
  # we can access an image like so: 'IMAGES['bR']'

  """
  main driver for code/ will handle user input and updating graphics
  """
  
def main():
  p.init()
  screen = p.display.set_mode((WIDTH, HEIGHT))
  clock = p.time.Clock()
  screen.fill(p.Color('white'))
  gs = ChessEngine.GameState()
  validMoves = gs.getValidMoves()
  moveMade = False
  loadImages() #only do once, before while loop
  gameRun = True
  sqSelected = () # keep track of last click of user as tuple row,col
  playerClicks = [] # track player clicks two tuples: [(6,4), (4,4)]
  while gameRun:
    for i in p.event.get():
      if i.type == p.QUIT:
        gameRun = False
      elif i.type == p.MOUSEBUTTONDOWN:
          location = p.mouse.get_pos() #x,y of mouse
          col = location[0]//SQ_SIZE
          row = location[1]//SQ_SIZE
          if sqSelected == (row,col): #user clicks same square twice
            sqSelected = () # deselect if invalid
            playerClicks = [] #clear player clicks
          else:
            sqSelected = (row,col)
            playerClicks.append(sqSelected) #append both 1st and 2nd clicks
          if len(playerClicks) == 2: #after 2nd click
            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
            print(move.getChessNotation())
            for i in range(len(validMoves)):
              if move == validMoves[i]:
                gs.makeMove(move)
                moveMade = True
                sqSelected = () # reset user clicks
                playerClicks = [] # reset clicks
            if not moveMade:
              playerClicks = [sqSelected]
      elif i.type == p.KEYDOWN:
        if i.key == p.K_z:
          gs.undoMove()
          moveMade = True
            
    if moveMade:
      validMoves = gs.getValidMoves()
      moveMade = False
      
    drawGameState(screen, gs)
    clock.tick(MAX_FPS)
    p.display.flip()
      
def drawGameState(screen, gs):
  drawBoard(screen) # draws squares
  drawPieces(screen, gs.board) # draws pieces
  
def drawBoard(screen):
  colors = [p.Color(227,193,111), p.Color(184,139,74)]
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      color = colors[((r+c)%2)] # alternates light and dark squares
      p.draw.rect(screen,color,p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
  
def drawPieces(screen,board):
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      piece = board[r][c]
      if piece != '--':
        screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    
  
      
      
# if you ever import ChessMain it won't run the function
if __name__ == '__main__':
  main()