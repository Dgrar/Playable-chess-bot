from chessrules import get_all_moves, get_legal_moves, is_in_check
from board import Board

PST = {
    1: [
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        [5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
        [1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
        [0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
        [0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
        [0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
        [0.5,  1.0,  1.0, -2.0, -2.0,  1.0,  1.0,  0.5],
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
    ],
    2: [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
        [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
        [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
        [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
        [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
        [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
    ],
    3: [
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
        [-1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
        [-1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
        [-1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
        [-1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
    ],
    4: [
        [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        [0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
        [-0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [0.0,  0.0,  0.0,  0.5,  0.5,  0.0,  0.0,  0.0]
    ],
    5: [
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [-0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [0.0,   0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [-1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [-1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
    ],
    6: [
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [2.0,   2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0],
        [2.0,   3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0]
    ]
}


def get_all_legal_moves(matrix, color_to_play, last_pawn_move, visual_board):
    moves = []
    color_val = 1 if color_to_play == "white" else -1

    for row in range(8):
        for col in range(8):
            piece_val = matrix[row][col]
            if piece_val == 0 or piece_val * color_val <= 0:
                continue
            pseudo_moves = get_all_moves(piece_val, row, col, matrix, last_pawn_move, visual_board, color_to_play)
            legal_moves = get_legal_moves(pseudo_moves, row, col, matrix, last_pawn_move)
            for move in legal_moves:
                moves.append(((row, col), move))

    return moves if moves else None


def order_moves(matrix, legal_moves):
    def score_move(move):
        origin, target = move[0], move[1]
        moving_piece = abs(matrix[origin[0]][origin[1]])
        target_piece = abs(matrix[target[0]][target[1]])
        if target_piece != 0:
            return 1000 + (target_piece * 10) - moving_piece
        return 0
    return sorted(legal_moves, key=score_move, reverse=True)


def eval(matrix):
    evaluation = 0
    material_conversion = {1: 100, 2: 320, 3: 330, 4: 500, 5: 900, 6: 900000}

    for row in range(8):
        for col in range(8):
            piece = matrix[row][col]
            if piece == 0:
                continue
            piece_type = abs(piece)
            sign = 1 if piece > 0 else -1
            material_value = material_conversion[piece_type]
            if piece > 0:
                positional_value = PST[piece_type][row][col]
            else:
                positional_value = PST[piece_type][7 - row][col]
            evaluation += (material_value + positional_value) * sign

    return evaluation


def make_move(matrix, move, last_pawn_move):
    origin, target = move[0], move[1]
    piece = matrix[origin[0]][origin[1]]
    captured = matrix[target[0]][target[1]]
    ep_captured = 0
    ep_pos = None
    rook_move_data = None

    if abs(piece) == 1 and origin[1] != target[1] and captured == 0:
        ep_pos = (origin[0], target[1])
        ep_captured = matrix[ep_pos[0]][ep_pos[1]]
        matrix[ep_pos[0]][ep_pos[1]] = 0

    if abs(piece) == 6 and abs(origin[1] - target[1]) == 2:
        row = origin[0]
        if target[1] == 6:
            rook_move_data = ((row, 7), (row, 5))
        else:
            rook_move_data = ((row, 0), (row, 3))
        matrix[rook_move_data[1][0]][rook_move_data[1][1]] = matrix[rook_move_data[0][0]][rook_move_data[0][1]]
        matrix[rook_move_data[0][0]][rook_move_data[0][1]] = 0

    matrix[target[0]][target[1]] = piece
    matrix[origin[0]][origin[1]] = 0

    return captured, ep_captured, ep_pos, rook_move_data


def unmake_move(matrix, move, captured, ep_captured, ep_pos, rook_move_data):
    origin, target = move[0], move[1]
    matrix[origin[0]][origin[1]] = matrix[target[0]][target[1]]
    matrix[target[0]][target[1]] = captured

    if ep_pos:
        matrix[ep_pos[0]][ep_pos[1]] = ep_captured

    if rook_move_data:
        matrix[rook_move_data[0][0]][rook_move_data[0][1]] = matrix[rook_move_data[1][0]][rook_move_data[1][1]]
        matrix[rook_move_data[1][0]][rook_move_data[1][1]] = 0


def minimax(matrix, depth, alpha, beta, is_maximizing, last_pawn_move, visual_board):
    if depth == 0:
        return eval(matrix)

    current_color = "white" if is_maximizing else "black"
    legal_moves = get_all_legal_moves(matrix, current_color, last_pawn_move, visual_board)

    if not legal_moves:
        if is_in_check(matrix, current_color):
            return -90000 if is_maximizing else 90000
        return 0

    legal_moves = order_moves(matrix, legal_moves)

    if is_maximizing:
        max_eval = -float('inf')
        for move in legal_moves:
            captured, ep_captured, ep_pos, rook_data = make_move(matrix, move, last_pawn_move)
            score = minimax(matrix, depth - 1, alpha, beta, False, last_pawn_move, visual_board)
            unmake_move(matrix, move, captured, ep_captured, ep_pos, rook_data)
            max_eval = max(max_eval, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            captured, ep_captured, ep_pos, rook_data = make_move(matrix, move, last_pawn_move)
            score = minimax(matrix, depth - 1, alpha, beta, True, last_pawn_move, visual_board)
            unmake_move(matrix, move, captured, ep_captured, ep_pos, rook_data)
            min_eval = min(min_eval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_eval


def get_move(visual_board: Board, color_to_play, last_pawn_move, depth=1):
    current_matrix = visual_board.np_matrix
    initial_moves = get_all_legal_moves(current_matrix, color_to_play, last_pawn_move, visual_board)

    if not initial_moves:
        return None

    best_move = None
    alpha = -float('inf')
    beta = float('inf')

    if color_to_play == "white":
        best_eval = -float('inf')
        for move in initial_moves:
            captured, ep_captured, ep_pos, rook_data = make_move(current_matrix, move, last_pawn_move)
            score = minimax(current_matrix, depth - 1, alpha, beta, False, last_pawn_move, visual_board)
            unmake_move(current_matrix, move, captured, ep_captured, ep_pos, rook_data)
            if score > best_eval:
                best_eval = score
                best_move = move
            alpha = max(alpha, score)
    else:
        best_eval = float('inf')
        for move in initial_moves:
            captured, ep_captured, ep_pos, rook_data = make_move(current_matrix, move, last_pawn_move)
            score = minimax(current_matrix, depth - 1, alpha, beta, True, last_pawn_move, visual_board)
            unmake_move(current_matrix, move, captured, ep_captured, ep_pos, rook_data)
            if score < best_eval:
                best_eval = score
                best_move = move
            beta = min(beta, score)

    return best_move