import gmplot
import os,sys,math
from enclosingCircle import *
import urllib.request, json
import random
import matplotlib.colors as mcolors

with urllib.request.urlopen(r"http://developer.kensnz.com/getlocdata") as url:
    geoData = json.loads(url.read().decode()) # a list of dict 
    # {"id":"419","userid":"15","latitude":"37.421798","longitude":"-122.0841619","description":"lab","created_at":"2019-11-06 21:44:45","updated_at":"2019-11-06 21:44:45"},

colorNames = [name  for name, color in mcolors.CSS4_COLORS.items()]
def random_color():
    # levels = range(32,256,32)
    # t = tuple(random.choice(levels) for _ in range(3))
    # return '#{:02x}{:02x}{:02x}'.format(t[0], t[1], t[2])
    return colorNames[random.randrange(0, 148)]

def getDataByUserIds(ids):
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


def main():
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
        dataDictForDraw = getDataByUserIds(parts) #dict of list of dict
        # print(dataDictForDraw) #sjdb
        sCmd = input("\nDo you want to draw an enclosing circle(c) or a polygon(p), (q) for quit?\n")
        while sCmd.rstrip().lstrip() != 'q':

            gmap = gmplot.GoogleMapPlotter(-46.402902, 168.386174, 14, apikey='')
            g = Graph()
            for id in dataDictForDraw:
                dataForDraw = dataDictForDraw[id]
                locList = [ Point(data['latitude'], data['longitude']) for data in  dataForDraw]
                # for p in locList:
                #     print(p) #sjdb
                # print([*zip(*locList)]) #sjdb
                if len(locList) > 0:
                    gmap.scatter(*zip(*locList), color=random_color(), size=40, marker=True)        
                g.points += locList        

            cnvPs = g.calcConvexHull()

            if 'p' in sCmd  :
                # print("in draw polygon") #sjdb
                attractions_lats, attractions_lngs = zip(*[p.var() for p in cnvPs])
                gmap.polygon(attractions_lats, attractions_lngs, color='cornflowerblue', edge_width=2)
            if  'c' in sCmd :
                # print("in write circle") #sjdb
                pCenter, circumPs = g.findCirclPoints()
                mxRSize = 0
                for p in circumPs:
                    rSize = haversine(pCenter.var(), p.var())
                    mxRSize = rSize if rSize > mxRSize else mxRSize
                gmap.polygon(*zip(*[p.var() for p in g.minCirclePs]), color='red', edge_width=3)
                gmap.marker(*pCenter.var() , color='cornflowerblue')
                gmap.text(*pCenter.var() , 'Circle center', color='blue')
                gmap.circle(*pCenter.var(), mxRSize, color='ivory')
            gmap.draw('sjmap.html')
            os.system("start sjmap.html")
            sCmd = input("\nDo you want to draw an enclosing circle(c) or a polygon(p), (q) for quit?\n")

        print("\nInput the user's geo location that you want to draw on the map: (q for quit)")
        line = sys.stdin.readline().rstrip()

if __name__ == '__main__':
    main()