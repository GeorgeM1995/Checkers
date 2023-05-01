import pygame
import sys
import enum

class CellValue(enum.Enum):
    EMPTY = 0
    BLACK = 1
    RED = 2
    INVALID = 3

class LogicalBoard:
    def __init__(self):
        self.board = []
        self.take_at = None
        self.player_turn = CellValue.BLACK
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


    def set_value_at(self, pos, value):
        if pos is not None:
            x, y = pos
            self.board[y][x] = value


    def check_for_take(self, x_0, y_0, x_1, y_1):
        if self.player_turn == CellValue.BLACK:
            front_right = (x_0 + 1, y_0 + 1)
            front_left = (x_0 - 1, y_0 + 1)
            y_movement = 2
            if x_1 > x_0:
                if self.value_at(front_right) == CellValue.RED:
                    self.take_at = front_right
                    return True
            if x_1 < x_0:
                if self.value_at(front_left) == CellValue.RED:
                    self.take_at = front_left
                    return True
        else:
            front_right = (x_0 + 1, y_0 - 1)
            front_left = (x_0 - 1, y_0 - 1)
            y_movement = -2
            if x_1 > x_0:
                if self.value_at(front_right) == CellValue.BLACK:
                    self.take_at = front_right
                    return True
            if x_1 < x_0:
                if self.value_at(front_left) == CellValue.BLACK:
                    self.take_at = front_left
                    return True
            return False


    def is_legal(self, start_pos, end_pos):
        x_0, y_0 = start_pos
        x_1, y_1 = end_pos
        dx = x_1 - x_0
        dy = y_1 - y_0
        self.take_at = None
        if start_pos == end_pos:
            print('false1')
            return False
        if self.value_at(end_pos) == self.next_player():
            print('false2')
            return False
        if self.value_at(end_pos) == self.player_turn:
            print('false3')
            return False
        if dy * self.player_direction(self.player_turn) < 0:
            return False
        if dy > 2 or dy < -2:
            return False
        if self.check_for_take(x_0, y_0, x_1, y_1):
            print('take check true')
            return True
        if dx > 1 or dx < -1:
            return False
        if dy > 1 or dy < -1:
            return False
        print('end loop true')
        return True



    def perform_move(self, start_pos, end_pos):
        if self.is_legal(start_pos, end_pos):
            self.set_value_at(start_pos, CellValue.EMPTY)
            self.set_value_at(end_pos, self.player_turn)

            if self.take_at:
                self.set_value_at(self.take_at, CellValue.EMPTY)
            self.take_at = None
            self.player_turn = self.next_player()
            return True
        return False

    def next_player(self):
        if self.player_turn == CellValue.BLACK:
            return CellValue.RED
        else:
            return CellValue.BLACK

    def player_direction(self, player):
        if player == CellValue.BLACK:
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
        self.img_red_normal = pygame.image.load('graphics/red_normal.png')

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
                    if logical_board.value_at(click_pos) == logical_board.player_turn:
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
