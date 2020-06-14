# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
import datetime


class GPDialog(QtWidgets.QDialog):
    def __init__(self, albums, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("Поиск картинок на Google Photos")
        """Здесь создаём диалогово окно для фильтров по Google Photos
        Документация https://developers.google.com/photos/library/guides/apply-filters"""
        self.mainBox = QtWidgets.QVBoxLayout()
        self.resize(600, 400)

        self.mainBox = QtWidgets.QVBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()
        """Здесь добавляем модель вкладок "аккордеон" """
        self.toolBox = QtWidgets.QToolBox()

        """Здесь объявляем категории"""
        self.category_box = QtWidgets.QGroupBox("Категория")
        self.category_vbox = QtWidgets.QVBoxLayout()

        self.categories = {
            'ANIMALS': 'Животные',
            'FASHION': 'Мода',
            'LANDMARKS': 'Достопримечательности',
            'RECEIPTS': 'Чеки',
            'WEDDINGS': 'Свадьбы',
            'ARTS': 'Искусство',
            'FLOWERS': 'Цветы',
            'LANDSCAPES': 'Пейзажи',
            'SCREENSHOTS': 'Скриншоты',
            'WHITEBOARDS': 'Доски для записей',
            'BIRTHDAYS': 'Дни рождения',
            'FOOD': 'Еда',
            'NIGHT': 'Ночи',
            'SELFIES': 'Селфи',
            'CITYSCAPES': 'Городские пейзажи',
            'GARDENS': 'Сады',
            'PEOPLE': 'Люди',
            'SPORT': 'Спорт',
            'CRAFTS': 'Крафт',
            'HOLIDAYS': 'Праздники',
            'PERFORMANCES': 'Выступления',
            'TRAVEL': 'Путешествия',
            'DOCUMENTS': 'Документы',
            'HOUSES': 'Дома',
            'PETS': 'Животные',
            'UTILITY': 'Полезности'}

        self.category_checkbox = {}

        for category, name in self.categories.items():
            self.category_checkbox[category] = QtWidgets.QCheckBox(name)
            self.category_checkbox[category].setCheckState(QtCore.Qt.Unchecked)
            self.category_checkbox[category].toggled["bool"].connect(self.category_filter)

            self.category_vbox.addWidget(self.category_checkbox[category])

        self.category_box.setLayout(self.category_vbox)
        self.toolBox.addItem(self.category_box, "По категории")

        """Здесь объявляем даты"""
        self.dateTime_box = QtWidgets.QGroupBox("Дата")
        dt = datetime.datetime.today()
        self.dateTime_hbox = QtWidgets.QHBoxLayout()
        self.dateTimeFrom = QtWidgets.QDateEdit(dt.date())
        self.dateTimeFrom.setMaximumDate(dt.date())
        self.dateTimeFrom.setCalendarPopup(True)
        self.dateTimeTo = QtWidgets.QDateEdit(dt.date())
        self.dateTimeTo.setMaximumDate(dt.date())
        self.dateTimeTo.setCalendarPopup(True)
        self.dateTime_hbox.addWidget(self.dateTimeFrom)
        self.dateTime_hbox.addWidget(self.dateTimeTo)
        self.dateTime_box.setLayout(self.dateTime_hbox)
        self.toolBox.addItem(self.dateTime_box, "По дате")

        """Здесь выбираем из альбома"""
        self.albums_box = QtWidgets.QGroupBox("Альбомы")
        self.albums_vbox = QtWidgets.QVBoxLayout()
        self.albums_radiobutton = {}

        if albums:
            for id, album in albums.items():
                self.albums_radiobutton[id] = QtWidgets.QRadioButton(album)
                self.albums_radiobutton[id].toggled["bool"].connect(self.album_filter)

                self.albums_vbox.addWidget(self.albums_radiobutton[id])

            self.albums_box.setLayout(self.albums_vbox)
            self.toolBox.addItem(self.albums_box, "По альбому")
        else:
            self.toolBox.addItem(QtWidgets.QLabel("Не найдено ни одного альбома"), "По альбому")
        self.toolBox.setCurrentIndex(0)

        self.vbox.addWidget(self.toolBox)
        self.mainBox.addLayout(self.vbox)

        self.hbox = QtWidgets.QHBoxLayout()
        self.btnOK = QtWidgets.QPushButton("&OK")
        self.btnCancel = QtWidgets.QPushButton("&Cancel")
        self.btnCancel.setDefault(True)
        self.btnOK.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.reject)
        self.hbox.addWidget(self.btnOK)
        self.hbox.addWidget(self.btnCancel)
        self.mainBox.addLayout(self.hbox)

        self.setLayout(self.mainBox)

        self.accepted.connect(self.on_accepted)
        self.rejected.connect(self.on_rejected)
        self.finished[int].connect(self.on_finished)

    def category_filter(self):
        category_list = []
        for category in self.categories:
            if self.category_checkbox[category].checkState() and category not in category_list:
                category_list.append(category)
        return category_list

    def album_filter(self):
        for album in self.albums_radiobutton:
            if self.albums_radiobutton[album].isChecked():
                return album

    def on_accepted(self):
        self.category_filter().clear()

    def on_rejected(self):
        self.category_filter().clear()

    def on_finished(self):
        self.category_filter().clear()

