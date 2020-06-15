# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import urllib.request
import random

from functions import get_authenticated_service
import sketchingTool
from gpdialog import GPDialog


class MainWindow(QtWidgets.QMainWindow, sketchingTool.Ui_SketchingTool):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # загружаем все настройки, которые только смогли здесь задать
        QtCore.QCoreApplication.setOrganizationName('ShiroSayuri')
        QtCore.QCoreApplication.setApplicationName('Sketching Tool')
        self.settings = QtCore.QSettings()
        self.window().resize(self.settings.value('size')) if self.settings.contains('size') else (1095, 844)
        self.window().move(self.settings.value('pos')) if self.settings.contains('pos') else (0, 0)
        self.pictureTime.setText(self.settings.value('timer')) if self.settings.contains('timer') else None

        # мешаем пользователю вводить что угодно кроме цифр
        self.pictureTime.setValidator(QtGui.QIntValidator())
        # провязываем события на функции
        self.actionLocal.triggered.connect(self.browse_folder)
        self.actionLog_In_Google_Photos.triggered.connect(self.gp_auth)
        self.actionGoogle_Photo.triggered.connect(self.from_google_photo)
        self.playButton.clicked.connect(self.play_button)
        self.prevButton.clicked.connect(self.prev_img)
        self.nextButton.clicked.connect(self.next_img)

        # авторизуемся, если можем, но если не можем, пользователя авторизовываться не отправляем
        self.service = get_authenticated_service(False)
        if self.service:
            self.actionGoogle_Photo.setEnabled(True)
            self.actionLog_In_Google_Photos.setText('Log Out Google Photos')
        else:
            self.actionGoogle_Photo.setEnabled(False)

        # у пинтереста меняется апи, нынешнее в бетке, они не апрувят мой апп
        self.actionPinterest.setVisible(False)
        self.actionLog_In_Pinterest.setVisible(False)

        # задаём разные переменные на входе
        self.listimages = []
        self.prev_images = []
        self.next_images = []
        self.timer_id = 0

    def browse_folder(self):
        # показываем диалог с поиском папки
        self.listimages.clear()
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку",
                                                               directory=self.settings.value('directory')
                                                               if self.settings.contains('directory') else '')
        if directory:
            for file_name in os.listdir(directory):
                # забираем из папки только картинощки
                if file_name.endswith('.jpg') or file_name.endswith('.png'):
                    self.listimages.append('{}/{}'.format(directory, file_name))
            self.settings.setValue('directory', directory)
            self.settings.sync()
        if self.listimages:
            self.set_image('random')
            return self.listimages
        else:
            # ругаемся
            dlg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                        "Ты чего-то недоговариваешь",
                                        'В выбранной папке нет ни одной картинки >_<',
                                        buttons=QtWidgets.QMessageBox.Ok,
                                        parent=self)
            dlg.exec()

    def play_button(self):
        # основная функция для запуска таймера и разного
        if self.pictureTime.text() and self.listimages and self.playButton.text() == 'Рисуем':
            # здесь живёт драконий костыль, чтобы картинки, удалённые в предыдущий-следующий списки не удалились совсем
            self.listimages += self.next_images + self.prev_images
            self.listimages = list(set(self.listimages))
            # но сами -то эти списки нам нужны пустыми
            self.prev_images.clear()
            self.next_images.clear()

            # нам нужны минуты от пользователя, но таймеру минуты не подходят

            self.mins = self.init_timer(self.pictureTime.text())
            if self.mins:
                self.timer_id = self.startTimer(self.mins*60*1000,
                                                timerType=QtCore.Qt.VeryCoarseTimer)

                # здесь переводим фокус на кнопочку плей, меняем ей название и делаем неактивным поле для ввода
                # надо же хоть как-то показать пользователю, что мы его услышали
                self.playButton.setFocus()
                self.playButton.setText('Хватит')
                self.pictureTime.setEnabled(False)

                # показываем первую рандомную картинку
                self.set_image('random')
                self.settings.setValue('timer', self.pictureTime.text())
                self.settings.sync()

        elif self.playButton.text() == 'Хватит':
            # здесь живёт драконий костыль, чтобы картинки, удалённые в предыдущий-следующий списки не удалились совсем
            self.listimages += self.next_images
            self.listimages = list(set(self.listimages))

            # убиваем единственный таймер, который у нас тут за всех отдувался
            self.killTimer(self.timer_id)
            # возвращаем название кнопке и активность полю для ввода
            self.playButton.setText('Рисуем')
            self.pictureTime.setEnabled(True)
        else:
            # снова ругаемся
            if not self.listimages:
                msg = 'Твоё рвение похвально, но сразу нужно выбрать, что ты будешь рисовать.'
            else:
                msg = 'Всё бы ничего, но я не уверен, что ты хочешь рисовать вечно.'
            dlg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                        "Ты чего-то недоговариваешь",
                                        msg,
                                        buttons=QtWidgets.QMessageBox.Ok,
                                        parent=self)
            dlg.exec()

    def set_image(self, flg):
        # создаём графическую сцену и заливаем её сереньким
        # наследуем от self, чтобы при закрытии окна, графическая сцена тоже закрывалась

        self.scene = QtWidgets.QGraphicsScene(self)
        self.picturesForSketch.setScene(self.scene)
        self.scene.setBackgroundBrush(QtCore.Qt.gray)

        # отчаянно пытаемся понять, какую картинку показывать
        # todo: переписать на итераторы?

        if flg == 'prev':
            # если нажали на prev и список предыдущих картинок не пустой,
            # удаляем нынешнюю картинку из предыдущих и добавляем в новые, если ещё её там нет
            now_img = self.prev_images[0:-1].pop(-1)
            if now_img not in self.next_images:
                self.next_images.append(self.prev_images.pop(-1))
        elif flg == 'next' and self.next_images:
            # если нажали на next и список последующих картинок не пустой,
            # удаляем картинку из последующих и добавляем в предыдущие, если ещё её там нет
            now_img = self.next_images.pop(-1)
            if now_img not in self.prev_images:
                self.prev_images.append(now_img)
        else:
            # сразу картинка удаляется из общего листа с картинками и добавляется в предыдущие картинки
            now_img = self.listimages.pop(self.listimages.index(random.choice(self.listimages)))
            self.prev_images.append(now_img)
            # обнуляется очередь следующих картинок
            self.next_images.clear()

        # наконец-то разбираемся с картинкой, добавляем её на графическую сцену,
        # которая уже привязана к графическому представлению, подогнав по размеру окна с сохранением пропорций

        if now_img.startswith('https'):
            data = urllib.request.urlopen(now_img).read()
            image = QtGui.QImage()
            image.loadFromData(data)
        else:
            image = now_img
        img = self.scene.addPixmap(QtGui.QPixmap(image))
        self.picturesForSketch.fitInView(img, mode=QtCore.Qt.KeepAspectRatio)

    def prev_img(self):
        # позволяем переключиться назад только если в списке предыдущих картинок есть картинки без нынешней
        if self.prev_images[0:-1]:
            self.set_image('prev')

    def next_img(self):
        # позволяем переключиться вперёд, только если картинки в главном списке не закончились
        if self.listimages:
            self.set_image('next')
        else:
            dlg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                                        "Нужно больше картинок",
                                        'Картинки закончились.\nЕсли хочешь, их можно запустить заново!',
                                        buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                        parent=self)
            res = dlg.exec()
            if res == QtWidgets.QMessageBox.Yes:
                self.listimages = self.prev_images[:]

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Return:
            # отслеживаем ентер и переходим к функции для кнопки плей
            self.play_button()

    def init_timer(self, str_time):
        mins = int(str_time)
        hours, minutes = mins // 60, mins % 60

        # составляем экзистенциальные вопросы
        msg = ('Tы уверен, что собираешься рисовать скетч ')
        # просклоняй меня полностью

        if hours % 10 == 1 and hours not in range(10, 20):
            msg += '{} час '.format(hours)
        elif hours % 10 in range(2, 5) and hours not in range(10, 20):
            msg += '{} часа '.format(hours)
        elif hours >= 1:
            msg += '{} часов '.format(hours)

        if minutes % 10 == 1 and minutes not in range(10, 20):
            msg += '{} минуту?'.format(minutes)
        elif minutes % 10 in range(2, 5) and minutes not in range(10, 20):
            msg += '{} минуты?'.format(minutes)
        else:
            msg += '{} минут?'.format(minutes)

        # задаём экзистенциальные вопросы пользователю и надеемся не вогнать его в кризис
        # возвращаем число только если пользователь в нём уверен и оно корректное
        if 60 <= int(str_time) <= 720:
            dlg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                                        "Странное ты выбрал время",
                                        msg,
                                        buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                        parent=self)
            res = dlg.exec()
            if res == QtWidgets.QMessageBox.Yes:
                return int(str_time)
        elif int(str_time) == 0:
            dlg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                        "Странное ты выбрал время",
                                        'При всём желании, за это время ты нарисуешь ничего.',
                                        buttons=QtWidgets.QMessageBox.Ok,
                                        parent=self)
            dlg.exec()
        elif int(str_time) >= 720:
            dlg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                        "Странное ты выбрал время",
                                        'Прости, но даже часа для наброска слишком много. '
                                        'А больше 12 часов, это просто преступление!',
                                        buttons=QtWidgets.QMessageBox.Ok,
                                        parent=self)
            dlg.exec()
        else:
            return int(str_time)

    def timerEvent(self, e):
        # инициируем переключение картинок по таймеру
        self.next_img()

    def gp_auth(self):
        if not self.actionGoogle_Photo.isEnabled():
            try:
                self.service = get_authenticated_service(True)
                self.actionLog_In_Google_Photos.setText(("Log Out Google Photos"))
                self.actionGoogle_Photo.setEnabled(True)
            except Exception as e:
                print(e)
                dlg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                            "Не получилось авторизоваться",
                                            'С авторизацией в Google Photos что-то пошло не так. Попробуй ещё раз.',
                                            buttons=QtWidgets.QMessageBox.Ok,
                                            parent=self)
                dlg.exec()
        else:
            self.actionGoogle_Photo.setEnabled(False)
            self.actionLog_In_Google_Photos.setText(("Log In Google Photos"))
            self.service = None
            if os.path.exists("token.pickle"):
                os.remove("token.pickle")

    def from_google_photo(self):
        # здесь собираем альбомы в список
        results = self.service.albums().list(
            pageSize=50, fields="nextPageToken,albums(id,title)").execute()

        items = results.get('albums', [])
        albums = {}
        if items:
            for item in items:
                albums[item['id']] = item.get('title', 'Без названия')

        # и отдаём их нашему диаоговому окну, в котором так же есть фильтры предустановленные по категориям и по датам
        dlg = GPDialog(albums)
        res = dlg.exec()

        if res == QtWidgets.QDialog.Accepted:
            s, ok = QtWidgets.QInputDialog.getInt(self,
                                                  'Сколько картинок загрузить?',
                                                  'Введи количество от 1 до 2000',
                                                  value=50,
                                                  min=1,
                                                  max=2000,
                                                  step=2)
            count = s if ok else 50
            filters = {}

            # при всём желании, видео мы не заскетчим, фильтруем на тип данных - фото
            filters["mediaTypeFilter"] = {"mediaTypes": ["PHOTO"]}

            if dlg.category_filter():
                filters["contentFilter"] = {"includedContentCategories": dlg.category_filter()}
            if all([dlg.dateTimeFrom.date(), dlg.dateTimeTo.date(), dlg.dateTimeFrom.date() != dlg.dateTimeTo.date()]):
                filters["dateFilter"] = {"dates": [{"year": dlg.dateTimeFrom.date().year(),
                                                    "month": dlg.dateTimeFrom.date().month(),
                                                    "day": dlg.dateTimeFrom.date().day()},
                                                   {"year": dlg.dateTimeTo.date().year(),
                                                    "month": dlg.dateTimeTo.date().month(),
                                                    "day": dlg.dateTimeTo.date().day()}]}
            if dlg.album_filter():
                filters["albumId"] = dlg.album_filter()
            nextpagetoken = ''
            while len(self.listimages) <= count:
                images = self.service.mediaItems().search(body={"filters": filters, "pageSize": 50, 'pageToken': nextpagetoken}).execute()
                nextpagetoken = images['nextPageToken']
                for image in images['mediaItems']:
                    if len(self.listimages) <= s:
                        self.listimages.append(image['baseUrl']+'=w2048-h1024')
                    else:
                        break
            self.set_image('random')

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        dlg = QtWidgets.QMessageBox.question(self,
                                             "Уже уходишь?",
                                             'Уверен, что хочешь закрыть приложение?',
                                             buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if dlg == QtWidgets.QMessageBox.Yes:
            a0.accept()
            QtWidgets.QWidget.closeEvent(self, a0)
            self.settings.setValue('size', self.window().size())
            self.settings.setValue('pos', self.window().pos())
            self.settings.sync()
        else:
            a0.ignore()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ico = QtGui.QIcon('sketchingTool.png')
    app.setWindowIcon(ico)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()