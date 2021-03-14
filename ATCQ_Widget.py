from __future__ import print_function

import sys, os
try:
    from pathlib import Path
    import urllib.request as url
except:
    from pathlib2 import Path
    import urllib2 as url

from PIL import Image
import json

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtCore
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebChannel import QWebChannel

# Can we use the houdini embedded browser at all? https://www.sidefx.com/docs/houdini/hom/browserpython.html

class ATCQ_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.SCRIPT_PATH = Path(os.path.realpath(__file__)).parent
        self.initUI()

    def initUI(self, node=None):
        self.node = node
        QtCore.qInstallMessageHandler(self.handler) # ignore warnings

        vbox = QVBoxLayout(self)
        self.webEngineView = QWebEngineView()

        self.channel = QWebChannel()
        self.channel.registerObject("atcq", self)
        self.webEngineView.page().setWebChannel(self.channel)
        self.webEngineView.loadFinished.connect(self.on_load_finished)
        self.load_page()

        vbox.addWidget(self.webEngineView)
        self.setLayout(vbox)
        self.setGeometry(600, 300, 600, 300)
        self.setWindowTitle('ATCQ')
        self.show()

    def handler(self, msg_type, msg_log_context, msg_string):
        pass

    def load_page(self):
        # SETHTML DO NOT USE! This will not initialise the working directory and so you cannot load external js, css etc
        # MUST use setURL with the correct local URL for imports to work
        file = str(self.SCRIPT_PATH.joinpath("web/index.html"))
        self.webEngineView.setUrl(QtCore.QUrl.fromLocalFile(file))

    @QtCore.Slot()
    def on_load_finished(self):
        p = str(self.SCRIPT_PATH.joinpath("atcq_image.png"))
        pp = p.replace("\\", "/")
        self.webEngineView.page().runJavaScript("window.setImagePath('{}');".format(pp))

    @QtCore.Slot(str)
    def resize(self, file):
        try:
            im = Image.open(file)
            print("file image resized")
        except:
            im = Image.open(url.urlopen(file))
            print("url image resized")
        sc = im.resize((300,300))
        write_path = str(self.SCRIPT_PATH.joinpath("atcq_image.png"))
        sc.save(write_path, format="PNG")
        print("resized image")
        self.webEngineView.page().runJavaScript('window.setStatus("Image processed");')

    # https://stackoverflow.com/questions/58210400/how-to-receive-data-from-python-to-js-using-qwebchannel
    # @QtCore.Slot(str) @QtCore.Slot(QJsonValue) @QtCore.Slot("QJsonObject") @QtCore.Slot(list)
    @QtCore.Slot(str, str) # generic json str which we parse
    def send_palette(self, palette, weights):
        p = json.loads(palette)
        w = json.loads(weights)
        print(p)
        print(w)

    @QtCore.Slot(str)
    def print(self, t):
        print(t)

    @QtCore.Slot(float)
    def exit(self, a):
        sys.exit()

def main():
    app = QApplication(sys.argv)
    ex = ATCQ_Widget()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

# note on returning values to js without calling js function explicitly?
# https://stackoverflow.com/questions/58210400/how-to-receive-data-from-python-to-js-using-qwebchannel
# In C++ so that a method can return a value it must be declared as Q_INVOKABLE and the equivalent in PyQt is to use result in the @pyqtSlot decorator:
# @QtCore.pyqtSlot(int, result=int)
# def getRef(self, x):
#     print("inside getRef", x)
#     return x + 5