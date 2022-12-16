""" Данный модуль содержит описание основного класса игры
Функционал класса:
- инициация группы спрайтов "поле игры";
- инициация группы спрайтов "доска квеста игры";
- инициация группы спрайтов "информационное поле игры";
- создание агентов команд игроков;
- инициация игры;
- проверка условия завершения игры;
- организация игрового цикла;
- завершение игры
"""

import pygame
from sotes import load_image, AnimatedCell, ControlCell, Board
from quest_screen import TextCell, QuestBoard
from questions import QuestData
from emotions import ImagesData
from sounds import SoundData

emo = {'norm': 0, 'wrong': 2, 'smile': 3, 'quest': 1}


class InfoBoard:
    def __init__(self, headtext, left=10, top=5, step_x=110, cell_size=160):
        """ создание поля, состоящего из шестиугольных сот с метками
        :param headtext: - заголовок игры
        :param left, top: отступы слева и сверху от границы основного холста
        :param step_x, cell_size: шаг по х между сотами и размер соты (диаметр соты)
        """
        self.left = left
        self.top = top
        self.step_x = step_x
        self.radius = cell_size // 2

        # создадим группу, содержащую все спрайты ячейки
        self.info_sprites = pygame.sprite.Group()
        # параметры группы по умолчанию
        face_color, res_color, move_color, once_color = '#5090BB80', '#AA50AA80', 'grey', '#50AA5080'

        # заголовки
        self.head1_sprite = TextCell(self.info_sprites, left, top, w=490, h=35,
                                     fontsize=40, color='brown', foncolor='#FFD30050')
        self.head1_sprite.add_text(headtext)
        self.head2_sprite = TextCell(self.info_sprites, 650, top, w=150, h=35,
                                     fontsize=40, color='brown', foncolor=move_color)
        self.head2_sprite.add_text('Чей ход')

        # ---- спрайты отображения состояния игры ----
        # спрайт отображения эмоций героя игры
        info_radius, step_x, step_y = self.radius, self.step_x, 55
        x1, y1 = step_x, step_y
        self.face_sprite = AnimatedCell(self.info_sprites, 2*info_radius, x1, y1, color=face_color)
        tanja_image = load_image("initface.jpg", -1)
        self.face_sprite.set_frames([tanja_image])

        # создание контрольного спрайта
        x1 += step_x + 3*info_radius
        y1 += info_radius
        self.res_sprite = ControlCell(self.info_sprites, info_radius, x1, y1, res_color)
        contents = ['Start', 'Вопрос', '.???.', 'Ой-ёй-ёй', 'ВЕРНО!', '!ПОБЕДА!']
        self.res_sprite.set_control(contents)

        # создание спрайта визуализации очередности хода
        x1 += step_x + 2*info_radius
        self.move_sprite = ControlCell(self.info_sprites, info_radius, x1, y1, move_color)
        contents = ['1-й игрок', '2-й игрок']
        self.move_sprite.set_control(contents)


class Game:
    def init_players(self):
        """ создание агентов команд игроков """
        redcar_image = load_image("redcar.png", -1)
        bluecar_image = load_image("bluecar.jpg", -1)
        players_state = {0: [0, 1], 1: [0, 3]}
        players_images = [redcar_image, bluecar_image]
        return players_state, players_images

    def _init_board_(self):
        """ создание поля игры 5х5 """
        txt_names = ['S', 'M', 'L', 'XL', 'V']
        clr_names = ['#D0A0A088', '#D0A0A088', 'grey', '#A0A0D088', '#A0A0D088']
        nrows, ncols = len(txt_names), 5
        texts = [[txt_names[row]] * ncols for row in range(nrows)]
        colors = [clr_names for _ in range(nrows)]
        board = Board(texts, colors, left=500, top=200, cell_size=100)
        board.cell_sprites.update(None)
        return board

    def __init__(self, gamehead='Вспомнить ВСЕ вместе с Таней', filename='quest.csv',
                 datapath='.\data', imagepath='.\emotions'):
        self.headtext = gamehead
        # создаем объект для работы с вопросами
        self.qdata = QuestData(filename, datapath)
        # создаем объект для работы с картинками эмоций
        self.emotions = ImagesData(path=imagepath)
        # создаем объект для работы со звуками
        self.sounds = SoundData()
        # инициируем игроков
        self.players_state, self.players_images = self.init_players()
        self.player_n = 0
        # инициируем доски игры
        self.board = self._init_board_()
        # разместим машинки игроков на старте
        state0 = self.players_state[0]
        state1 = self.players_state[1]
        self.board.cells[state0[0]][state0[1]].next_status()
        self.board.cells[state1[0]][state1[1]].next_status()
        self.board.cell_sprites.update(None)
        # инициируем доску вопроса/ответов
        self.question = ['ЗДЕСЬ БУДЕТ ВОПРОС', 'Здесь будет ответ №1',
                         'Здесь будет ответ №2', 'Здесь будет ответ №3']
        self.questboard = self._init_questboard_()
        self.choice = 0  # пока не выбрали ответ
        # инициируем доску контроля / информации
        self.infoboard = self._init_infoboard_()
        # настраиваем поле очередности хода
        self.infoboard.move_sprite.set_control(self.players_images)
        # настраиваем поле результата
        contents = ['Start', 'Вопрос', '.???.', 'Ой-ёй-ёй', 'ВЕРНО!', '!ПОБЕДА!']
        self.infoboard.res_sprite.set_control(contents)
        self.sounds.play_sound(6)

    def _init_questboard_(self):
        ''' Создаем доску для отображения вопроса '''
        questboard = QuestBoard(self.question, left=30, top=270, width=400, head_height=50, height=110)
        questboard.quest_sprites.update(None)
        return questboard

    def _init_infoboard_(self):
        ''' Создаем доску для отображения вопроса '''
        infoboard = InfoBoard(self.headtext)
        infoboard.info_sprites.update(None)
        return infoboard

    def change_state(self, mouse_pos):
        ''' проверка - какая кнопка была нажата и в каком состоянии находится
        в зависимости от этого изменяем состояние спрайтов
        эту функцию вызываем после апдейта доски вопроса и
        вместо апдейта доски управления
        '''
        level, col = self.players_state[self.player_n]
        # проверяем нажатие кнопки управления
        if self.infoboard.res_sprite.check_mouse(mouse_pos):
            # была нажата кнопка управления / результата
            ctrl_state = self.infoboard.res_sprite.status
            if ctrl_state == 0: # 'Start'
                # задаем вопрос для данного уровня
                self.question = self.qdata.get_next_quest(level=level)
                self.questboard.add_question(self.question)
                self.questboard.quest_sprites.update(None)
                # переводим кнопку управления и эмоций в следующее состояние
                self.infoboard.res_sprite.run_command(1)
                tanja_image = self.emotions.get_image(level, emo['quest'])
                self.infoboard.face_sprite.set_frames(tanja_image)
                # включаем музон
                self.sounds.play_sound(1)
            elif ctrl_state == 2: # '.???.'
                # проверяем, что верно и меняем инфо статус соответственно
                if self.qdata.is_it_right(self.question[0], self.question[self.choice]):
                    tanja_image = self.emotions.get_image(level, emo['smile'])
                    self.infoboard.face_sprite.set_frames(tanja_image)
                    self.infoboard.res_sprite.run_command(4) # верно!
                    # включаем соответствующий музон
                    self.sounds.play_sound(4)
                else:
                    tanja_image = self.emotions.get_image(level, emo['wrong'])
                    self.infoboard.face_sprite.set_frames(tanja_image)
                    self.infoboard.res_sprite.run_command(3) # НЕверно!
                    # включаем соответствующий музон
                    self.sounds.play_sound(3)
            elif ctrl_state in [3, 4]: # не/верно
                # меняем состояние игрового поля и проверяем завершение игры
                delta_row, delta_col = 0, 0
                if ctrl_state == 3: # неверно - косой ход
                    # оцениваем необходимое смещение по столбцу
                    delta_col = ((1 + col - self.player_n) % 2) * 2 - 1
                    if (delta_col + self.player_n) == 1 or (delta_col - self.player_n) == -2:
                        delta_row = 1
                elif ctrl_state == 4: # верно - прямой ход
                    delta_row = 1
                # меняем состояние двух полей
                newlevel, newcol = level + delta_row, col + delta_col
                self.board.cells[level][col].next_status()
                self.board.cells[newlevel][newcol].next_status()
                self.players_state[self.player_n] = [newlevel, newcol]
                # очищаем доску вопроса
                self.questboard.add_question([' ', ' ', ' ', ' '])
                self.questboard.quest_sprites.update(None)
                self.choice = 0
                # проверяем условие завершение игры
                if newlevel == self.board.nrows - 1:
                    # Виктория!
                    self.infoboard.res_sprite.run_command(5)
                    # включаем соответствующий музон
                    self.sounds.play_sound(5)
                else:
                    # меняем состояние кнопки хода
                    self.player_n = (self.player_n + 1) % 2
                    self.infoboard.move_sprite.next_status()
                    # меняем кнопку управления
                    self.infoboard.res_sprite.run_command(0)
                    # меняем эмоцию
                    tanja_image = self.emotions.get_image(newlevel, emo['norm'])
                    self.infoboard.face_sprite.set_frames(tanja_image)
                    # включаем соответствующий музон
                    self.sounds.play_sound(0)

        elif (self.questboard.get_answernum() > 0) and \
                self.infoboard.res_sprite.status == 1:
            # была нажата кнопка ответа в состоянии вопроса
            self.choice = self.questboard.get_answernum()
            # делаем переход к следующему состоянию инфо кнопок
            tanja_image = self.emotions.get_image(level, emo['quest'])
            self.infoboard.face_sprite.set_frames(tanja_image)
            # меняем кнопку управления
            self.infoboard.res_sprite.run_command(2)
            # включаем соответствующий музон
            self.sounds.play_sound(2)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 800
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Игра')
    fps = 10 # количество кадров в секунду
    clock = pygame.time.Clock()

    # создаем объект для реализации игры
    # считываем название игры, если есть
    try:
        f = open('.\data\game_head.txt')
        game_head = f.read().strip('/n').rstrip()
        f.close()
        game_head = game_head[:30]
        game = Game(game_head)
    except:
        game = Game()

    # Запускаем основной цикл игры
    running = True
    while running:
        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.questboard.quest_sprites.update(event.pos)
                game.change_state(event.pos)
                game.board.cell_sprites.update(None)

    # формирование кадра
        screen.fill((150, 150, 150))
        game.infoboard.info_sprites.update(None)
        game.questboard.quest_sprites.draw(screen)
        game.board.cell_sprites.draw(screen)
        game.infoboard.info_sprites.draw(screen)

        # смена кадра
        pygame.display.flip()
        # временная задержка
        clock.tick(fps)

    pygame.quit()

