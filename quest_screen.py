''' Модуль отрисовки поля вопросов
Основной функционал модуля:
- реализация функционала поля отрисовки текста вопросов/ответов: класс TextCell;
- реализация функционала доски вопросов/ответов: класс QuestBoard;
'''

import pygame
import numpy as np


class TextCell(pygame.sprite.Sprite):
    def __init__(self, text_sprites, x, y, w, h, fontsize=30, color='white', foncolor='black'):
        super().__init__(text_sprites)
        self.left, self.top = x, y
        self.width = w
        self.height = h
        self.fontsize = fontsize
        self.colors = [pygame.Color(color), pygame.Color(foncolor)]
        self.status = 0
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        self.text = ''
        self.image.fill(pygame.Color(foncolor))
        self.draw_text()

    def draw_text(self, dX=5, dY=1):
        font = pygame.font.Font(None, self.fontsize)
        # формируем список строк, умещающихся в заданную ширину
        if not self.text:
            lines = ['        ']
        else:
            words = self.text.split()
            lines = []
            while words:
                word_n = 0
                line = ' '.join(words[:word_n + 1])
                while font.render(line, True, pygame.Color('white')).get_width() <= self.width:
                    word_n += 1
                    if word_n == len(words): break
                    line = ' '.join(words[:word_n + 1])
                lines.append(' '.join(words[:word_n]))
                words = words[word_n:]

        # построчно выводим текст, начиная с использованием отступов dX, dY
        text_x, text_y = dX, dY
        foncolor_n = (self.status + 1) % 2
        self.image.fill(self.colors[foncolor_n])
        for line in lines:
            text = font.render(line, True, self.colors[self.status])
            self.image.blit(text, (text_x, text_y))
            text_y += text.get_height() + dY

    def add_text(self, text):
        ''' масштабировать и добавить картинку в середину соты
        :param text: текст в виде строки
        '''
        self.text = text

    def next_status(self):
        self.status = (self.status + 1) % 2

    def update(self, mouse_pos):
        if mouse_pos is not None and self.rect.collidepoint(mouse_pos):
            self.next_status()
        self.draw_text()


class QuestBoard:
    def __init__(self, texts, left=20, top=20, width=400,
                 head_height = 100, height=100, font_size=30):
        ''' создание поля бокса вопроса(заголовка) и боксов с ответами с контролем выбора
        :param texts: - список вопроса и ответов; вопрос - в начале
        :param left, top: отступы слева и сверху от границы основного холста
        :param width, head_height, height: ширина и высота бокса вопроса и ответов
        :param font_size: размер шрифта в вопросах и ответах
        '''
        self.texts = texts
        # цвет шрифта вопроса, шрифта ответов и фона
        self.colors = ['red', 'white', 'darkgrey']
        self.left = left
        self.top = top
        self.width = width
        self.head_height = head_height
        self.height = height
        self.font_size = font_size
        # параметры по умолчанию - отступы и интервалы между ответами
        self.dx, self.dy = 10, 20

        # создадим группу, содержащую все спрайты квеста
        self.quest_sprites = pygame.sprite.Group()
        # создадим все спрайты
        self.cells = [TextCell(self.quest_sprites, *self.get_pos(0),
                               width, head_height, font_size,
                               self.colors[0], self.colors[2])]
        self.cells += [TextCell(self.quest_sprites, *self.get_pos(row),
                                width, height, font_size,
                                self.colors[1], self.colors[2])
                       for row in range(1, len(texts))]
        self.add_question(texts)

    # разместить вопрос и ответы в ячейках поля
    def add_question(self, texts):
        for row, cell in enumerate(self.cells):
            cell.status = 0
            cell.add_text(texts[row])

    # определить координаты левого верхнего угла ячейки по ее положению на доске
    def get_pos(self, row):
        # row: номер текста, 0 - номер вопроса
        pos_x = self.left
        pos_y = self.top
        if row:
            pos_x += self.dx
            pos_y += self.head_height + 10 + self.dy
            if row > 1:
                pos_y += (row -1) * (self.dy + self.height)
        return pos_x, pos_y

    def get_answernum(self):
        # узнать какая кнопка ответа была нажата или 0
        num = 0
        for n, cell in enumerate(self.cells):
            if cell.status != 0:
                num = n
        return num


if __name__ == '__main__':
    pygame.init()
    size = width, height = 500, 800
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Игра')
    fps = 10 # количество кадров в секунду
    clock = pygame.time.Clock()

    # поле 5 на 5
    texts = ['Вопрос 1. Сколько лет Татьяне?',
             'Ответ 1. Двадцать пять или значительно меньше',
             'Ответ 2. Тридцать пять или немного меньше',
             'Ответ 3. Сорок пять или немного больше']
    questboard = QuestBoard(texts, head_height=60, height=120)
    questboard.quest_sprites.update(None)

    running = True
    while running:
        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                questboard.quest_sprites.update(event.pos)

        # формирование кадра
        screen.fill((150, 150, 150))
        questboard.quest_sprites.draw(screen)
        # смена кадра
        pygame.display.flip()
        # временная задержка
        clock.tick(fps)

    pygame.quit()


