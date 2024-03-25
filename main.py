import random
import pygame

from geometry import Point, Vector, make_vector, intersect

color_white = pygame.Color(255, 255, 255)
color_black = pygame.Color(0, 0, 0)
color_red = pygame.Color(255, 0, 0)
color_green = pygame.Color(0, 255, 0)
color_dark_green = pygame.Color(0, 150, 0)
color_light_green = pygame.Color(100, 255, 100)
color_lighter_green = pygame.Color(120, 255, 120)
color_blue = pygame.Color(0, 0, 255)
color_grey_green = pygame.Color(70, 150, 70)
color_light_gray = pygame.Color(150, 150, 150)
color_dark_gray = pygame.Color(70, 70, 70)


class Button:
    def __init__(self, x, y, width, height, text='Button', font=None, enabled=True):
        self.enabled = enabled
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.text = text

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def draw(self, surface):
        pygame.draw.rect(surface=surface,
                         color=color_grey_green if self.enabled else color_dark_gray,
                         rect=(self.x, self.y, self.width, self.height),
                         border_radius=5,
                         width=0)

        pygame.draw.rect(surface=surface,
                         color=color_lighter_green if self.enabled else color_light_gray,
                         rect=(self.x, self.y, self.width, self.height),
                         border_radius=5,
                         width=3)

        if self.text != '':
            font = pygame.font.SysFont(self.font, 40)
            text = font.render(self.text,
                               1,
                               color_lighter_green if self.enabled else color_light_gray)
            surface.blit(text,
                         (self.x + (self.width // 2 - text.get_width() // 2),
                          self.y + (self.height // 2 - text.get_height() // 2)))

    def mouse_is_over(self, pos):
        if not self.enabled:
            return False
        x, y = pos
        if self.x < x < self.x + self.width:
            if self.y < y < self.y + self.height:
                return True
        return False


class Game:
    cell_size = 50

    inner_line_thickness = 1
    border_line_thickness = 5
    pocket_radius = 20
    ball_radius = 18
    intersections_radius = 10

    intersection_color = color_light_green
    target_color = color_red

    buttons_height = 40
    buttons_width = 160

    def __init__(self, width, height, caption='My Game', font=None):
        self.game_stage = 'select_aim'
        self.scores = 0
        self.hit_it = None
        self.ball_in_pocket = None
        self.intersect_points = []
        self.board_corners = None
        self.board_sides = None
        self.aim_position = None
        self.aim_coordinates = None
        self.boll_coordinates = None
        self.boll_position = None
        self.hit_path_len = None
        self.pocket_coordinates = None
        self.height_in_cells = None
        self.width_in_cells = None
        self.intersections_coordinates = {}
        self.board_y = None
        self.board_x = None
        self.board_height = None
        self.board_width = None
        self.width = width
        self.height = height
        size = width, height
        pygame.init()
        self.font = font
        self.surface = pygame.display.set_mode(size)
        pygame.display.set_caption(caption)

        self.hit_button = Button((self.width - (self.buttons_width * 2)) // 3,
                                 self.height - self.buttons_height - 20,
                                 self.buttons_width,
                                 self.buttons_height,
                                 'Hit it!')
        self.new_button = Button((self.width - (self.buttons_width * 2)) // 3 * 2 + self.buttons_width,
                                 self.height - self.buttons_height - 20,
                                 self.buttons_width,
                                 self.buttons_height,
                                 'Next')

        self.startup_game(*self.get_random_game_parameters())

    def get_random_game_parameters(self):
        """
        Запускает новый раунд игры со случайными параметрами
        :return: ширина, высота игрового поля в клетках, позиция шара в клетках
        """
        width_in_cells = random.randint(5, 10)
        height_in_cells = random.randint(5, 10)
        boll_position = (random.randint(1, width_in_cells - 1), random.randint(1, height_in_cells - 1))
        return width_in_cells, height_in_cells, boll_position

    def startup_game(self, width_in_cells, height_in_cells, boll_position):
        """
        Запуск новой игры с новыми параметрами игрового поля
        :param width_in_cells: ширина игрового поля в клеточках
        :param height_in_cells: высота игрового поля в клеточках
        :param boll_position: позиция шара
        :return: None
        """
        self.width_in_cells = width_in_cells
        self.height_in_cells = height_in_cells
        self.boll_position = boll_position
        self.board_width = (self.cell_size * width_in_cells +
                            self.inner_line_thickness * (width_in_cells - 1) )
        self.board_height = (self.cell_size * height_in_cells +
                             self.inner_line_thickness * (height_in_cells - 1))
        self.board_x, self.board_y = ((self.width - self.board_width) // 2, (self.height - self.board_height) // 2)
        self.board_corners = [Point((self.board_x, self.board_y)),  # left top
                              Point((self.board_x + self.board_width, self.board_y)),  # right top
                              Point((self.board_x, self.board_y + self.board_height)),  # left bottom
                              Point((self.board_x + self.board_width, self.board_y + self.board_height))]  # rth bottom
        self.board_sides = [((self.board_corners[0], self.board_corners[1]), (0, 1)),  # top
                            ((self.board_corners[0], self.board_corners[2]), (1, 0)),  # left
                            ((self.board_corners[1], self.board_corners[3]), (1, 0)),  # right
                            ((self.board_corners[2], self.board_corners[3]), (0, 1))]  # bottom
        self.intersections_coordinates = {}
        for x in range(1, width_in_cells):
            coordinate_x = self.board_x + x * (self.cell_size + self.inner_line_thickness)
            for y in range(1, height_in_cells):
                coordinate_y = self.board_y + y * (
                        self.cell_size + self.inner_line_thickness)
                self.intersections_coordinates[(x, y)] = Point((coordinate_x, coordinate_y))
        self.boll_coordinates = self.intersections_coordinates[self.boll_position]
        self.pocket_coordinates = ((self.board_x, self.board_y),
                                   (self.board_x + self.board_width, self.board_y),
                                   (self.board_x, self.board_y + self.board_height),
                                   (self.board_x + self.board_width, self.board_y + self.board_height))
        self.aim_coordinates = None
        self.aim_position = None
        self.intersect_points = []
        self.ball_in_pocket = None
        self.hit_it = None
        self.hit_path_len = None
        self.hit_button.enable()
        self.game_stage = 'select_aim'

    def fill(self, color=color_black):
        """
        Закрашиваем игровое поле
        :param color: цвет (по умолчанию черный)
        :return: None
        """
        self.surface.fill(color)

    def draw_dashed_line(self, color, start_pos: Point, end_pos: Point, width=1, dash_length=10):
        """
        Отрисовка пунктирной линии
        :param color: цвет линии
        :param start_pos: начальная позиция
        :param end_pos: конечная позиция
        :param width: толщина линии
        :param dash_length: длина черты
        :return: None
        """
        origin = Point(start_pos)
        target = Point(end_pos)
        displacement = target - origin
        length = displacement.length()
        slope = displacement / length

        for index in range(0, length // dash_length, 2):
            start = origin + (slope * index * dash_length)
            end = origin + (slope * (index + 1) * dash_length)
            pygame.draw.line(self.surface, color, start.get(), end.get(), width)

    def draw_hit_lines(self):
        """
        Отображение траектории шара
        :return: None
        """
        if self.hit_it:
            prev_point = self.boll_coordinates
            hit_path_len = self.hit_path_len
            draw_full_lines = []
            for i, intersect_point in enumerate(self.intersect_points):
                line_len = Vector((prev_point, intersect_point)).length()
                if line_len <= hit_path_len:
                    # рисуем целиком
                    pygame.draw.line(surface=self.surface,
                                     color=pygame.Color(i * 50, i * 50, 255 - i * 50),
                                     start_pos=prev_point,
                                     end_pos=intersect_point,
                                     width=3)
                    hit_path_len -= line_len
                    draw_full_lines.append(True)
                else:
                    # рисуем часть линии
                    start_pos, end_pos = make_vector(prev_point, intersect_point, hit_path_len)
                    pygame.draw.line(surface=self.surface,
                                     color=pygame.Color(i * 50, i * 50, 255 - i * 50),
                                     start_pos=start_pos,
                                     end_pos=end_pos,
                                     width=3)
                    draw_full_lines.append(False)
                    break
                prev_point = intersect_point

            if all(draw_full_lines):
                if self.game_stage == 'animation':
                    if self.ball_in_pocket:
                        self.scores += 5
                    else:
                        self.scores -= 1
                self.game_stage = 'after_animation'

            self.hit_path_len = (self.hit_path_len + 10) % 100000

    def draw_board(self):
        """
        Отрисовка игрового поля
        :return: None
        """
        # рисуем вертикальные линии
        for x in range(1, self.width_in_cells):
            coordinate_x = self.intersections_coordinates[(x, 1)].x
            pygame.draw.line(self.surface,
                             color=color_green,
                             start_pos=(coordinate_x, self.board_y),
                             end_pos=(coordinate_x, self.board_y + self.board_height)
                             )

        # рисуем горизонтальные линии
        for y in range(1, self.height_in_cells):
            coordinate_y = self.intersections_coordinates[(1, y)].y
            pygame.draw.line(surface=self.surface,
                             color=color_green,
                             width=self.inner_line_thickness,
                             start_pos=(self.board_x, coordinate_y),
                             end_pos=(self.board_x + self.board_width, coordinate_y)
                             )

        # рисуем границы бильярдного стола
        pygame.draw.rect(surface=self.surface,
                         color=color_green,
                         width=self.border_line_thickness,
                         rect=(self.board_x - self.border_line_thickness,
                               self.board_y - self.border_line_thickness,
                               self.board_width + self.border_line_thickness * 2,
                               self.board_height + self.border_line_thickness * 2)
                         )

        # рисуем лузы
        for coordinates in self.pocket_coordinates:
            pygame.draw.circle(surface=self.surface,
                               color=color_green,
                               radius=self.pocket_radius,
                               center=coordinates)

        # рисуем точку прицеливания и линию от шара до точки прицеливания
        if not self.hit_it:
            if self.aim_position:
                # рисуем линию от шара до точки прицеливания (если она определена)
                self.draw_dashed_line(color=color_white,
                                      start_pos=self.boll_coordinates,
                                      end_pos=self.aim_coordinates,
                                      width=4)
                # рисуем точку прицеливания (если она определена)
                pygame.draw.circle(surface=self.surface,
                                   color=self.target_color,
                                   radius=self.intersections_radius,
                                   center=self.aim_coordinates)

        # рисуем кружки на месте пересечения линий (возможные цели для нанесения удара)
        for coordinates in self.intersections_coordinates.values():
            pygame.draw.circle(surface=self.surface,
                               color=self.intersection_color,
                               radius=self.intersections_radius,
                               center=coordinates)

        # рисуем траекторию удара по шару
        self.draw_hit_lines()

        # рисуем шар
        pygame.draw.circle(surface=self.surface,
                           color=color_white,
                           radius=self.ball_radius,
                           center=self.boll_coordinates)

        # рисуем элементы управления
        self.hit_button.draw(surface=self.surface)
        self.new_button.draw(surface=self.surface)

        # выводим текст
        font = pygame.font.SysFont(self.font, 40)
        text = font.render('Yandex billiard game', 1, color_lighter_green)
        self.surface.blit(text, ((self.width // 2 - text.get_width() // 2), 10))
        font = pygame.font.SysFont(self.font, 30)
        text = font.render('Select an aiming point and press [Hit it!] button', 1, color_dark_green)
        self.surface.blit(text, ((self.width // 2 - text.get_width() // 2), 50))
        text = font.render('Press [Next] button for the next round', 1, color_dark_green)
        self.surface.blit(text, ((self.width // 2 - text.get_width() // 2), 75))

        # выводим количество набранных очков
        font = pygame.font.SysFont(self.font, 20)
        text = font.render('Yours scores', 1, color_dark_green)
        self.surface.blit(text, ((self.width // 2 - text.get_width() // 2), self.height - 30))
        font = pygame.font.SysFont(self.font, 80)
        text = font.render(str(self.scores), 1, color_red)
        self.surface.blit(text, ((self.width // 2 - text.get_width() // 2), self.height - 80))

        # выводим надпись win или fate
        if self.game_stage == 'after_animation':
            if self.ball_in_pocket:
                font = pygame.font.SysFont(self.font, 200)
                text = font.render('Win!', 1, color_red)
                self.surface.blit(text, ((self.width // 2 - text.get_width() // 2),
                                         (self.height // 2 - text.get_height() // 2)))
            else:
                font = pygame.font.SysFont(self.font, 20)
                text = font.render("It's fate, dude!", 1, color_red)
                self.surface.blit(text, ((self.width // 2 - text.get_width() // 2), self.height - 100))

    def hit_intersection(self, pos):
        """
        Возвращает True в случае, если указатель мыши на пересечении
        :param pos: позиция указателя мыши
        :return: возвращает True в случае, если указатель мыши на пересечении или False
        """
        return self.surface.get_at(pos) == self.intersection_color

    def set_aim(self, pos):
        """
        Выбирает одно из пересечений как метку для прицеливания
        :param pos:
        :return:
        """
        for position, coordinates in self.intersections_coordinates.items():
            if (abs(pos[0] - coordinates.x) <= self.intersections_radius and
                    abs(pos[1] - coordinates.y) <= self.intersections_radius):
                self.aim_coordinates = coordinates
                self.aim_position = position
                self.hit_it = False
                self.hit_button.enable()
                self.game_stage = 'select_aim'
                return coordinates

    def check_near_corner(self, point):
        """
        Проверяет, не находится ли шар рядом с лузой
        :param point:
        :return:
        """
        delta = 2
        for corner in self.board_corners:
            if abs(corner.x - point.x) <= delta and abs(corner.y - point.y) <= delta:
                return corner

    def calculate_hit_lines(self):
        """
        Расчет траектории движения шара после удара в заданном направлении
        :return: None
        """
        vector_len = 10000000

        self.intersect_points = []
        self.ball_in_pocket = False

        start_point = self.boll_coordinates
        end_point = self.aim_coordinates
        point1, end_point = make_vector(start_point, end_point, vector_len)

        start_side = None
        for i in range(5):
            vector = make_vector(start_point, end_point, vector_len)
            key = None
            intersect_point = None
            for side, key in self.board_sides:
                if side != start_side:
                    intersect_point = intersect(side, vector)
                    if intersect_point:
                        start_side = side
                        self.intersect_points.append(intersect_point)
                        self.ball_in_pocket = self.check_near_corner(intersect_point)
                        break
            if self.ball_in_pocket:
                break
            if intersect_point:
                d_x = intersect_point.x - end_point.x
                d_y = intersect_point.y - end_point.y
                start_point = intersect_point
                end_point = Point((end_point.x + key[0] * d_x * 2, end_point.y + key[1] * d_y * 2))

    def hit(self):
        """
        Запускает удар по шару в заданном направлении
        :return: None
        """
        if self.aim_position:
            self.hit_it = True
            self.hit_path_len = 0
            self.hit_button.disable()
            self.game_stage = 'animation'


if __name__ == '__main__':
    width = height = 800
    game = Game(width, height, 'Just a simple game')
    clock = pygame.time.Clock()
    fps = 60

    running = True
    while running:
        # отрисовка и изменение свойств объектов
        game.fill()
        game.draw_board()

        # цикл приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.hit_intersection(event.pos):
                    game.set_aim(event.pos)
                    game.calculate_hit_lines()
                if game.hit_button.mouse_is_over(event.pos):
                    game.hit()
                if game.new_button.mouse_is_over(event.pos):
                    game.startup_game(*game.get_random_game_parameters())
        pygame.display.flip()  # смена кадра
        # временная задержка
        clock.tick(fps)

    pygame.quit()
