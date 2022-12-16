''' Модуль загрузки и интерфейса работы со звуками, отражающими состояние игры
Любой рабочий файл звука должен иметь имя вида:  name_state.*
номер state будет использоваться для доступа к звукам
- state соответствуют видам состояний игры (см. состояние кнопки управления игрой)

Основной функционал модуля:
- загрузка списка звуковых файлов из папки path в список filelist файлов;
- подготовка списка файлов в соответствии с состояниями
- проигрыш звукового объекта указанное кол-во секунд по параметру state;

'''
import numpy as np
import os
import pygame


class SoundData:
    def __init__(self, path='.\sounds'):
        ''' Чтение файлов из папки path; в папке могут быть только звучки и папки '''
        self.path = path
        file_list = os.listdir(path)
        file_list = [x for x in file_list if os.path.isfile(os.path.join(path, x))]
        self.filelist = [x for x in file_list if self.get_state(x) is not None]
        if self.filelist:
            self.init_to_game()

    def get_state(self, filename):
        name, extname = filename.split('.')
        try:
            _, state = name.split('_')
            state = int(state)
            return state
        except:
            return None

    def init_to_game(self):
        # определяем максимальные индексы строк и столбцов по именам
        self.access = np.zeros(len(self.filelist), dtype=np.int16)
        # наполняем массив номеров звуков в зависимости от индексов
        for nom, filename in enumerate(self.filelist):
            state = self.get_state(filename)
            self.access[state] = nom

    def play_sound(self, state):
        filename = self.filelist[self.access[state]]
        fullname = os.path.join(self.path, filename)
        pygame.mixer.music.load(fullname)
        pygame.mixer.music.play()


if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 850
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Игра')
    screen.fill('blue')

    sound_data = SoundData()
    state = 0
    print(sound_data.filelist)
    print(sound_data.access)
    sound_data.play_sound(state)

    running = True
    while running:
        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                state = (state + 1) % 6
                sound_data.play_sound(state)

        # смена кадра
        pygame.display.flip()