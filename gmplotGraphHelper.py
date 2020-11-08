import gmplot
import os,sys,math
from enclosingCircle import *
import urllib.request, json
import random
import matplotlib.colors as mcolors
import argparse

def reqAndSaveDataPoints():
    geoData = []
    with urllib.request.urlopen(r"http://developer.kensnz.com/getlocdata") as url:
        geoDataStr = url.read().decode()
        f = open("geo_locals.json", 'w')
        f.write(geoDataStr)
        f.close()
        geoData = json.loads(geoDataStr) # a list of dict 
        # {"id":"419","userid":"15","latitude":"37.421798","longitude":"-122.0841619","description":"lab","created_at":"2019-11-06 21:44:45","updated_at":"2019-11-06 21:44:45"},
    return geoData

def loadDataPoints():
    geoData = []
    with open(r'geo_locals.json', 'r') as file:
        geoData = json.loads(file.read().replace('/n', ''))
    return geoData

colorNames = [name  for name, color in mcolors.CSS4_COLORS.items()]
def random_color():
    # levels = range(32,256,32)
    # t = tuple(random.choice(levels) for _ in range(3))
    # return '#{:02x}{:02x}{:02x}'.format(t[0], t[1], t[2])
    return colorNames[random.randrange(0, 148)]

def getDataByUserIds(ids, geoLocations):
    geoData = geoLocations
    retDataDict = {}
    for id in ids:
        id = id.lstrip().rstrip()
        retDataDict[id] = []
    for data in geoData:
        if data['userid'] in ids:
            # print(data) #sjdb
            if float(data['latitude']) < 0: 
                retDataDict[data['userid']].append(data)
    return retDataDict 

#calc distance between 2 geo location
def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

def getGraphHelper(dataDictForDraw):
    graphHelper = Graph()
    for id in dataDictForDraw:
        dataForDraw = dataDictForDraw[id]
        color=random_color()
        locList = [ Point(data['latitude'], data['longitude'], data['description'], color) for data in  dataForDraw]
        # for p in locList:
        #     print(p) #sjdb
        graphHelper.points += locList 
    return graphHelper

def plotMarkers(graph):
    gmap = gmplot.GoogleMapPlotter(-46.402902, 168.386174, 10, apikey='')
    for p in graph.points:
        gmap.marker(*p.var(), title=p.title, color=p.color)
    gmap.draw("mapMakers.html")

def plotConvexHull(graph):
    gmap = gmplot.GoogleMapPlotter(-46.402902, 168.386174, 10, apikey='')
    for p in graph.points:
        gmap.marker(*p.var(), title=p.title, color=p.color)
    cnvxPs = graph.calcConvexHull()
    attractions_lats, attractions_lngs = zip(*[p.var() for p in cnvxPs])
    gmap.polygon(attractions_lats, attractions_lngs, color='cornflowerblue', edge_width=2)
    gmap.draw("mapConvex.html")

def plotEnclosingCircle(graph):
    gmap = gmplot.GoogleMapPlotter(-46.402902, 168.386174, 10, apikey='')
    for p in graph.points:
        gmap.marker(*p.var(), title=p.title, color=p.color)
    cnvxPs = graph.calcConvexHull()
    attractions_lats, attractions_lngs = zip(*[p.var() for p in cnvxPs])
    gmap.polygon(attractions_lats, attractions_lngs, color='cornflowerblue', edge_width=2)
    pCenter, circumPs = graph.findCirclPoints()
    mxRSize = 0
    for p in circumPs:
        rSize = haversine(pCenter.var(), p.var())
        mxRSize = rSize if rSize > mxRSize else mxRSize
    gmap.polygon(*zip(*[p.var() for p in circumPs]), color='red', edge_width=3)
    gmap.marker(*pCenter.var() , color='cornflowerblue')
    gmap.text(*pCenter.var() , 'Circle center', color='blue')
    gmap.circle(*pCenter.var(), mxRSize, color='ivory')    
    gmap.draw("mapCircle.html")


def main():
    geoData = []
    try:
        geoData = loadDataPoints()
        if len(geoData) == 0:
            geoData = reqAndSaveDataPoints()
    except FileNotFoundError:
        geoData = reqAndSaveDataPoints()
    except:
        e = sys.exc_info()[0]
        print("sys error: \n{}".format(e))
        sys.exit(-1)

    useridSet = set()
    for data in geoData:
        useridSet.add(data['userid'])
    
    print("All user ids:")
    print(useridSet)
 
    print("\nInput the user's geo location that you want to draw on the map: (q for quit)")
    line = sys.stdin.readline().rstrip()
    while line != 'q':
        strParts = line.split(',') #sj!!! might be ' 15'
        parts = [ p.lstrip().rstrip() for p in strParts]          
        dataDictForDraw = getDataByUserIds(parts, geoData) #dict of list of dict
        # print(dataDictForDraw) #sjdb
        sCmd = input("\nDo you want to draw an enclosing circle(c) or a polygon(p), (q) for quit?\n")
        while sCmd.rstrip().lstrip() != 'q':
            graphHelper = getGraphHelper(dataDictForDraw)
            plotMarkers(graphHelper)

            if 'p' in sCmd  :
                # print("in draw polygon") #sjdb
                plotConvexHull(graphHelper)
                os.system("start mapConvex.html")
            if  'c' in sCmd :
                # # print("in write circle") #sjdb
                plotEnclosingCircle(graphHelper)
                os.system("start mapCircle.html")
            sCmd = input("\nDo you want to draw an enclosing circle(c) or a polygon(p), (q) for quit?\n")

        print("\nInput the user's geo location that you want to draw on the map: (q for quit)")
        line = sys.stdin.readline().rstrip()

if __name__ == '__main__':
    main()