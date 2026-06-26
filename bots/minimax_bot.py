from chessrules import get_all_moves, get_legal_moves
from board import Board
import random
import copy

def get_all_legal_moves(matrix, color_to_play, last_pawn_move, visual_board):
    moves = []
    color_val = 1 if color_to_play == "white" else -1
    
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            piece_val = matrix[row][col]
            
            if piece_val == 0: 
                continue
                
            if piece_val * color_val < 0:
                continue
            
            pseudo_moves = get_all_moves(abs(piece_val), row, col, matrix, last_pawn_move, visual_board, color_to_play)
            legal_moves = get_legal_moves(pseudo_moves, row, col, matrix, last_pawn_move)
            
            for move in legal_moves:
                moves.append(((row, col), move))
            
    return moves if moves else None

def eval(matrix):
    evaluation = 0
    material_conversion = {1: 10, 2: 32, 3: 33, 4: 50, 5: 90, 6: 90000}
    
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            piece = matrix[row][col]
            if piece == 0:
                continue
            sign = 1 if piece > 0 else -1
            evaluation += material_conversion[abs(piece)] * sign
            
    return evaluation

def simulate_move(matrix, move):
    matrix_copy = copy.deepcopy(matrix)
    origin, target = move[0], move[1]
    matrix_copy[target[0]][target[1]] = matrix_copy[origin[0]][origin[1]]
    matrix_copy[origin[0]][origin[1]] = 0
    return matrix_copy

def minimax(matrix, depth, is_maximizing, last_pawn_move, visual_board):
    if depth == 0:
        return eval(matrix)
        
    current_color = "white" if is_maximizing else "black"
    legal_moves = get_all_legal_moves(matrix, current_color, last_pawn_move, visual_board)
    
    if not legal_moves:
        return -80000 if is_maximizing else 80000

    if is_maximizing:
        max_eval = -float('inf')
        for move in legal_moves:
            new_matrix = simulate_move(matrix, move)
            score = minimax(new_matrix, depth - 1, False, last_pawn_move, visual_board)
            max_eval = max(max_eval, score)
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            new_matrix = simulate_move(matrix, move)
            score = minimax(new_matrix, depth - 1, True, last_pawn_move, visual_board)
            min_eval = min(min_eval, score)
        return min_eval

def get_move(visual_board: Board, color_to_play, last_pawn_move, depth=2):
    current_matrix = visual_board.np_matrix
    initial_moves = get_all_legal_moves(current_matrix, color_to_play, last_pawn_move, visual_board)
    
    if not initial_moves:
        return None

    best_move = None
    
    if color_to_play == "white":
        best_eval = -float('inf')
        for move in initial_moves:
            new_matrix = simulate_move(current_matrix, move)
            score = minimax(new_matrix, depth - 1, False, last_pawn_move, visual_board)
            
            if score > best_eval:
                best_eval = score
                best_move = move
    else:
        best_eval = float('inf')
        for move in initial_moves:
            new_matrix = simulate_move(current_matrix, move)
            score = minimax(new_matrix, depth - 1, True, last_pawn_move, visual_board)
            
            if score < best_eval:
                best_eval = score
                best_move = move
                
    return best_move