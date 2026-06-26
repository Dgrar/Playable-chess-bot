import numpy as np

def is_move_valid(pos) -> bool:
    return 0<=pos<=7
        
def is_square_attacked(target_row, target_col, defender_color, np_matrix):
    enemy_color = "black" if defender_color == "white" else "white"
    
    pawn_direction = 1 if enemy_color == "white" else -1
    for dc in [-1, 1]:
        r, c = target_row + pawn_direction, target_col + dc
        if 0 <= r < 8 and 0 <= c < 8:

            if abs(np_matrix[r][c]) == 1 and ((np_matrix[r][c] > 0 and enemy_color == "white") or (np_matrix[r][c] < 0 and enemy_color == "black")):
                return True

   
    knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in knight_offsets:
        r, c = target_row + dr, target_col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            if abs(np_matrix[r][c]) == 2 and ((np_matrix[r][c] > 0 and enemy_color == "white") or (np_matrix[r][c] < 0 and enemy_color == "black")):
                return True

    orthogonal_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in orthogonal_directions:
        r, c = target_row + dr, target_col + dc
        step = 1
        while 0 <= r < 8 and 0 <= c < 8:
            val = np_matrix[r][c]
            if val != 0:
                is_enemy = (val > 0 and enemy_color == "white") or (val < 0 and enemy_color == "black")
                if is_enemy and (abs(val) in [4, 5] or (abs(val) == 6 and step == 1)):
                    return True
                break 
            r += dr
            c += dc
            step += 1

    diagonal_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in diagonal_directions:
        r, c = target_row + dr, target_col + dc
        step = 1
        while 0 <= r < 8 and 0 <= c < 8:
            val = np_matrix[r][c]
            if val != 0:
                is_enemy = (val > 0 and enemy_color == "white") or (val < 0 and enemy_color == "black")
                if is_enemy and (abs(val) in [3, 5] or (abs(val) == 6 and step == 1)):
                    return True
                break 
            r += dr
            c += dc
            step += 1

    return False

def get_legal_moves(moves, row_start, col_start, board, last_pawn_move=None):
    legal = []
    piece_value = board[row_start, col_start]
    color = "white" if piece_value > 0 else "black"

    if color == "white":
        king_row, king_col = np.unravel_index(np.argmax(board), board.shape)
    else:
        king_row, king_col = np.unravel_index(np.argmin(board), board.shape)

    is_king = abs(piece_value) == 6

    for move in moves:
        row, col = move

        # Guardar estado
        captured = board[row][col]
        ep_captured = 0
        ep_row = -1

        # Aplicar
        board[row_start][col_start] = 0
        board[row][col] = piece_value

        # En passant
        if abs(piece_value) == 1 and col != col_start and captured == 0:
            ep_row = row_start
            ep_captured = board[row_start][col]
            board[row_start][col] = 0

        check_row = row if is_king else king_row
        check_col = col if is_king else king_col

        if not is_square_attacked(check_row, check_col, color, board):
            legal.append(move)

        # Deshacer
        board[row_start][col_start] = piece_value
        board[row][col] = captured
        if ep_row != -1:
            board[ep_row][col] = ep_captured

    return legal

def is_in_check(board, color):
    if color == "white":
        king_row, king_col = np.unravel_index(np.argmax(board), board.shape)
    else:
        king_row, king_col = np.unravel_index(np.argmin(board), board.shape)
    return is_square_attacked(king_row, king_col, color, board)

def get_all_moves(piece, row, col, board, last_pawn_move, board_obj, color):
    abs_piece = abs(piece)
    if abs_piece == 1: return pawn_move(color, row, col, board, last_pawn_move)
    elif abs_piece == 2: return knight_move(color, row, col, board)
    elif abs_piece == 3: return bishop_move(color, row, col, board)
    elif abs_piece == 4: return rook_move(color, row, col, board)
    elif abs_piece == 5: return queen_move(color, row, col, board)
    elif abs_piece == 6: return king_move(color, row, col, board, board_obj)
    return []

def get_game_state(board, color, last_pawn_move, board_obj):
    value = 1 if color == "white" else -1

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece * value <= 0:
                continue
            pseudo = get_all_moves(piece, row, col, board, last_pawn_move, board_obj, color)
            if get_legal_moves(pseudo, row, col, board, last_pawn_move):
                return "ongoing"

    return "checkmate" if is_in_check(board, color) else "stalemate"

def needs_promotion(board):
    for col in range(8):
        if board[0][col] == 1:
            return (0, col, "white")
        if board[7][col] == -1:
            return (7, col, "black")
    return None

def pawn_move(color, row, col, board,last_pawn_move):
    moves = []
    
 
    direction = 1 if color == "black" else -1
    starting_row = 1 if color == "black" else 6
    next_row = row + direction
    

    if is_move_valid(next_row):
       
        if board[next_row][col] == 0:
            moves.append((next_row, col))
            
            
            two_rows = row + direction * 2
            if row == starting_row and board[two_rows][col] == 0:
                moves.append((two_rows, col))
                
        for i in [-1, 1]:
            capture_col = col + i

            if 0 <= capture_col <= 7:
                other_piece = board[next_row][capture_col]
                
                if other_piece != 0 and (other_piece * direction) > 0:
                    moves.append((next_row, capture_col))
    
    row_start = last_pawn_move["start_row"]
    row_end = last_pawn_move["target_row"]
    col_end = last_pawn_move["target_col"]
    last_move = last_pawn_move["last_move"]
    if row == (3.5 + direction *0.5):
        if last_move:
            if direction == -1:
                abs(col_end - col)
                if row_start == 1 and row_end == 3:
                    if abs(col_end - col) == 1:
                        moves.append((next_row, col_end))
            else:
                if row_start == 6 and row_end == 4:
                    if abs(col_end - col) == 1:
                        moves.append((next_row, col_end))
        
         
    return moves

def king_move(color, row, col, board, board_obj):
    moves = []
    value = -1 if color == "black" else 1
    

    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0: 
                continue
            move_row = row + i
            move_col = col + j
            if is_move_valid(move_row) and is_move_valid(move_col):
                if board[move_row][move_col] * value <= 0:
                    if not is_square_attacked(move_row, move_col, color, board):
                        moves.append((move_row, move_col))
                    

    if not is_square_attacked(row, col, color, board):
        if color == "white" and row == 7: 
            if not board_obj.white_king_moved:

                if not board_obj.white_rook_h_moved and board[7][5] == 0 and board[7][6] == 0:
                    if not is_square_attacked(7, 5, color, board) and not is_square_attacked(7, 6, color, board):
                        moves.append((7, 6))

                if not board_obj.white_rook_a_moved and board[7][1] == 0 and board[7][2] == 0 and board[7][3] == 0:
                    if not is_square_attacked(7, 3, color, board) and not is_square_attacked(7, 2, color, board):
                        moves.append((7, 2))
        
        elif color == "black" and row == 0: 
            if not board_obj.black_king_moved:
                if not board_obj.black_rook_h_moved and board[0][5] == 0 and board[0][6] == 0:
                    if not is_square_attacked(0, 5, color, board) and not is_square_attacked(0, 6, color, board):
                        moves.append((0, 6))
                if not board_obj.black_rook_a_moved and board[0][1] == 0 and board[0][2] == 0 and board[0][3] == 0:
                    if not is_square_attacked(0, 3, color, board) and not is_square_attacked(0, 2, color, board):
                        moves.append((0, 2))
    return moves

def knight_move(color, row, col, board):
    moves = []
    value = 1 if color=="white" else -1
    for i in [-2,2]:
        for j in [-1,1]:
            move_row = row + i
            move_col = col + j
            if is_move_valid(move_row) and is_move_valid(move_col):
                if board[move_row][move_col] * value <= 0:
                    moves.append((move_row,move_col))
    for i in [-1,1]:
        for j in [-2,2]:
            move_row = row + i
            move_col = col + j
            if is_move_valid(move_row) and is_move_valid(move_col):
                if board[move_row][move_col] * value <= 0:
                    moves.append((move_row,move_col))
    return moves

def bishop_move(color, row, col, board):
    moves = []

    value = 1 if color == "white" else -1
    

    direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    for df, dc in direcciones:
        paso = 1
        while True:
            next_row = row + (df * paso)
            next_col = col + (dc * paso)
            
            if not (0 <= next_row <= 7 and 0 <= next_col <= 7):
                break
                
            destino = board[next_row][next_col]
            
            if destino == 0:
                moves.append((next_row, next_col))
            
            else:
                if (destino * value) < 0:
                    moves.append((next_row, next_col))
                break 
            
            paso += 1 
    
    return moves

def rook_move(color, row, col, board):
    moves = []

    value = 1 if color == "white" else -1
    
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for df, dc in direcciones:
        paso = 1
        while True:
            next_row = row + (df * paso)
            next_col = col + (dc * paso)
            
            if not (0 <= next_row <= 7 and 0 <= next_col <= 7):
                break
                
            destino = board[next_row][next_col]
            
            if destino == 0:
                moves.append((next_row, next_col))
            
            else:
                if (destino * value) < 0:
                    moves.append((next_row, next_col))
                break 
            
            paso += 1 
    
    return moves

def queen_move(color, row, col, board):

    moves = bishop_move(color, row, col, board)
    for move in rook_move(color, row,col,board):
        moves.append(move)
    return moves