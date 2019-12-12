import sqlite3
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidgetItem
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow


class DBSaper(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gamerStat.ui', self)
        self.con = sqlite3.connect('book_catalog.db')
        self.showPlayer_b.clicked.connect(self.showPlayers)
        self.showAll_b.clicked.connect(self.showAllBook)
        self.search_b.clicked.connect(self.search)
        self.showSelect.clicked.connect(self.showSelectedBook)
        self.s_ask = ''
        self.by_author = False

    def search(self):
        win = SearchWin(self)
        win.show()

    def showSelectedBook(self):
        temp = [(i.row(), i.text(), i.column()) for i in self.tableWidget.selectedItems()]
        temp.sort(key=lambda u: u[2])
        if len(temp) == 4:
            if temp[0][0] == temp[1][0] == temp[2][0] == temp[3][0] != 0:
                cur = self.con.cursor()
                book = cur.execute(
                    '''Select year, description, image
                    FROM books 
                    WHERE name LIKE ? AND 
                    autor = (SELECT id FROM autors WHERE name LIKE ?) AND 
                    genre = (SELECT id FROM genres WHERE name LIKE ?)''',
                    (temp[0][1].lower(), temp[1][1].lower(), temp[2][1].lower())).fetchall()[0]
                autor = temp[1][1]
                genre = temp[2][1]
                win = SelectBookWindow(self, title=temp[0][1], author=autor,
                                       genre=genre, year=book[0], description=book[1], image=book[2])
                win.show()

    def showResOfSerch(self):
        cur = self.con.cursor()
        if not self.by_author:
            result = cur.execute(
                '''Select name, autor, genre, year 
                FROM books 
                WHERE name LIKE ? ''',
                ('%' + self.s_ask.lower() + '%',)).fetchall()
        else:
            result = cur.execute(
                '''Select name, autor, genre, year from books WHERE (SELECT name FROM autors WHERE id = autor) LIKE ? ''',
                ('%' + self.s_ask.lower() + '%',)).fetchall()
        self.tableWidget.setRowCount(len(result) + 1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Title'))
        self.tableWidget.setItem(0, 1, QTableWidgetItem('Author'))
        self.tableWidget.setItem(0, 2, QTableWidgetItem('Genre'))
        self.tableWidget.setItem(0, 3, QTableWidgetItem('Year'))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                if j == 1:
                    temp = cur.execute('Select name from autors WHERE id = ?', (val,)).fetchall()[0][0]
                    self.tableWidget.setItem(i + 1, j,
                                             QTableWidgetItem(' '.join([i.capitalize() for i in temp.split()])))
                    continue
                if j == 2:
                    temp = cur.execute('Select name from genres WHERE id = ?', (val,)).fetchall()[0][0]
                    self.tableWidget.setItem(i + 1, j,
                                             QTableWidgetItem(' '.join([i.capitalize() for i in temp.split()])))
                    continue
                self.tableWidget.setItem(i + 1, j, QTableWidgetItem(str(val).capitalize()))
        self.tableWidget.resizeColumnsToContents()

    def showPlayers(self):
        cur = self.con.cursor()
        result = cur.execute(
            '''Select name from autors WHERE id BETWEEN 1 AND 1001''').fetchall()
        self.tableWidget.setRowCount(len(result) + 1)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Name'))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i + 1, j, QTableWidgetItem(str(val).capitalize()))

    def showAllBook(self):
        cur = self.con.cursor()
        result = cur.execute(
            '''Select name, autor, genre, year from books WHERE id BETWEEN 0 AND 1001''').fetchall()
        self.tableWidget.setRowCount(len(result) + 1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Title'))
        self.tableWidget.setItem(0, 1, QTableWidgetItem('Author'))
        self.tableWidget.setItem(0, 2, QTableWidgetItem('Genre'))
        self.tableWidget.setItem(0, 3, QTableWidgetItem('Year'))
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                if j == 1:
                    temp = cur.execute('Select name from autors WHERE id = ?', (val,)).fetchall()[0][0]
                    self.tableWidget.setItem(i + 1, j,
                                             QTableWidgetItem(' '.join([i.capitalize() for i in temp.split()])))
                    continue
                if j == 2:
                    temp = cur.execute('Select name from genres WHERE id = ?', (val,)).fetchall()[0][0]
                    self.tableWidget.setItem(i + 1, j,
                                             QTableWidgetItem(' '.join([i.capitalize() for i in temp.split()])))
                    continue
                self.tableWidget.setItem(i + 1, j, QTableWidgetItem(str(val).capitalize()))
        self.tableWidget.resizeColumnsToContents()


class SearchWin(QMainWindow):
    def __init__(self, main=None):
        self.main = main
        super().__init__(main)
        uic.loadUi('search_win.ui', self)
        self.pushButton.clicked.connect(self.search)

    def search(self):
        self.main.s_ask = self.lineEdit.text()
        self.main.by_author = self.radioButton.isChecked()
        self.close()
        self.main.showResOfSerch()


class SelectBookWindow(QMainWindow):
    def __init__(self, main=None, title='book of Life', author='MinusOne',
                 genre='humdrum', year='2003', description='default book for test', image=None):
        super().__init__(main)
        uic.loadUi('show_selected_book_ui.ui', self)
        self.title_le.setText(str(title))
        self.author_le.setText(str(author))
        self.genre_le.setText(str(genre))
        self.year_le.setText(str(year))
        self.description_te.setText(str(description))
        self.back_b.clicked.connect(self._)
        if image != None:
            self.pixmap = QPixmap(str(image))
        else:
            self.pixmap = QPixmap('def_image.png')
        self.image_in_frame.setPixmap(self.pixmap)

    def _(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSaper()
    ex.show()
    sys.exit(app.exec())
