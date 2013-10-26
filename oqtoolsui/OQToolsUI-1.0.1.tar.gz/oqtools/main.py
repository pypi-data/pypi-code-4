import sys
from PyQt4 import QtGui as gui

from oqtools.main_window import MainWindow


def main():
    app = gui.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()