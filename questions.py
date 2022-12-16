''' Модуль загрузки и интерфейса работы с вопросами / ответами
Основной функционал модуля (класса QuestData):
- загрузка вопросов и ответов из файла quest.csv в таблицу quests = pd.DataFrame;
- подготовка пула еще не отвеченных вопросов;
- случайный выбор вопроса из пула по заданному уровню сложности level;
- формирование списка вопрос, ответы в случайном порядке;
- проверка правильный ли выбран ответ на данный вопрос;
'''
import pandas as pd
import numpy as np
import os, sys


class QuestData:
    def __init__(self, filename='quest.csv', path='.\data'):
        fullname = os.path.join(path, filename)
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            self.data = None
            print(f"Файл с данными '{fullname}' не найден")
            sys.exit()
        elif filename[filename.find('.'):] == 'xlsx' \
                or filename[filename.find('.'):] == 'xls':
            self.data = pd.read_excel(fullname)
        else:
            self.data = pd.read_csv(fullname, sep=';', header=0, encoding='windows-1251')
        # self.answers_n = self.data.shape[1] - 2
        self.answers_n = sum(['answer' in name for name in self.data.columns])
        self.init_to_play()
        # np.random.seed()

    def init_to_play(self):
        if len(self.data) > 1:
            # наполняем словарь номеров неотвеченных вопросов для каждого уровня
            self.qdict = dict()
            for nom in self.data.index:
                level = self.data.loc[nom, 'level']
                if level in self.qdict:
                    self.qdict[level].append(nom)
                else:
                    self.qdict[level] = [nom]

    def choice_quest_num(self, level):
        quest_nums = self.qdict[level]
        if quest_nums:
            qnum = np.random.choice(quest_nums, 1)[0]
            quest_nums.remove(qnum)
            return qnum

    def get_next_quest(self, level):
        qlist = []
        qnum = self.choice_quest_num(level)
        print(f'выбран вопрос {qnum}')
        if qnum is not None:
            qlist = list(self.data.loc[qnum, :])[1:]
        # случайный порядок ответов
        noms = list(range(1, len(qlist)))
        noms = list(np.random.permutation(noms))
        noms = [0] + noms
        return list(np.array(qlist)[noms])

    def is_it_right(self, q, a):
        nom = self.data.index[self.data.question == q][0]
        return a == self.data.loc[nom, 'answer1']


if __name__ == '__main__':
    qdata = QuestData()
    if qdata:
        # print(qdata.data.head())
        # print(qdata.qdict)
        # print(qdata.answers_n)
        qlist = qdata.get_next_quest(level=0)
        print(qlist)
        print(qdata.qdict)
        print(qdata.is_it_right(qlist[0], qlist[1]))
        print(qdata.is_it_right(qlist[0], qlist[2]))
        print(qdata.is_it_right(qlist[0], qlist[3]))