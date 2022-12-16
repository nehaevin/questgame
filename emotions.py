''' Модуль загрузки и интерфейса работы с картинками лиц - эмоций игры
Любой рабочий файл картинки должен иметь имя вида:  name_row_col.*
номера row, col будут использоваться для доступа к картинкам
- строки соответствуют строкам игрового поля (уровню, level)
- столбцы соответствуют видам эмоций: 0 - норм, 1 - радость, 2 - испуг, ...

Основной функционал модуля (класса ImagesData):
- загрузка картинок лиц из папки path в список imagelist;
- подготовка двумерного массивы np.array доступа к картинкам;
- получение картинки по параметрам (row, col);

'''
import numpy as np
import os
import pygame


class ImagesData:
    def __init__(self, path='.\emotions'):
        ''' Чтение файлов из папки path; в папке могут быть только картинки и папки '''
        self.image_dict = self.load_images_from_dir_to_dict(path)
        # формируем список папок для анимации
        file_list = os.listdir(path)
        dir_list = [x for x in file_list if os.path.isdir(os.path.join(path, x))]
        dir_list = [x for x in dir_list if self.get_rowcol(x) is not None]
        if dir_list:
            for dirname in dir_list:
                row_col = self.get_rowcol(dirname)
                self.image_dict[row_col] = self.load_images_from_dir_to_list(os.path.join(path, dirname))

    def get_rowcol(self, name):
        namelist = name.split('.')
        if len(namelist) > 1:
            name, extname = namelist
        else:
            name = namelist[0]
        try:
            _, row, col = name.split('_')
            row, col = int(row), int(col)
            return row, col
        except:
            return None

    def get_order(self, name):
        namelist = name.split('.')
        if len(namelist) > 1:
            name, extname = namelist
        else:
            name = namelist[0]
        try:
            _, order = name.split('-')
            order = int(order)
            return order
        except:
            return None

    def load_images_from_dir_to_list(self, path):
        ''' Чтение файлов из папки path; читаются как картинки только файлы,
        название которых имеет вид "name_order.*"; здесь order показывает очередность
        анимации картинок
        '''
        # получаем и фильтруем список файлов
        file_list = os.listdir(path)
        file_list = [x for x in file_list if os.path.isfile(os.path.join(path, x))]
        file_list = [x for x in file_list if self.get_order(x) is not None]
        # формируем список картинок из отобранных файлов
        imagelist = []
        for filename in file_list:
            fullname = os.path.join(path, filename)
            image = pygame.image.load(fullname)
            image = image.convert()
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
            imagelist.append(image)
        return imagelist

    def load_images_from_dir_to_dict(self, path):
        ''' Чтение файлов из папки path; читаются как картинки только файлы,
        название которых имеют вид "name_row_col.ext" '''
        imagedict = {}
        # получаем и фильтруем список файлов
        file_list = os.listdir(path)
        file_list = [x for x in file_list if os.path.isfile(os.path.join(path, x))]
        filelist = [x for x in file_list if self.get_rowcol(x) is not None]
        # формируем список картинок из отобранных файлов
        for filename in filelist:
            row_col = self.get_rowcol(filename)
            fullname = os.path.join(path, filename)
            image = pygame.image.load(fullname)
            image = image.convert()
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
            imagedict[row_col] = [image]
        return imagedict

    def get_image(self, row, col):
        return self.image_dict[(row, col)]


if __name__ == '__main__':
    pygame.init()
    size = width, height = 1000, 850
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Игра')
    screen.fill('white')

    imdata = ImagesData()
    if imdata:
        print(imdata.filelist)
        print(imdata.access)
        image = imdata.get_image(0, 1)
        screen.blit(image, (100, 10))

    running = True
    while running:
        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # смена кадра
        pygame.display.flip()



