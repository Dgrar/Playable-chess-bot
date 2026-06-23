import pygame
import numpy as np
from pathlib import Path
from chessrules import *

IMAGES_DIR = Path(__file__).resolve().parent.joinpath("pieces")

def move_piece(pos, visual_board, square_width, pieces, turn_holder):

    target_square_col = (pos[0] - visual_board.offset_x) // square_width
    target_square_row = (pos[1] - visual_board.offset_y) // square_width
    
    if target_square_col > 7 or target_square_col < 0: return False
    if target_square_row > 7 or target_square_row < 0: return False
    
    try:
        start_row, start_col = visual_board.selected_squares[0]
        # Evitar mover al mismo lugar
        if start_row == target_square_row and start_col == target_square_col:
            visual_board.stop_selecting()
            return False
        if not (target_square_row,target_square_col) in visual_board.selected_squares or (target_square_row,target_square_col) == (start_row,start_col):
            print("Not available")
            return False
        visual_board.move(start_row, start_col, target_square_row, target_square_col, pieces)
        return True
    except IndexError as e:
        print(e)
        return False

def starting_pos():
    # 1 peon, 2 caballo, 3 alfil, 4 torre, 5 dama, 6 rey
    pieces_row = np.array([4,2,3,5,6,3,2,4])
    pawns_row = np.ones(8)
    board = np.zeros((8,8))
    board[0] = -pieces_row
    board[1] = -pawns_row
    board[6] = pawns_row
    board[7] = pieces_row
    return board

class Piece:
    def __init__(self, value, row, column, size, board_offset_x, board_offset_y):
        self.row = row
        self.column = column
        self.size = size
        self.selected = False
        self.color = "white" if value > 0 else "black"
        
        diccionario_piezas = {1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K'}
        self.piece_type = diccionario_piezas[abs(value)]
        
        # Carga de imágenes optimizada con convert_alpha
        image_path = IMAGES_DIR.joinpath(f"{self.color}_{self.piece_type}.png")
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            # Fallback visual por si no encuentra las imágenes
            self.image = pygame.Surface((int(size*.8), int(size*.8)))
            self.image.fill((255, 0, 0) if self.color == "white" else (0, 0, 255))
            
        self.imagesize_y = int(self.size * .85)
        self.imagesize_x = int(self.size * .85 if self.piece_type != "P" else self.size * .7)
        self.image = pygame.transform.scale(self.image, (self.imagesize_x, self.imagesize_y))
        self.rect = self.image.get_rect()
        
        # Calcular posición
        padding_x = (size - self.imagesize_x) // 2
        padding_y = (size - self.imagesize_y) // 2
        self.x_pos = self.column * self.size + padding_x
        self.y_pos = self.row * self.size + padding_y
        self.rect.topleft = (board_offset_x + self.x_pos, board_offset_y + self.y_pos)

    def draw(self, surface, x, y):
        surface.blit(self.image, (x + self.x_pos, y + self.y_pos))

    def clicked(self, board,np_board):
        if len(board.selected_squares) > 0:
            self.stop_selecting(board)
        else:
            self.select(board,np_board)

    def select(self, board, np_board):
        self.selected = True
        board.select(self.row, self.column,self.get_available_moves(np_board, board))

    def stop_selecting(self, board):
        self.selected = False
        board.stop_selecting()

    def get_available_moves(self,board, board_obj):
        match self.piece_type:
            case "P":
                return pawn_move(self.color,self.row,self.column, board)
            case "N":
                return knight_move(self.color,self.row,self.column,board)
            case "B":
                return bishop_move(self.color, self.row,self.column,board)
            case "R":
                return rook_move(self.color,self.row,self.column,board)
            case "Q":
                return queen_move(self.color, self.row,self.column,board)
            case "K":
                return king_move(self.color,self.row,self.column,board, board_obj)
    
class Board(pygame.sprite.Sprite):
    def __init__(self, offset_x, offset_y, size, np_matrix, pieces):
        super().__init__()
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.square_size = size
        self.color_white = (240, 217, 181)
        self.color_black = (181, 136, 99)
        self.selected_squares = []
        self.selected_piece = 0
        self.matrix = [[None for _ in range(8)] for _ in range(8)]
        self.np_matrix = np_matrix
        
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        
        self.sincronize_np(np_matrix, pieces)

    def sincronize_np(self, np_matrix, pieces):
        pieces.clear() # ¡CRUCIAL! Vaciamos la lista vieja para evitar duplicados fantasma
        self.matrix = [[None for _ in range(8)] for _ in range(8)]
        
        for row in range(8):
            for col in range(8):
                val = int(np_matrix[row][col])
                if val != 0:
                    piece = Piece(val, row, col, self.square_size, self.offset_x, self.offset_y)
                    self.matrix[row][col] = piece
                    pieces.append(piece)

    def draw(self, surface):
        for row in range(8):
            for col in range(8):
                color = self.color_white if (row + col) % 2 == 0 else self.color_black
                rect = pygame.Rect(
                    self.offset_x + col * self.square_size, 
                    self.offset_y + row * self.square_size, 
                    self.square_size, 
                    self.square_size
                )
                pygame.draw.rect(surface, color, rect)

            if len(self.selected_squares) > 0:
                origin_square = self.selected_squares[0]
                
                for row, col in self.selected_squares:
                    if (row, col) == origin_square:
                        continue
                    
                    marker_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    center_pos = (self.square_size // 2, self.square_size // 2)
                    is_capture = self.np_matrix[row][col] != 0

                    if not is_capture:
                        pygame.draw.circle(marker_surface, (0, 200, 0, 130), center_pos, int(self.square_size * 0.18))
                    else:
                        pygame.draw.circle(marker_surface, (255, 0, 0, 140), center_pos, int(self.square_size * 0.4), width=6)

                    pos_x = self.offset_x + col * self.square_size
                    pos_y = self.offset_y + row * self.square_size
                    surface.blit(marker_surface, (pos_x, pos_y))

            for row in range(8):
                for col in range(8):
                    piece = self.matrix[row][col]
                    if piece is not None:
                        piece.draw(surface, self.offset_x, self.offset_y)

    def select(self, row, col, moves):
        self.selected_squares = [(row, col)]
        print(moves)
        if moves:
            for move in moves:
                self.selected_squares.append(move)
        self.selected_piece = self.np_matrix[row, col]

    def stop_selecting(self):
        self.selected_squares.clear()
        self.selected_piece = 0

    def move(self, start_row, start_col, end_row, end_col, pieces):
        piece_val = self.np_matrix[start_row][start_col]
        
        if abs(piece_val) == 6:
            if start_col == 4 and end_col == 6:
                self.np_matrix[start_row][5] = self.np_matrix[start_row][7]
                self.np_matrix[start_row][7] = 0.
            elif start_col == 4 and end_col == 2:
                self.np_matrix[start_row][3] = self.np_matrix[start_row][0]
                self.np_matrix[start_row][0] = 0.

        if piece_val == 6: self.white_king_moved = True
        elif piece_val == -6: self.black_king_moved = True
        elif piece_val == 4 and start_row == 7 and start_col == 0: self.white_rook_a_moved = True
        elif piece_val == 4 and start_row == 7 and start_col == 7: self.white_rook_h_moved = True
        elif piece_val == -4 and start_row == 0 and start_col == 0: self.black_rook_a_moved = True
        elif piece_val == -4 and start_row == 0 and start_col == 7: self.black_rook_h_moved = True

        self.np_matrix[start_row][start_col] = 0.
        self.np_matrix[end_row][end_col] = self.selected_piece
        self.sincronize_np(self.np_matrix, pieces)
        self.selected_squares.clear()
        self.selected_piece = 0


    def get_possible_moves(self, pos):
        row,col = pos
        moves = self.matrix[row][col].get_available_moves(self.np_matrix, self.matrix)
        
        
def main():
    pygame.init()
    square_width = 80
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    running = True
    logic_matrix = starting_pos()
    whiteTurn = True
    pieces = []
    
    visual_board = Board((SCREEN_WIDTH - square_width * 8) // 2, (SCREEN_HEIGHT - square_width * 8) // 2, square_width, logic_matrix, pieces)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                clicked_sprites = [s for s in pieces if s.rect.collidepoint(pos)]
                
                # Turno actual estructurado
                current_color = "white" if whiteTurn else "black"
                
                if clicked_sprites:
                    # Si tocamos una pieza del propio turno, la seleccionamos
                    if clicked_sprites[0].color == current_color:
                        clicked_sprites[0].clicked(visual_board, visual_board.np_matrix)
                    # Si tocamos una pieza rival y tenemos algo seleccionado, intentamos captura
                    elif visual_board.selected_piece != 0:
                        if move_piece(pos, visual_board, square_width, pieces, whiteTurn):
                            whiteTurn = not whiteTurn # Cambiar turno si el movimiento fue válido
                else:
                    # Click en casilla vacía: si hay pieza seleccionada, se mueve
                    if visual_board.selected_piece != 0:
                        if move_piece(pos, visual_board, square_width, pieces, whiteTurn):
                            whiteTurn = not whiteTurn # Cambiar turno si el movimiento fue válido

        screen.fill("black")
        visual_board.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
