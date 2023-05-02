import pygame
import sys
import enum

class CellValue(enum.Enum):
    EMPTY = 0
    BLACK = 1
    RED = 2
    INVALID = 3
    BLACK_KING = 4
    RED_KING = 5

class Player(enum.Enum):
    BLACK = 0
    RED = 1

class LogicalBoard:
    def __init__(self):
        self.board = []
        self.take_at = None
        self.player_turn = Player.BLACK
        for y in range (8):
            row = []
            for x in range(8):
                if x % 2 != y % 2:
                    if y < 3:
                        row.append(CellValue.BLACK)
                    elif y < 5:
                        row.append(CellValue.EMPTY)
                    else:
                        row.append(CellValue.RED)
                else:
                    row.append(CellValue.INVALID)
            self.board.append(row)
        print(self.board)

    def value_at(self, pos):
        if pos is not None:
            x, y = pos
            return self.board[y][x]

    def player_owns_square(self, player, pos):
        if self.value_at(pos) == CellValue.BLACK or self.value_at(pos) == CellValue.BLACK_KING:
            return True
        if self.value_at(pos) == CellValue.RED or self.value_at(pos) == CellValue.RED_KING:
            return True
        return False



    def set_value_at(self, pos, value):
        if pos is not None:
            x, y = pos
            self.board[y][x] = value

    def king_check(self,end_pos):
        x_1, y_1 = end_pos
        if self.player_turn == Player.BLACK:
            if y_1 >= 7:
                self.set_value_at(end_pos, CellValue.BLACK_KING)
        if self.player_turn == Player.RED:
            if y_1 <= 0:
                self.set_value_at(end_pos, CellValue.RED_KING)




    def check_for_take(self, start_pos, end_pos):
        x_0, y_0 = start_pos
        x_1, y_1 = end_pos
        dy = y_1 - y_0
        front_right = (x_0 + 1, y_0 + 1)
        front_left = (x_0 - 1, y_0 + 1)
        back_right = (x_0 + 1, y_0 - 1)
        back_left = (x_0 - 1, y_0 - 1)
        if dy == 2 or dy == -2:
            if x_1 > x_0 and y_1 > y_0:
                if self.player_owns_square(self.next_player, front_right):
                    self.take_at = front_right
                    return self.take_at
            if x_1 < x_0 and y_1 > y_0:
                if self.player_owns_square(self.next_player, front_left):
                    self.take_at = front_left
                    return self.take_at
            if x_1 > x_0 and y_1 < y_0:
                if self.player_owns_square(self.next_player, back_right):
                    self.take_at = back_right
                    return self.take_at
            if x_1 < x_0 and y_1 < y_0:
                if self.player_owns_square(self.next_player, back_left):
                    self.take_at = back_left
                    return self.take_at
        return None


    def is_legal(self, start_pos, end_pos):
        x_0, y_0 = start_pos
        x_1, y_1 = end_pos
        dx = x_1 - x_0
        dy = y_1 - y_0
        self.take_at = None
        if start_pos == end_pos:
            return False
        if self.player_owns_square(self.player_turn, end_pos) or self.player_owns_square(self.next_player(), end_pos):
            return False
        if self.value_at(start_pos) == CellValue.BLACK or self.value_at(start_pos) == CellValue.RED:
            if dy * self.player_direction(self.player_turn) < 0:
                return False
        if dy > 2 or dy < -2:
            return False
        if self.check_for_take(start_pos, end_pos):
            return True
        if dx > 1 or dx < -1:
            return False
        if dy > 1 or dy < -1:
            return False
        return True



    def perform_move(self, start_pos, end_pos):
        if self.is_legal(start_pos, end_pos):
            self.set_value_at(end_pos, self.value_at(start_pos))
            self.set_value_at(start_pos, CellValue.EMPTY)
            self.king_check(end_pos)

            if self.take_at != None:
                self.set_value_at(self.take_at, CellValue.EMPTY)
            self.take_at = None
            self.player_turn = self.next_player()
            return True
        return False

    def next_player(self):
        if self.player_turn == Player.BLACK:
            return Player.RED
        else:
            return Player.BLACK

    def player_direction(self, player):
        if player == Player.BLACK:
            return 1
        else:
            return -1

    def game_over(self):
        return False



class GraphicalBoard:
    def __init__(self, resolution, cell_size):
        self.img_background = pygame.image.load('graphics/game_board.png')
        self.rect_background = self.img_background.get_rect(center=(resolution / 2, resolution / 2))
        self.squares = {}
        self.img_black_normal = pygame.image.load('graphics/black_normal.png')
        self.img_black_king = pygame.image.load('graphics/black_king.png')
        self.img_red_normal = pygame.image.load('graphics/red_normal.png')
        self.img_red_king = pygame.image.load('graphics/red_king.png')

        # shift_x, shift_y to center the rect on the square
        img_width, img_height = self.img_red_normal.get_size()
        shift_x = (cell_size - img_width) / 2
        shift_y = (cell_size - img_height) / 2
        for y in range(8):
            top_pos = 2 + y * cell_size + shift_y
            for x in range(8):
                left_pos = 2 + x * cell_size + shift_x
                if x % 2 != y % 2:
                    space = pygame.Rect(left_pos, top_pos, cell_size, cell_size)
                    self.squares[(x, y)] = space
        print(f'Graphical board: {self.squares}')

    def rect_at(self, screen_pos):
        for pos, square in self.squares.items():
            if square.collidepoint(screen_pos):
                return pos
        return None

    def draw(self, screen, logical_board):
        screen.blit(self.img_background, self.rect_background)
        for pos, square_graphic in self.squares.items():
            square_logic = logical_board.value_at(pos)
            img = None
            if square_logic == CellValue.BLACK:
                img = self.img_black_normal
            elif square_logic == CellValue.RED:
                img = self.img_red_normal
            elif square_logic == CellValue.BLACK_KING:
                img = self.img_black_king
            elif square_logic == CellValue.RED_KING:
                img = self.img_red_king
            if img is not None:
                screen.blit(img, square_graphic)

def main():
    clock = pygame.time.Clock()
    resolution = 900
    cell_size = 111
    screen = pygame.display.set_mode((resolution, resolution))

    logical_board = LogicalBoard()
    graphical_board = GraphicalBoard(resolution, cell_size)

    start_pos = None

    while not logical_board.game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_click = pygame.mouse.get_pos()
                if start_pos is None:

                    click_pos = graphical_board.rect_at(mouse_click)
                    if logical_board.player_owns_square(logical_board.player_turn, click_pos):
                        start_pos = click_pos
                else:
                    end_pos = graphical_board.rect_at(mouse_click)
                    if end_pos is not None:
                        logical_board.perform_move(start_pos, end_pos)
                    start_pos = None

        graphical_board.draw(screen, logical_board)
        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()
