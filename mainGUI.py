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
        self.updateUserids() #sj todo, to update the GUI interface to let user be able to select userid
        self.isSelectionChanged = False 
    
        self.browser = QWebEngineView()
        url = 'https://www.google.co.nz/maps/@-44.5798817,172.5296327,6z'  #sj TODO 
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)

        navigation_bar = QToolBar('Navigation')
        navigation_bar.setIconSize(QSize(64, 64))
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
        navigation_bar.addAction(hull_button)
        navigation_bar.addAction(circle_button)

        # URL bar
        self.urlbar = QLineEdit()
        font = self.urlbar.font()
        font.setPointSize(20)
        self.urlbar.setFont(font) 
        # react to the return press to draw marks like URL editer
        self.urlbar.returnPressed.connect(self.searchUsers)  #sj tmp

        navigation_bar.addSeparator()
        navigation_bar.addAction(QAction(QIcon('icons/userid.png'),'', self))
        navigation_bar.addWidget(self.urlbar)
        navigation_bar.addAction(marker_button)

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
        self.isSelectionChanged = True  #sj, once reload GeoData, change isSelectionChanged to ensure redraw

    def searchUsers(self):
        self.isSelectionChanged = True
        self.graphHelper = None
        self.drawMarkers()

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

    #sj tmp. like a search bar, need redesign the GUI, if I want to add a combo box 
    def getSelectedUserids(self):
        idsTxt = self.urlbar.text()  #get user ids from search bar 
        strParts = idsTxt.split(',') #sj!!! might be ' 15'
        ids = [ p.lstrip().rstrip() for p in strParts]
        return ids  #sj todo

if __name__ == '__main__':
    # init the application
    app = QApplication(sys.argv)
    # init the main window
    window = MainWindow()
    # show it
    window.show()
    # execute the app
    app.exec_()