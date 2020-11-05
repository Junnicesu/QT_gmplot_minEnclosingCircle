import sys
from pathlib import Path
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from gmplotGraphHelper import *

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Geo Plot for locations')
        self.setWindowIcon(QIcon('icons/earth.png')) #sj todo
        self.resize(1440, 1024)
        self.show()

        self.graphHelper = None 
        self.geoData = [] #sj
        self.userIds = set() #sj userid set
        self.checkGeoData() #sj todo. check the json file exist, if not request online.
        self.updateUserids() #sj todo
        self.isSelectionChanged = False 
    
        self.browser = QWebEngineView()
        url = 'https://www.google.co.nz/maps/@-44.5798817,172.5296327,6z'  #sj TODO 
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)

        navigation_bar = QToolBar('Navigation')
        navigation_bar.setIconSize(QSize(48, 48))
        self.addToolBar(navigation_bar)

        reload_button = QAction(QIcon('icons/reloadGeo.png'), 'Reload', self)
        marker_button = QAction(QIcon('icons/drawMarkers.png'), 'GeoMarks', self)
        hull_button = QAction(QIcon('icons/drawHull.png'), 'Hull Points', self)
        circle_button = QAction(QIcon('icons/drawCircle.png'), 'Encircle Points', self)

        reload_button.triggered.connect(self.reloadGeoData)
        marker_button.triggered.connect(self.drawMarkers)
        hull_button.triggered.connect(self.drawHull)
        circle_button.triggered.connect(self.drawCircle)

        # add buttons to the Nav bar
        navigation_bar.addAction(reload_button)
        navigation_bar.addAction(marker_button)
        navigation_bar.addAction(hull_button)
        navigation_bar.addAction(circle_button)

        # 添加URL地址栏
        self.urlbar = QLineEdit()
        # 让地址栏能响应回车按键信号
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        navigation_bar.addSeparator()
        navigation_bar.addWidget(self.urlbar)

        # 让浏览器相应url地址的变化
        self.browser.urlChanged.connect(self.renew_urlbar)

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == '':
            q.setScheme('http')
        self.browser.setUrl(q)

    def renew_urlbar(self, q):
        # 将当前网页的链接更新到地址栏
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    # load Geo Data From Cached file first. If not, request it from internet.
    def checkGeoData(self):
        geoData = []
        try:
            geoData = loadDataPoints()
            if len(geoData) == 0:
                geoData = reqAndSaveDataPoints()
        except FileNotFoundError:
            geoData = reqAndSaveDataPoints()
        except:
            e = sys.exc_info()[0]
            #sj todo, popup msg
            # print("sys error: \n{}".format(e))
            # sys.exit(-1)
        if len(geoData) > 0 :
            self.geoData = geoData

    def reloadGeoData(self):
        geoData = []
        try:
            geoData = reqAndSaveDataPoints()
        except:
            e = sys.exc_info()[0]
            #sj todo, popup msg

    def drawMarkers(self):
        qUrl = QUrl('file:///mapMakers.html')
        if qUrl.scheme() == '':
            qUrl.setScheme('file')        
        if not self.isSelectionChanged and Path("mapMakers.html").is_file():
            self.browser.setUrl(qUrl)
        else:
            if not self.graphHelper :
                userids = self.getSelectedUserids() #sj todo
                dataDictForDraw = getDataByUserIds(userids, self.geoData) #dict of list of dict
                self.graphHelper = getGraphHelper(dataDictForDraw)
            plotMarkers(self.graphHelper)
            self.browser.setUrl(qUrl)

    def drawHull(self):
        qUrl = QUrl('file:///mapConvex.html')
        if not self.isSelectionChanged and Path("mapConvex.html").is_file():
            self.browser.setUrl(qUrl)
        else:
            if not self.graphHelper :
                userids = self.getSelectedUserids() #sj todo
                dataDictForDraw = getDataByUserIds(userids, self.geoData) #dict of list of dict
                self.graphHelper = getGraphHelper(dataDictForDraw)
                for p in self.graphHelper.points:
                    print(p)  #sjdb
            plotConvexHull(self.graphHelper)
            self.browser.setUrl(qUrl)

    def drawCircle(self):
        qUrl = QUrl('file:///mapCircle.html')
        if not self.isSelectionChanged and Path("mapCircle.html").is_file():
            self.browser.setUrl(qUrl)
        else:
            if not self.graphHelper:
                userids = self.getSelectedUserids() #sj todo
                dataDictForDraw = getDataByUserIds(userids, self.geoData) #dict of list of dict
                self.graphHelper = getGraphHelper(dataDictForDraw)
            plotEnclosingCircle(self.graphHelper)
            self.browser.setUrl(qUrl)

    # fresh the GUI combo box of users after reload 
    def updateUserids(self):
        if len(self.geoData) > 0 :
            for data in self.geoData:
                self.userIds.add(data['userid'])
        #sj todo, add the userids to the combo box

    def getSelectedUserids(self):
        self.isSelectionChanged = True
        return ['2014','1977']  #sj todo

if __name__ == '__main__':
    # 创建应用
    app = QApplication(sys.argv)
    # 创建主窗口
    window = MainWindow()
    # 显示窗口
    window.show()
    # 运行应用，并监听事件
    app.exec_()