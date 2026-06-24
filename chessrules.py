import numpy as np

def is_move_valid(pos) -> bool:
    return 0<=pos<=7
        
def is_square_attacked(target_row, target_col, defender_color, np_matrix):
    enemy_color = "black" if defender_color == "white" else "white"
    
    # 1. Comprobar ataques de peones enemigos
    pawn_direction = 1 if enemy_color == "white" else -1
    for dc in [-1, 1]:
        r, c = target_row + pawn_direction, target_col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            # Los peones se representan con valor absoluto 1
            if abs(np_matrix[r][c]) == 1 and ((np_matrix[r][c] > 0 and enemy_color == "white") or (np_matrix[r][c] < 0 and enemy_color == "black")):
                return True

    # 2. Comprobar ataques de caballos enemigos (Valor absoluto 2)
    knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in knight_offsets:
        r, c = target_row + dr, target_col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            if abs(np_matrix[r][c]) == 2 and ((np_matrix[r][c] > 0 and enemy_color == "white") or (np_matrix[r][c] < 0 and enemy_color == "black")):
                return True

    # 3. Comprobar ataques de rayos en direcciones ortogonales (Torres=4, Damas=5) y reyes en corto (6)
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
                break # Una pieza propia o enemiga bloquea la línea de visión lejana
            r += dr
            c += dc
            step += 1

    # 4. Comprobar ataques de rayos en direcciones diagonales (Alfiles=3, Damas=5) y reyes en corto (6)
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
                break # Bloqueo de línea de visión
            r += dr
            c += dc
            step += 1

    return False

def is_in_check(board, defender_color):
    row, col = np.unravel_index(np.argmax(board), board.shape)
    return is_square_attacked(row, col, defender_color, board)


def pawn_move(color, row, col, board,last_pawn_move): # Last Move en un dict/string de Forma, row, col
    moves = []
    
    # Dirección: Negro baja (1), Blanco sube (-1)
    direction = 1 if color == "black" else -1
    starting_row = 1 if color == "black" else 6
    next_row = row + direction
    
    # ---- AVANCES ----
    if is_move_valid(next_row):
        # Avanzar 1 casilla
        if board[next_row][col] == 0:
            moves.append((next_row, col))
            
            # Avanzar 2 casillas (Solo desde fila inicial y si la casilla está libre)
            two_rows = row + direction * 2
            if row == starting_row and board[two_rows][col] == 0:
                moves.append((two_rows, col))
                
        for i in [-1, 1]:
            capture_col = col + i

            if 0 <= capture_col <= 7:
                other_piece = board[next_row][capture_col]
                # Si no está vacía y el signo matemático es opuesto (es enemigo)
                if other_piece != 0 and (other_piece * direction) > 0:
                    moves.append((next_row, capture_col))
    # Al paso
    
    row_start = last_pawn_move["start_row"]
    row_end = last_pawn_move["target_row"]
    col_end = last_pawn_move["target_col"]
    last_move = last_pawn_move["last_move"]
    if row == (3.5 + direction *0.5):
        if last_move:
            if direction == -1:
                abs(col_end - col)
                print(row_start)
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
    
    # 1. Movimientos normales del Rey (8 direcciones)
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