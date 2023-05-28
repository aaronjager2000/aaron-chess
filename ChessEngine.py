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
    
    self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves, 
                          'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
    
    self.move_log = []
    self.white_to_move = True
    
    self.white_king_location = (7,4)
    self.black_king_location = (0,4)
    
    self.in_check = False
    self.pins = []
    self.checks = []
    
    self.enpassant_possible = ()
    
    self.current_castling_right = castle_rights(True, True, True, True)
    self.castle_rights_log = [self.current_castling_right]
    
  
  def make_move(self, move):
    self.board[move.start_row][move.start_col] = '--'
    self.board[move.send_row][move.end_col] = move.piece_moved
    self.move_log.append(move) # log move so we can undo
    self.white_to_move = not self.white_to_move
    #update kings pos
    if move.piece_moved == 'wK':
      self.white_king_location = (move.send_row, move.end_col)
    elif move.piece_moved == 'bK':
      self.black_king_location = (move.send_row, move.end_col)
      
    if move.is_pawn_promotion:
      self.board[move.send_row][move.end_col] = move.piece_moved[0] + 'Q'
      
    
  def undo_move(self):
    if len(self.move_log) != 0:
      move = self.move_log.pop()
      self.board[move.start_row][move.start_col] = move.piece_moved
      self.board[move.send_row][move.end_col] = move.piece_captured
      self.white_to_move = not self.white_to_move
      #update kings pos
      if move.piece_moved == 'wK':
        self.white_king_location = (move.start_row, move.start_col)
      elif move.piece_moved == 'bK':
        self.black_king_location = (move.start_row, move.start_col)
  
  
    """
    all moves considering checks
    """
  def get_valid_moves(self):
    moves=[]
    self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
    if self.white_to_move:
      king_row = self.white_king_location[0]
      king_col = self.white_king_location[1]
    else:
      king_row = self.black_king_location[0]
      king_col = self.black_king_location[1]
    if self.in_check:
      if len(self.checks) == 1: # onlt 1 check, block check or move king
        moves = self.get_all_possible_moves()
        #to block check you must move piece into square between king and checker
        check = self.checks[0]
        check_row = check[0]
        check_col = check[1]
        piece_checking = self.board[check_row][check_col]
        valid_sqaures = []
        #if knight, must capture knight or move king, other pieces can be blocked
        if piece_checking[1] == 'N':
          valid_sqaures = [(check_row,check_col)]
        else:
          for i in range(1,8):
            valid_sqaure = (king_row + check[2] * i, king_col + check[3] * i) # check directions
            valid_sqaures.append(valid_sqaure)
            if valid_sqaure[0] == check_row and valid_sqaure[1] == check_col: # once you get to piece end checks
              break
        # remove moves that don't block check or move kings
        for i in range(len(moves)-1,-1,-1):
          if moves[i].piece_moved[1] != 'K': # move does not move king so it must block or capture
            if not (moves[i].send_row, moves[i].end_col) in valid_sqaures: # move does not block or capture
              moves.remove(moves[i])
      else: # double check, king must move
        self.get_king_moves(king_row,king_col,moves)
    else: # not in check
      moves = self.get_all_possible_moves()

    return moves

      
    """
    all moves without considering checks
    """
  def get_all_possible_moves(self):
    moves = []
    for r in range(len(self.board)):
      for c in range(len(self.board[r])):
        turn = self.board[r][c][0]
        if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
          piece = self.board[r][c][1]
          self.move_functions[piece](r,c,moves)
    return moves
  
  def get_pawn_moves(self,r,c,moves):
    piece_pinned = False
    pin_direction = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piece_pinned = True
        pin_direction = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break
    
    
    
    if self.white_to_move:
      if self.board[r-1][c] == '--': # 1 square advance
        if not piece_pinned or pin_direction == (-1,0):
          moves.append(Move((r,c), (r-1,c), self.board))
          if r == 6 and self.board[r-2][c] == '--': # 2 square advance
            moves.append(Move((r,c), (r-2,c), self.board))
          
      if c-1 >= 0:
        if self.board[r-1][c-1][0] == 'b':
          if not piece_pinned or pin_direction == (-1,-1):
            moves.append(Move((r,c), (r-1,c-1), self.board))
        elif (r-1, c-1) == self.enpassant_possible:
          if not piece_pinned or pin_direction == (-1,-1):
            moves.append(Move((r,c), (r-1,c-1), self.board, enpassant_possible=True))

      if c+1 <= 7:
        if self.board[r-1][c+1][0] == 'b':
          if not piece_pinned or pin_direction == (-1,1):
            moves.append(Move((r,c), (r-1,c+1), self.board))
    
    else:
      if self.board[r+1][c] == '--':
        if not piece_pinned or pin_direction == (1,0):
          moves.append(Move((r,c), (r+1,c), self.board))
          if r == 1 and self.board[r+2][c] == '--':
            moves.append(Move((r,c), (r+2,c), self.board))
      
      if c-1 >= 0:
        if self.board[r+1][c-1][0] == 'w':
          if not piece_pinned or pin_direction == (1,-1):
            moves.append(Move((r,c), (r+1,c-1), self.board))
      
      if c+1 <= 7:
        if self.board[r+1][c+1][0] == 'w':
          if not piece_pinned or pin_direction == (1,1):
            moves.append(Move((r,c), (r+1, c+1), self.board))
       
  def get_rook_moves(self,r,c,moves):
    piece_pinned = False
    pin_direction = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1]:
        piece_pinned = True
        pin_direction = (self.pins[i][2], self.pins[i][3])
        if self.board[r][c][1] != 'Q':
          self.pins.remove(self.pins[i])
        break
        
    directions = ((-1,0), (0,-1), (1,0), (0,1))
    enemy_color = 'b' if self.white_to_move else 'w'
    for d in directions:
      for i in range(1,8):
        send_row = r + d[0] * i
        end_col = c + d[1] * i
        if 0 <= send_row < 8 and 0 <= end_col < 8: # on board
          if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
            end_piece = self.board[send_row][end_col]
            if end_piece == '--': # empty space valid
              moves.append(Move((r,c), (send_row, end_col), self.board))
            elif end_piece[0] == enemy_color: # enemy piece valid
              moves.append(Move((r,c), (send_row, end_col), self.board))
              break
            else: # friendly piece invalid
              break
        else: # off board
          break
  
  def get_knight_moves(self,r,c,moves):
    piece_pinned = False
    pin_direction = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1] == c:
        piece_pinned = True
        pin_direction = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break
    
    knight_moves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
    ally_color = 'w' if self.white_to_move else 'b'
    for m in knight_moves:
      send_row = r + m[0]
      end_col = c + m[1]
      if 0 <= send_row < 8 and 0 <= end_col < 8:
        if not piece_pinned:
          end_piece = self.board[send_row][end_col]
          if end_piece[0] != ally_color: # empty or enemy piece
            moves.append(Move((r,c), (send_row, end_col), self.board))
          
  
  def get_bishop_moves(self,r,c,moves):
    piece_pinned = False
    pin_direction = ()
    for i in range(len(self.pins)-1,-1,-1):
      if self.pins[i][0] == r and self.pins[i][1]:
        piece_pinned = True
        pin_direction = (self.pins[i][2], self.pins[i][3])
        self.pins.remove(self.pins[i])
        break
    
    directions = ((-1,-1), (-1,1), (1,-1), (1,1))
    enemy_color = 'b' if self.white_to_move else 'w'
    for d in directions:
      for i in range(1,8):
        send_row = r + d[0] * i
        end_col = c + d[1] * i
        if 0 <= send_row < 8 and 0 <= end_col < 8: # on board
          if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
            end_piece = self.board[send_row][end_col]
            if end_piece == '--': # empty space valid
              moves.append(Move((r,c), (send_row, end_col), self.board))
            elif end_piece[0] == enemy_color: # enemy piece valid
              moves.append(Move((r,c), (send_row, end_col), self.board))
              break
            else: # friendly piece invalid
              break
        else: # off board
          break
  
  def get_queen_moves(self,r,c,moves):
    self.get_rook_moves(r,c,moves)
    self.get_bishop_moves(r,c,moves)

  def get_king_moves(self,r,c,moves):
    row_moves = (-1,-1,-1,0,0,1,1,1)
    col_moves = (-1,0,1,-1,1,-1,0,1)
    ally_color = 'w' if self.white_to_move else 'b'
    for i in range(8):
      send_row = r + row_moves[i]
      end_col = c + col_moves[i]
      if 0 <= send_row < 8 and 0 <= end_col < 8:
        end_piece = self.board[send_row][end_col]
        if end_piece[0] != ally_color: #empty or enemy
          # place king on end square check for checks
          if ally_color == 'w':
            self.white_king_location = (send_row, end_col)
          else:
            self.black_king_location = (send_row, end_col)
          in_check, pins, checks = self.check_for_pins_and_checks()
          if not in_check:
            moves.append(Move((r,c), (send_row, end_col), self.board))
          # place king back on original location
          if ally_color == 'w':
            self.white_king_location = (r,c)
          else:
            self.black_king_location = (r,c)
          
  
        
  def check_for_pins_and_checks(self):
    pins = [] # allied pin piece square and directional info (of potential check)
    checks = [] # squares where enemy is applying a check
    in_check = False
    if self.white_to_move:
      enemy_color = 'b'
      ally_color = 'w'
      start_row = self.white_king_location[0]
      start_col = self.white_king_location[1]
    else:
      enemy_color = 'w'
      ally_color = 'b'
      start_row = self.black_king_location[0]
      start_col = self.black_king_location[1]
    # check outward from king for pins and checks, keep track of pins
    directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
    for j in range(len(directions)):
      d = directions[j]
      possible_pin = () # reset possible pins
      for i in range(1,8):
        send_row = start_row + d[0] * i
        end_col = start_col + d[1] * i
        if 0 <= send_row < 8 and 0 <= end_col < 8:
          end_piece = self.board[send_row][end_col]
          if end_piece[0] == ally_color:
            if possible_pin == (): # 1st allied piece can be pinned
              possible_pin = (send_row,end_col,d[0],d[1])
            else: # 2nd allied piece, no pin or check possible in this direciton
              break
          elif end_piece[0] == enemy_color:
            type = end_piece[1]
            # orthogonally away from king and piece is a rook
            # diagonally away and piece is a bishop
            # 1 square away and diagonally and piece is pawn
            # any direction and piece is queen
            # any direction 1 square away and piece is king (this prevents illegal king moves ie moving into a piece controlled by enemy king)
            if (0 <= j <= 3 and type == 'R') or \
                  (4 <= j <= 7 and type == 'B') or \
                  (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                  (type == 'Q') or (i == 1 and type == "K"):
                if possible_pin == ():
                  in_check = True
                  checks.append((send_row, end_col, d[0], d[1])) 
                  break
                else: # piece blocking pin
                  pins.append(possible_pin)
                  break
            else: # enemy piece not applying check
              break
    
    #check for knight checks gg no re 
    knight_moves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
    for m in knight_moves:
      send_row = start_row + m[0]
      end_col = start_col + m[1]
      if 0 <= send_row < 8 and 0 <= end_col < 8:
        end_piece = self.board[send_row][end_col]
        if end_piece[0] == enemy_color and end_piece[1] == 'N':
          in_check = True
          checks.append((send_row,end_col,m[0],m[1]))    
    return in_check, pins, checks          
            
      
      
        
class castle_rights():
  def __init__(self, wks, bks, wqs, bqs):
    self.bqs = bqs
    self.wqs = wqs
    self.bks = bks
    self.wks = wks
    
    
class Move():
  
  ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                 '5': 3, '6': 2, '7': 1, '8': 0}
  rows_to_ranks = {v: k for k, v in ranks_to_rows.items()} # reverses dictionary using magic
  
  files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                 'e': 4, 'f': 5, 'g': 6, 'h': 7}
  cols_to_files = {v: k for k, v in files_to_cols.items()}
  
  # enpassant_possible passed in as optional parameter since we give it a default value 
  def __init__(self, startSq, endSq, board, enpassant_possible = False):
    self.start_row = startSq[0]
    self.start_col = startSq[1]
    self.send_row = endSq[0]
    self.end_col = endSq[1]
    self.piece_moved = board[self.start_row][self.start_col]
    self.piece_captured = board[self.send_row][self.end_col]
    #pawn promotion
    #self.promotion_choice = 'Q'
    self.is_pawn_promotion = (self.piece_moved == 'wp' and self.send_row == 0) or (self.piece_moved == 'bp' and self.send_row == 7)
      
    # en passant
    self.is_enpassant_move = enpassant_possible
    
      
    
    self.move_id = self.start_row * 1000 + self.start_col * 100 + self.send_row * 10 + self.end_col
  
  
  
  def __eq__(self, other):
    if isinstance(other,Move):
      return self.move_id == other.move_id
    return False
    
  def get_chess_notation(self):
    return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.send_row, self.end_col)
    
  
  def get_rank_file(self, r, c):
    return self.cols_to_files[c] + self.rows_to_ranks[r]