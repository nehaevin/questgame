''' Модуль отрисовки игрового поля
Основной функционал модуля:
- загрузка картинки из файла для последующей вставки в спрайты;
- реализация функционала кнопки отрисовки картинок: класс AnimatedCell;
- реализация функционала кнопки управления: класс ControlCell;
- создание и инициализация игровой доски: класс Board;
'''

import pygame
import numpy as np
import os, sys


# Изображение не получится загрузить
# без предварительной инициализации pygame
def load_image(name, colorkey=None, path='.\images'):
    fullname = os.path.join(path, name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class AnimatedCell(pygame.sprite.Sprite):
    """ квадратная ячейка размером cell_size x cell_size выводит в рамку
    список картинок, т.е. перебирает картинки в порядке их следования
    """
    def __init__(self, cell_sprites, cell_size, x, y, color='white'):
        """ инициация размера окошка и его левого угла
        :param cell_sprites: контейнер спрайтов
        :param cell_size: размер окна вывода
        :param x, y: - координаты левого угла окна
        :param color: цвет рамки и начального текста, для красоты
        """
        super().__init__(cell_sprites)
        self.radius = cell_size // 2
        self.x, self.y = x, y
        self.color = pygame.Color(color)
        self.rect = pygame.Rect(x, y, cell_size, cell_size)
        self.set_frames([self.draw_text('Аватар')])

    def draw_text(self, txt):
        # сгенерируем текст txt в картинку
        font = pygame.font.Font(None, 30)
        text = font.render(txt, True, self.color)
        return text

    def set_frames(self, images_list):
        ''' масштабировать и добавить картинку в середину соты
        :param images_list: картинка в виде surface (холста)
        '''
        if images_list is None:
            return
        self.frames = []
        for image in images_list:
            self.frames.append(pygame.transform.scale(image, (2 * self.radius - 2,
                                                              2 * self.radius - 2)))
        self.cur_frame = 0 # указатель текущей картинки
        self.image = self.frames[self.cur_frame]

    def update(self, mouth_pos):
        if mouth_pos:
            pass
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class ControlCell(pygame.sprite.Sprite):
    def __init__(self, control_sprites, radius, x, y, color='white'):
        super().__init__(control_sprites)
        self.radius = radius
        self.center = x, y
        self.color = color
        self.points = ((2 * radius, radius),
                       (int(1.5 * radius), int(radius * (1 - np.sqrt(3) / 2))),
                       (int(0.5 * radius), int(radius * (1 - np.sqrt(3) / 2))),
                       (0, radius),
                       (int(0.5 * radius), int(radius * (1 + np.sqrt(3) / 2))),
                       (int(1.5 * radius), int(radius * (1 + np.sqrt(3) / 2)))
                       )
        self.rect = pygame.Rect(x - radius, y - radius, 2 * radius, 2 * radius)
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        self.contents = ['Start']
        self.status = 0
        self.update_content()
        self.draw()

    def set_control(self, contents):
        ''' Программа инициации контроля над кнопкой; она устанавливает два параметра
        :param contents: список содержания (текст или картинка) в зависимости от статуса
        '''
        self.contents = contents
        self.status = 0
        self.update_content()
        self.draw()

    def add_text(self, text=None):
        yandex_color = pygame.Color("#ffcc00")
        font = pygame.font.Font(None, 50)
        if text is None:
            rendered_text = font.render(' ', True, yandex_color)
        else:
            rendered_text = font.render(text, True, yandex_color)
        # вставим текст посредине
        self.content = pygame.transform.scale(rendered_text,
                                              (int(np.sqrt(3) * self.radius),
                                               self.radius))

    def add_image(self, image):
        ''' масштабировать и добавить картинку в середину соты
        :param image: картинка в виде surface (холста)
        '''
        if image is None:
            self.added_image = None
            return
        self.content = pygame.transform.scale(image,
                                              (int(np.sqrt(3) * self.radius),
                                               int(np.sqrt(3) * self.radius)))

    def update_content(self):
        content = self.contents[self.status]
        if isinstance(content, str):
            self.add_text(content)
        else:
            self.add_image(content)

    def run_command(self, status):
        # status - это новый статус
        if not (0 <= status < len(self.contents)):
            return
        self.status = status
        self.update_content()
        self.draw()

    def draw_content(self):
        if self.content:
            pic_x = self.radius - self.content.get_width() // 2
            pic_y = self.radius - self.content.get_height() // 2
            self.image.blit(self.content, (pic_x, pic_y))

    def draw(self):
        pygame.draw.circle(self.image, pygame.Color(self.color),
                           (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, pygame.Color("white"),
                           (self.radius, self.radius), self.radius, 1)
        pygame.draw.lines(self.image, pygame.Color('brown'), True, self.points, 3)
        self.draw_content()

    def next_status(self):
        self.status = (self.status + 1) % len(self.contents)
        self.update_content()

    def check_mouse(self, mouse_pos):
        x, y = self.center
        if (mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2 <= self.radius ** 2:
            return True
        else:
            return False

    def update(self, mouse_pos):
        if mouse_pos is not None and self.check_mouse(mouse_pos):
            self.next_status()
        self.draw()

class Board:
    def __init__(self, textmat, colormat, left=20, top=20, cell_size=50):
        ''' создание поля, состоящего из шестиугольных сот с метками
        :param textmat, colormat: - матрицы названий и цветов сот по горизонтали и вертикали
        :param left, top: отступы слева и сверху от границы основного холста
        :param cell_size: размер соты (диаметр соты)
        '''
        self.redcar_image = load_image("redcar.png", -1)
        self.bluecar_image = load_image("bluecar.jpg", -1)
        self.texts = np.array(textmat)
        self.colors = np.array(colormat)
        self.ncols = len(textmat[0])
        self.nrows = len(textmat)
        self.radius = cell_size // 2
        # значения по умолчанию
        self.middle_n = (self.ncols - 1) / 2
        self.left = left + self.radius
        self.bottom = top + self.radius * (2 * self.nrows - 1 + self.middle_n)

        # создадим группу, содержащую все спрайты ячейки
        self.cell_sprites = pygame.sprite.Group()
        self.cells = [[ControlCell(self.cell_sprites, self.radius,
                            *self.get_pos(row, col), self.colors[row, col])
                       for col in range(self.ncols)] for row in range(self.nrows)]
        images_row = [self.redcar_image, self.redcar_image, 'grey',
                      self.bluecar_image, self.bluecar_image]
        images = np.array([images_row for _ in range(self.nrows)])
        '''
        commands = {'init': {'from': -1, 'to': 0},
                    'go_in': {'from': 0, 'to': 1},
                    'go_out': {'from': 1, 'to': 2}}
                    '''
        for row in range(self.nrows):
            for col in range(self.ncols):
                contents = [self.texts[row, col], images[row, col], 'passed']
                self.cells[row][col].set_control(contents)

    # определить координаты левого верхнего угла ячейки по ее положению на доске
    def get_pos(self, row, col):
        # row, col: ряд и колонка ячейки на доске
        pos_x = int(self.left + col * np.sqrt(3) * self.radius)
        pos_y = int(self.bottom - self.radius * (2 * row + abs(col - self.middle_n)))
        return pos_x, pos_y


if __name__ == '__main__':
    pygame.init()
    size = width, height = 500, 650
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Инициализация игры')
    fps = 10  # количество кадров в секунду
    clock = pygame.time.Clock()

    # создаем поле игры 5 на 5
    txt_names = ['S', 'M', 'L', 'XL', 'W']
    clr_names = ['#D0A0A088', '#D0A0A088', 'grey', '#A0A0D088', '#A0A0D088']
    nrows, ncols = len(txt_names), 5
    texts = [[txt_names[row]] * ncols for row in range(nrows)]
    colors = [clr_names for _ in range(nrows)]
    board = Board(texts, colors, cell_size=100)
    board.cell_sprites.update(None)

    running = True
    while running:
        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.cell_sprites.update(event.pos)

        # формирование кадра
        screen.fill((150, 150, 150))
        board.cell_sprites.draw(screen)
        # смена кадра
        pygame.display.flip()
        # временная задержка
        clock.tick(fps)

    pygame.quit()
