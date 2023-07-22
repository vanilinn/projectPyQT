import random
import sys
import sqlite3

import datetime as dt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, \
    QInputDialog
from PyQt5.QtWidgets import QMainWindow, QDateEdit, QLabel, QFileDialog

NUMBERS_OF_TASKS = {"Математика": 18, "Русский": 27, "Физика": 30, "Биология": 28, "География": 31, "Химия": 34,
                    "Обществознание": 25, "Литература": 12, "История": 19, "Немецкий": 44, "Французский": 44,
                    "Испанский": 44, "Английский": 44, "Информатика": 27}


class Schedule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.con = sqlite3.connect("schedule_db.sqlite")

        self.open_settings()

        self.setGeometry(300, 200, 800, 450)
        self.setWindowTitle("Расписание")

        self.button_rem = QPushButton(self)
        self.button_rem.move(5, 5)
        self.button_rem.resize(150, 25)
        self.button_rem.setText("Открыть напоминания")
        self.button_rem.clicked.connect(self.open_reminder)

        self.button_prof = QPushButton(self)
        self.button_prof.move(5, 30)
        self.button_prof.resize(150, 25)
        self.button_prof.setText("Открыть профиль")
        self.button_prof.clicked.connect(self.open_profile)

        self.btn_reset = QPushButton(self)
        self.btn_reset.move(700, 420)
        self.btn_reset.resize(100, 25)
        self.btn_reset.setText("Сбросить данные")
        self.btn_reset.clicked.connect(self.reset_all)
        self.set_table()

    def reset_all(self):
        self.con = sqlite3.connect("schedule_db.sqlite")
        self.con.cursor().execute("DELETE FROM exams;", )
        self.con.cursor().execute("DELETE FROM timetable;", )
        self.con.commit()
        self.con.close()
        self.close()
        # Функция для сброса данных о экзаменах

    def open_reminder(self):
        self.reminder = Reminder(self)
        self.reminder.show()
        # Функция для открытия напоминалки

    def open_profile(self):
        self.profile = Profile(self)
        self.profile.load_photo()
        self.profile.show()
        # Функция для открытия профиля

    def open_settings(self):
        self.setings = Settings(self)
        # Функция для открытия настроек

    def set_table(self):
        # Функция для визуализации таблицы
        res = self.con.cursor().execute("SELECT * FROM timetable").fetchall()
        table = QTableWidget(self)
        table.setColumnCount(3)
        table.setRowCount(0)
        table.move(100, 100)
        table.resize(table.sizeHint().width() + 51, 300)
        # Назначаем название столбцам
        table.setHorizontalHeaderLabels(["Дата", "Экзамен", "Выполнение"])
        table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
        table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
        # Формируем таблицу
        for i, row in enumerate(res):
            table.setRowCount(
                table.rowCount() + 1)
            for j, elem in enumerate(row):
                table.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        table.resizeColumnsToContents()
        table.show()


# Класс для ошибки
class Error(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 400, 250, 50)
        self.setWindowTitle("Ошибка")
        self.text_of_error = QLabel(self)
        self.text_of_error.setText("Вы ввели некорректные данные")
        self.text_of_error.resize(250, 50)
        self.text_of_error.move(50, 0)


# Класс для напоминалки
class Reminder(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 700, 800, 150)
        self.setWindowTitle("Напоминания")
        self.con = sqlite3.connect("schedule_db.sqlite")
        self.view_reminder()

    def view_reminder(self):
        # Функция для вывода задания на сегодня
        now_date = dt.date.today()
        res = self.con.cursor().execute("""SELECT * FROM timetable
            WHERE date = ?""", (now_date,)).fetchall()
        today_exam = ""

        if res:
            if res[0][2] == '+':
                today_exam = "Вы уже выполнили сегодняшнее задание"
            else:
                today_exam = "Ваше задание на сегодня: " + str(res[0][1])

        self.show_reminder = QLabel(self)
        self.show_reminder.setText(today_exam)
        self.show_reminder.resize(400, 50)
        self.show_reminder.move(30, 10)

        self.is_done_btn = QPushButton('Выполнено', self)
        self.is_done_btn.resize(self.is_done_btn.sizeHint())
        self.is_done_btn.move(100, 100)
        self.is_done_btn.clicked.connect(self.is_done)

    def is_done(self):
        # Функция для отметки выполненного задания
        global ex
        self.con.cursor().execute("""UPDATE timetable SET is_done = "+" WHERE date = ?""", (dt.date.today(),))
        self.con.commit()
        ex.set_table()
        self.close()


# Класс для профиля
class Profile(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.con = sqlite3.connect("schedule_db.sqlite")
        self.setGeometry(1113, 200, 300, 650)
        self.setWindowTitle("Профиль")
        self.load_btn = QPushButton(self)
        self.load_btn.setText("Загрузить фото профиля")
        self.load_btn.resize(self.load_btn.sizeHint())
        self.load_btn.move(80, 300)
        self.load_btn.clicked.connect(self.load_photo)
        self.load_btn_reset = QPushButton(self)
        self.load_btn_reset.setText("Сбросить фото профиля")
        self.load_btn_reset.resize(self.load_btn.sizeHint())
        self.load_btn_reset.move(80, 320)
        self.load_btn_reset.clicked.connect(self.reset_photo)
        self.show_progress = QLabel(self)
        self.show_progress.setText("Подготовка выполнена на : " + self.progress())
        self.show_progress.resize(self.show_progress.sizeHint())
        self.show_progress.move(50, 400)
        self.show_name = QLabel(self)
        self.show_name.setText("Профиль пользователя " + self.input_name())
        self.show_name.resize(self.show_progress.sizeHint())
        self.show_name.move(80, 250)

    def reset_photo(self):
        # Функция для сброса фото пользователя
        f = open("pathofphoto.txt", mode="w")
        f.write("")
        f.close()
        self.close()

    def load_photo(self):
        # Функция для загрузки фото пользователя
        f = open("pathofphoto.txt", mode="r").read()
        if f:
            photo_name = f
        else:
            photo_name = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
            f1 = open("pathofphoto.txt", mode="w")
            f1.write(photo_name)

        self.photo = QPixmap(photo_name)
        self.image = QLabel(self)
        self.image.move(50, 50)
        self.image.resize(200, 200)
        self.image.setPixmap(self.photo)

    def progress(self):
        # Функция для подсчета прогресса
        pluses = 0
        minuses = 0
        table = self.con.cursor().execute("""SELECT * FROM timetable""").fetchall()
        for elem in table:
            if elem[2] == "+":
                pluses += 1
            else:
                minuses += 1
        self.global_progress = pluses / (pluses + minuses) * 100
        return str(round(self.global_progress)) + "%"

    def input_name(self):
        # Функция для ввода имени пользователя
        f = open("username.txt", mode="r")
        user_name = f.read()
        if user_name:
            name = user_name
            return name
        else:
            name, is_ok_pressed = QInputDialog.getText(self, "Введите имя",
                                                       "Как тебя зовут?")
            f1 = open("username.txt", mode="w")
            f1.write(name)
            f1.close()

            if is_ok_pressed:
                return name


# Класс для ввода экзаменов и времени на подготовку
class Settings(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        self.setGeometry(400, 300, 600, 400)
        self.setWindowTitle("Составление расписания")
        self.con = sqlite3.connect("schedule_db.sqlite")
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Settings")
        self.resize(607, 384)
        self.centragrid = QtWidgets.QWidget(self)
        self.centragrid.setObjectName("centragrid")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centragrid)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.btn_liter = QtWidgets.QCheckBox(self.centragrid)
        self.btn_liter.setObjectName("btn_liter")
        self.gridLayout.addWidget(self.btn_liter, 16, 1, 1, 1)
        self.btn_dtch = QtWidgets.QCheckBox(self.centragrid)
        self.btn_dtch.setObjectName("btn_dtch")
        self.gridLayout.addWidget(self.btn_dtch, 3, 1, 1, 1)
        self.btn_bio = QtWidgets.QCheckBox(self.centragrid)
        self.btn_bio.setObjectName("btn_bio")
        self.gridLayout.addWidget(self.btn_bio, 2, 1, 1, 1)
        self.btn_geo = QtWidgets.QCheckBox(self.centragrid)
        self.btn_geo.setObjectName("btn_geo")
        self.gridLayout.addWidget(self.btn_geo, 8, 1, 1, 1)
        self.btn_french = QtWidgets.QCheckBox(self.centragrid)
        self.btn_french.setObjectName("btn_french")
        self.gridLayout.addWidget(self.btn_french, 9, 1, 1, 1)
        self.btn_physics = QtWidgets.QCheckBox(self.centragrid)
        self.btn_physics.setObjectName("btn_physics")
        self.gridLayout.addWidget(self.btn_physics, 16, 0, 1, 1)
        self.btn_spanish = QtWidgets.QCheckBox(self.centragrid)
        self.btn_spanish.setObjectName("btn_spanish")
        self.gridLayout.addWidget(self.btn_spanish, 4, 1, 1, 1)
        self.btn_social = QtWidgets.QCheckBox(self.centragrid)
        self.btn_social.setObjectName("btn_social")
        self.gridLayout.addWidget(self.btn_social, 15, 1, 1, 1)
        self.btn_russian = QtWidgets.QCheckBox(self.centragrid)
        self.btn_russian.setObjectName("btn_russian")
        self.gridLayout.addWidget(self.btn_russian, 2, 0, 1, 1)
        self.btn_chemistry = QtWidgets.QCheckBox(self.centragrid)
        self.btn_chemistry.setObjectName("btn_chemistry")
        self.gridLayout.addWidget(self.btn_chemistry, 15, 0, 1, 1)
        self.btn_it = QtWidgets.QCheckBox(self.centragrid)
        self.btn_it.setObjectName("btn_it")
        self.gridLayout.addWidget(self.btn_it, 4, 0, 1, 1)
        self.btn_math = QtWidgets.QCheckBox(self.centragrid)
        self.btn_math.setObjectName("btn_math")
        self.gridLayout.addWidget(self.btn_math, 3, 0, 1, 1)
        self.btn_history = QtWidgets.QCheckBox(self.centragrid)
        self.btn_history.setObjectName("btn_history")
        self.gridLayout.addWidget(self.btn_history, 9, 0, 1, 1)
        self.btn_eng = QtWidgets.QCheckBox(self.centragrid)
        self.btn_eng.setObjectName("btn_eng")
        self.gridLayout.addWidget(self.btn_eng, 8, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.pushButton = QPushButton("Кнопка", self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.check_checkbox)
        self.gridLayout_2.addWidget(self.pushButton, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.centragrid)
        self.label.setMaximumSize(QtCore.QSize(300, 100))
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.calendar1 = QDateEdit(self)
        self.calendar1.setMinimumDate(QDate.currentDate())
        self.calendar1.resize(110, 22)
        self.calendar1.move(400, 250)
        self.calendar2 = QDateEdit(self)
        self.calendar2.setMinimumDate(QDate.currentDate())
        self.calendar2.resize(110, 22)
        self.calendar2.move(400, 280)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def check_number_of_tasks(self):
        # Проверка на корректность ввода
        self.first_date = max(dt.date(self.calendar1.date().year(), self.calendar1.date().month(),
                                      self.calendar1.date().day()), dt.date.today())
        self.second_date = dt.date(self.calendar2.date().year(), self.calendar2.date().month(),
                                   self.calendar2.date().day())
        self.days_to = self.second_date - self.first_date
        self.our_exams = self.con.cursor().execute("""SELECT * FROM exams""").fetchall()
        self.number_of_tasks = 0
        for elem in self.our_exams:
            self.number_of_tasks += NUMBERS_OF_TASKS[elem[1]]
        if dt.timedelta(days=self.number_of_tasks) > self.days_to or self.number_of_tasks <= 0:
            self.error = Error()
            self.error.show()
            self.con.cursor().execute("DELETE FROM exams;", )
            self.con.cursor().execute("DELETE FROM timetable;", )
            return False
        return True

    def create_table(self):
        # Заполнение таблицы с расписанием
        list1 = []
        for elem in self.our_exams:
            for i in range(NUMBERS_OF_TASKS[elem[1]]):
                list1.append(elem)
        random.shuffle(list1)
        counter_of_days = 0
        for elem in list1:
            now_date = self.first_date + dt.timedelta(days=counter_of_days)

            self.con.cursor().execute("""INSERT INTO timetable(exam_id, date, is_done) VALUES(?, ?, ?)""",
                                      (str(elem[1]), now_date, "-"))
            counter_of_days += 1

    def fill_bd(self, btn):
        # Формирование запроса к БД дял каждой кнопки, если она нажата
        if btn.isChecked():
            self.con.cursor().execute("""INSERT INTO exams(name) VALUES(?)""",
                                      (btn.text(),))

    def check_checkbox(self):
        # Проверка выбора дял каждого экзамена
        global ex
        for cb in [self.btn_math, self.btn_russian, self.btn_physics, self.btn_chemistry, self.btn_it,
                   self.btn_bio, self.btn_history, self.btn_geo, self.btn_eng, self.btn_dtch,
                   self.btn_french, self.btn_social, self.btn_spanish, self.btn_liter]:
            self.fill_bd(cb)
        self.close()
        if self.check_number_of_tasks():
            self.create_table()
            self.con.commit()
            ex.set_table()
            ex.show()
        self.con.commit()
        self.con.close()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Экзамены и сроки"))
        self.btn_liter.setText(_translate("MainWindow", "Литература"))
        self.btn_dtch.setText(_translate("MainWindow", "Немецкий"))
        self.btn_bio.setText(_translate("MainWindow", "Биология"))
        self.btn_geo.setText(_translate("MainWindow", "География"))
        self.btn_french.setText(_translate("MainWindow", "Французский"))
        self.btn_physics.setText(_translate("MainWindow", "Физика"))
        self.btn_spanish.setText(_translate("MainWindow", "Испанский"))
        self.btn_social.setText(_translate("MainWindow", "Обществознание"))
        self.btn_russian.setText(_translate("MainWindow", "Русский"))
        self.btn_chemistry.setText(_translate("MainWindow", "Химия"))
        self.btn_it.setText(_translate("MainWindow", "Информатика"))
        self.btn_math.setText(_translate("MainWindow", "Математика"))
        self.btn_history.setText(_translate("MainWindow", "История"))
        self.btn_eng.setText(_translate("MainWindow", "Английский"))
        self.pushButton.setText(_translate("MainWindow", "Подтвердить"))
        self.label.setText(_translate("MainWindow", "Выберете экзамен"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Schedule()
    ex1 = Settings(ex)
    con = sqlite3.connect("schedule_db.sqlite")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM exams").fetchall()
    if not result:
        ex1.show()
    else:
        ex.show()
    con.close()
    sys.exit(app.exec())
