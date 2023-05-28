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

def load_images():
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
  valid_moves = gs.get_valid_moves()
  move_made = False
  load_images() #only do once, before while loop
  game_run = True
  sq_selected = () # keep track of last click of user as tuple row,col
  player_clicks = [] # track player clicks two tuples: [(6,4), (4,4)]
  while game_run:
    for i in p.event.get():
      if i.type == p.QUIT:
        game_run = False
      elif i.type == p.MOUSEBUTTONDOWN:
          location = p.mouse.get_pos() #x,y of mouse
          col = location[0]//SQ_SIZE
          row = location[1]//SQ_SIZE
          if sq_selected == (row,col): #user clicks same square twice
            sq_selected = () # deselect if invalid
            player_clicks = [] #clear player clicks
          else:
            sq_selected = (row,col)
            player_clicks.append(sq_selected) #append both 1st and 2nd clicks
          if len(player_clicks) == 2: #after 2nd click
            move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
            print(move.get_chess_notation())
            for i in range(len(valid_moves)):
              if move == valid_moves[i]:
                gs.make_move(move)
                move_made = True
                sq_selected = () # reset user clicks
                player_clicks = [] # reset clicks
            if not move_made:
              player_clicks = [sq_selected]
      elif i.type == p.KEYDOWN:
        if i.key == p.K_z:
          gs.undo_move()
          move_made = True
            
    if move_made:
      valid_moves = gs.get_valid_moves()
      move_made = False
      
    draw_game_state(screen, gs)
    clock.tick(MAX_FPS)
    p.display.flip()
      
def draw_game_state(screen, gs):
  draw_board(screen) # draws squares
  draw_pieces(screen, gs.board) # draws pieces
  
def draw_board(screen):
  colors = [p.Color(227,193,111), p.Color(184,139,74)]
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      color = colors[((r+c)%2)] # alternates light and dark squares
      p.draw.rect(screen,color,p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
  
def draw_pieces(screen,board):
  for r in range(DIMENSION):
    for c in range(DIMENSION):
      piece = board[r][c]
      if piece != '--':
        screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    
  
      
      
# if you ever import ChessMain it won't run the function
if __name__ == '__main__':
  main()