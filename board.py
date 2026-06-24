import pygame
import numpy as np
from pathlib import Path
from chessrules import *

IMAGES_DIR = Path(__file__).resolve().parent.joinpath("pieces")

def move_piece(pos, visual_board, square_width, pieces, turn_holder, last_pawn_move):
    target_square_col = (pos[0] - visual_board.offset_x) // square_width
    target_square_row = (pos[1] - visual_board.offset_y) // square_width

    if target_square_col > 7 or target_square_col < 0: return None
    if target_square_row > 7 or target_square_row < 0: return None
    try:
        start_row, start_col = visual_board.selected_squares[0]
        if start_row == target_square_row and start_col == target_square_col:
            visual_board.stop_selecting()
            return None
        if not (target_square_row, target_square_col) in visual_board.selected_squares or (target_square_row, target_square_col) == (start_row, start_col):
            return None

        if abs(visual_board.np_matrix[start_row][start_col]) == 1:
            if visual_board.np_matrix[start_row][start_col] == 1:
                if target_square_row == 2:
                    if last_pawn_move["last_move"] == True and last_pawn_move["target_row"] == 3 and target_square_col == last_pawn_move["target_col"]:
                        visual_board.np_matrix[last_pawn_move["target_row"]][last_pawn_move["target_col"]] = 0
            else:
                if target_square_row == 5:
                    if last_pawn_move["last_move"] == True and last_pawn_move["target_row"] == 4 and target_square_col == last_pawn_move["target_col"]:
                        visual_board.np_matrix[last_pawn_move["target_row"]][last_pawn_move["target_col"]] = 0

            last_pawn_move.clear()
            last_pawn_move.update({
                "start_row": start_row,
                "target_col": target_square_col,
                "target_row": target_square_row,
                "last_move": True
            })
        else:
            last_pawn_move["last_move"] = False

        visual_board.move(start_row, start_col, target_square_row, target_square_col, pieces)
        other_color = "black" if turn_holder else "white"
        return get_game_state(visual_board.np_matrix, other_color, last_pawn_move, visual_board)
    except IndexError as e:
        print(e)
        return None


def starting_pos():
    pieces_row = np.array([4, 2, 3, 5, 6, 3, 2, 4])
    pawns_row = np.ones(8)
    board = np.zeros((8, 8))
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

        image_path = IMAGES_DIR.joinpath(f"{self.color}_{self.piece_type}.png")
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((int(size * .8), int(size * .8)))
            self.image.fill((255, 0, 0) if self.color == "white" else (0, 0, 255))

        self.imagesize_y = int(self.size * .85)
        self.imagesize_x = int(self.size * .85 if self.piece_type != "P" else self.size * .7)
        self.image = pygame.transform.scale(self.image, (self.imagesize_x, self.imagesize_y))
        self.rect = self.image.get_rect()

        padding_x = (size - self.imagesize_x) // 2
        padding_y = (size - self.imagesize_y) // 2
        self.x_pos = self.column * self.size + padding_x
        self.y_pos = self.row * self.size + padding_y
        self.rect.topleft = (board_offset_x + self.x_pos, board_offset_y + self.y_pos)

    def draw(self, surface, x, y):
        surface.blit(self.image, (x + self.x_pos, y + self.y_pos))

    def clicked(self, board, np_board, last_pawn_move):
        if len(board.selected_squares) > 0:
            self.stop_selecting(board)
        else:
            self.select(board, np_board, last_pawn_move)

    def select(self, board, np_board, last_pawn_move):
        self.selected = True
        board.select(self.row, self.column, self.get_available_moves(np_board, board, last_pawn_move))

    def stop_selecting(self, board):
        self.selected = False
        board.stop_selecting()

    def get_available_moves(self, board, board_obj, last_pawn_move):
        match self.piece_type:
            case "P": pseudo = pawn_move(self.color, self.row, self.column, board, last_pawn_move)
            case "N": pseudo = knight_move(self.color, self.row, self.column, board)
            case "B": pseudo = bishop_move(self.color, self.row, self.column, board)
            case "R": pseudo = rook_move(self.color, self.row, self.column, board)
            case "Q": pseudo = queen_move(self.color, self.row, self.column, board)
            case "K": pseudo = king_move(self.color, self.row, self.column, board, board_obj)
        return get_legal_moves(pseudo, self.row, self.column, board)


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
        pieces.clear()
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

        if piece_val == 6:    self.white_king_moved = True
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


class PromotionUI:
    def __init__(self, row, col, color, square_size, offset_x, offset_y, images_dir):
        self.row = row
        self.col = col
        self.color = color
        self.square_size = square_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.pieces = ["Q", "R", "B", "N"]
        self.values = {"Q": 5, "R": 4, "B": 3, "N": 2}
        self.active = True

        self.bg_color     = (181, 136, 99)
        self.border_color = (101,  67,  33)
        self.hover_color  = (240, 217, 181)

        self.images = {}
        cell = int(square_size * 1.3)
        self.cell = cell
        for p in self.pieces:
            path = images_dir / f"{color}_{p}.png"
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (int(cell * .82), int(cell * .82)))
            self.images[p] = img

        total_w = cell * 4 + 24
        total_h = cell + 24
        self.x = offset_x + col * square_size - total_w // 2 + square_size // 2
        self.x = max(offset_x, min(self.x, offset_x + 8 * square_size - total_w))
        self.y = offset_y + (8 * square_size - total_h) // 2
        self.w = total_w
        self.h = total_h

    def draw(self, surface):
        border_rect = pygame.Rect(self.x - 5, self.y - 5, self.w + 10, self.h + 10)
        pygame.draw.rect(surface, self.border_color, border_rect, border_radius=12)
        pygame.draw.rect(surface, self.bg_color, pygame.Rect(self.x, self.y, self.w, self.h), border_radius=10)

        mouse_pos = pygame.mouse.get_pos()
        for i, piece in enumerate(self.pieces):
            item_rect = self._item_rect(i)
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, self.hover_color, item_rect, border_radius=8)
            img = self.images[piece]
            img_x = item_rect.centerx - img.get_width() // 2
            img_y = item_rect.centery - img.get_height() // 2
            surface.blit(img, (img_x, img_y))

        for i in range(1, 4):
            x_line = self.x + 12 + i * self.cell
            pygame.draw.line(surface, self.border_color, (x_line, self.y + 8), (x_line, self.y + self.h - 8), 1)

    def _item_rect(self, index):
        return pygame.Rect(self.x + 12 + index * self.cell, self.y + 6, self.cell, self.h - 12)

    def handle_click(self, pos):
        for i, piece in enumerate(self.pieces):
            if self._item_rect(i).collidepoint(pos):
                return self.values[piece]
        return None


class GameOverUI:
    def __init__(self, state, square_size, offset_x, offset_y):
        self.state = state
        self.active = True

        self.board_w = square_size * 8
        self.board_h = square_size * 8
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.square_size = square_size

        self.panel_w = int(square_size * 5.5)
        self.panel_h = int(square_size * 3)
        self.x = offset_x + (self.board_w - self.panel_w) // 2
        self.y = offset_y + (self.board_h - self.panel_h) // 2

        self.bg_color       = (30, 18, 8)
        self.border_color   = (101, 67, 33)
        self.text_color     = (240, 217, 181)
        self.subtle_color   = (160, 120, 80)
        self.btn_color      = (181, 136, 99)
        self.btn_hover      = (210, 170, 120)
        self.btn_text_color = (30, 18, 8)

        self.font_title = pygame.font.SysFont("Georgia", int(square_size * 0.55), bold=True)
        self.font_sub   = pygame.font.SysFont("Georgia", int(square_size * 0.32))
        self.font_btn   = pygame.font.SysFont("Georgia", int(square_size * 0.3), bold=True)

        btn_w = int(square_size * 2)
        btn_h = int(square_size * 0.55)
        btn_y = self.y + self.panel_h - btn_h - int(square_size * 0.35)
        spacing = int(square_size * 0.25)
        total_btn_w = btn_w * 2 + spacing
        btn_start_x = self.x + (self.panel_w - total_btn_w) // 2

        self.btn_restart = pygame.Rect(btn_start_x, btn_y, btn_w, btn_h)
        self.btn_quit    = pygame.Rect(btn_start_x + btn_w + spacing, btn_y, btn_w, btn_h)

    def draw(self, surface):
        overlay = pygame.Surface((self.board_w, self.board_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (self.offset_x, self.offset_y))

        border_rect = pygame.Rect(self.x - 5, self.y - 5, self.panel_w + 10, self.panel_h + 10)
        pygame.draw.rect(surface, self.border_color, border_rect, border_radius=14)
        pygame.draw.rect(surface, self.bg_color, pygame.Rect(self.x, self.y, self.panel_w, self.panel_h), border_radius=12)

        sep_y = self.y + int(self.square_size * 0.08) + int(self.square_size * 1.15)
        pygame.draw.line(surface, self.border_color, (self.x + 20, sep_y), (self.x + self.panel_w - 20, sep_y), 1)

        title_text, sub_text = ("Jaque Mate", "El rey ha caído.") if self.state == "checkmate" else ("Ahogado", "Tablas por ahogado.")

        title_surf = self.font_title.render(title_text, True, self.text_color)
        sub_surf   = self.font_sub.render(sub_text, True, self.subtle_color)

        title_x = self.x + (self.panel_w - title_surf.get_width()) // 2
        title_y = self.y + int(self.square_size * 0.3)
        surface.blit(title_surf, (title_x, title_y))

        sub_x = self.x + (self.panel_w - sub_surf.get_width()) // 2
        sub_y = title_y + title_surf.get_height() + int(self.square_size * .5)
        surface.blit(sub_surf, (sub_x, sub_y))

        mouse_pos = pygame.mouse.get_pos()
        for btn, label in [(self.btn_restart, "Nueva partida"), (self.btn_quit, "Salir")]:
            color = self.btn_hover if btn.collidepoint(mouse_pos) else self.btn_color
            pygame.draw.rect(surface, color, btn, border_radius=8)
            pygame.draw.rect(surface, self.border_color, btn, width=2, border_radius=8)
            btn_surf = self.font_btn.render(label, True, self.btn_text_color)
            surface.blit(btn_surf, (btn.centerx - btn_surf.get_width() // 2, btn.centery - btn_surf.get_height() // 2))

    def handle_click(self, pos):
        if self.btn_restart.collidepoint(pos):
            return "restart"
        if self.btn_quit.collidepoint(pos):
            return "quit"
        return None


def make_board(square_width, screen_w, screen_h, pieces):
    logic_matrix = starting_pos()
    offset_x = (screen_w - square_width * 8) // 2
    offset_y = (screen_h - square_width * 8) // 2
    return Board(offset_x, offset_y, square_width, logic_matrix, pieces), offset_x, offset_y


def main():
    pygame.init()
    square_width = 80
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    pieces = []
    last_pawn_move = {"start_row": 7, "target_col": 5, "target_row": 1, "last_move": False}

    visual_board, off_x, off_y = make_board(square_width, SCREEN_WIDTH, SCREEN_HEIGHT, pieces)
    whiteTurn = True
    promotion_ui = None
    gameover_ui = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:

                if gameover_ui:
                    action = gameover_ui.handle_click(pygame.mouse.get_pos())
                    if action == "restart":
                        pieces = []
                        last_pawn_move.clear()
                        last_pawn_move.update({"start_row": 7, "target_col": 5, "target_row": 1, "last_move": False})
                        visual_board, off_x, off_y = make_board(square_width, SCREEN_WIDTH, SCREEN_HEIGHT, pieces)
                        whiteTurn = True
                        promotion_ui = None
                        gameover_ui = None
                    elif action == "quit":
                        running = False
                    continue

                if promotion_ui and promotion_ui.active:
                    value = promotion_ui.handle_click(pygame.mouse.get_pos())
                    if value is not None:
                        final_value = value if promotion_ui.color == "white" else -value
                        visual_board.np_matrix[promotion_ui.row][promotion_ui.col] = final_value
                        visual_board.sincronize_np(visual_board.np_matrix, pieces)
                        promotion_ui = None
                        whiteTurn = not whiteTurn
                    continue

                pos = pygame.mouse.get_pos()
                clicked_sprites = [s for s in pieces if s.rect.collidepoint(pos)]
                current_color = "white" if whiteTurn else "black"

                if clicked_sprites:
                    if clicked_sprites[0].color == current_color:
                        clicked_sprites[0].clicked(visual_board, visual_board.np_matrix, last_pawn_move)
                    elif visual_board.selected_piece != 0:
                        state = move_piece(pos, visual_board, square_width, pieces, whiteTurn, last_pawn_move)
                        if state is not None:
                            result = needs_promotion(visual_board.np_matrix)
                            if result:
                                row, col, color = result
                                promotion_ui = PromotionUI(row, col, color, square_width, off_x, off_y, IMAGES_DIR)
                            elif state in ("checkmate", "stalemate"):
                                gameover_ui = GameOverUI(state, square_width, off_x, off_y)
                            else:
                                whiteTurn = not whiteTurn
                else:
                    if visual_board.selected_piece != 0:
                        state = move_piece(pos, visual_board, square_width, pieces, whiteTurn, last_pawn_move)
                        if state is not None:
                            result = needs_promotion(visual_board.np_matrix)
                            if result:
                                row, col, color = result
                                promotion_ui = PromotionUI(row, col, color, square_width, off_x, off_y, IMAGES_DIR)
                            elif state in ("checkmate", "stalemate"):
                                gameover_ui = GameOverUI(state, square_width, off_x, off_y)
                            else:
                                whiteTurn = not whiteTurn

        screen.fill("black")
        visual_board.draw(screen)
        if promotion_ui:
            promotion_ui.draw(screen)
        if gameover_ui:
            gameover_ui.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()