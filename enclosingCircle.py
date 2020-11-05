import sys
from random import randrange
import matplotlib.pyplot as plt
import argparse
from math import *
import numpy as np
from itertools import combinations

class Point:
    pivot = (0.0, 0.0)
    def __init__(self, a, b, description=None, color=None):
        self.x = float(a) 
        self.y = float(b)
        if description: self.title = description
        if color: self.color = color
    def __getitem__(self, item):
        return (self.x, self.y)[item]
    def var(self):
        return (self.x, self.y)
    def __str__(self):
        return "{} {}".format(self.x, self.y) 
    def __lt__(self, other):
        sa = signedArea(self.pivot, self.var(), other.var()) 
        if abs(sa) == 0 :
            # print("co-linear!!! to compare radius") #sjdb
            return (self.x - self.pivot[0])**2 + (self.y-self.pivot[1])**2 < \
                   (other.x - other.pivot[0])**2 + (other.y-other.pivot[1])**2 
        else:
            return sa > 0 
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

def signedArea(pA, pB, pC):
    sArea = pA[0]*pB[1] - pB[0]*pA[1] + pB[0]*pC[1] - pC[0]*pB[1] + pC[0]*pA[1] - pA[0]*pC[1]
    return sArea

class Graph:
    def __init__(self):
        self.points = []
        self.hullps = []
        self.minCirclePs = []
    def __str__(self):
        ret = "Pivot : {}\n".format(Point.pivot)
        for p in self.points:
            ret += str(p) + '; '
        return ret            

    def findPivot(self):
        tmpPv = self.points[0]
        for pt in self.points[1:]:
            if pt.x < tmpPv.x :
                tmpPv = pt
            elif pt.x == tmpPv.x :
                if pt.y < tmpPv.y:
                    tmpPv = pt            
        Point.pivot = tmpPv.var()
        # print("pivot is {}, whoes id is {}".format(tmpPv, hex(id(tmpPv)) ) ) #sjdb
        return tmpPv

    def radiusSort(self):
        self.points.sort()
        # print(self) #sjdb

    def calcConvexHull(self):
        if len(self.hullps) >0:
            return self.hullps
        self.findPivot()
        self.radiusSort()
        self.hullps.append(self.points[0])
        self.hullps.append(self.points[1])
        for p in self.points[2:]:
            if signedArea(self.hullps[-2].var(), self.hullps[-1].var(), p.var()) > 0 :
                self.hullps.append(p)
                # print("Point number %d added" % (self.points.index(p)+1)) #sjdb
            else:
                # !!!!!! very important to check hull validation in a loop, !!!!len(self.hullps)>2 
                while len(self.hullps)>2 and signedArea(self.hullps[-2].var(), self.hullps[-1].var(), p.var()) <= 0:
                    pRm = self.hullps.pop(-1)
                    # print("Point %d  is removed" % (self.points.index(pRm)+1)) #sjdb
                self.hullps.append(p) 
                # print("Point number %d added" % (self.points.index(p)+1)) #sjdb        
        return self.hullps


    def drawScatter(self):        
        plt.close('all')

        if len(self.minCirclePs) == 3:
            pCenter, r = findCircumscribedCircle(self.minCirclePs[0], self.minCirclePs[1], self.minCirclePs[2])
            circleObj = plt.Circle(pCenter.var(), r, color='r', fill=False)
            ax = plt.gca()
            ax.add_patch(circleObj)
            plt.axis('scaled')    
        elif len(self.minCirclePs) == 2:
            pA, pB = self.minCirclePs[0], self.minCirclePs[1]
            pCenter= Point((pA.x+pB.x)/2, (pA.y+pB.y)/2)
            r = distAB(pA.var(), pB.var()) /2 
            circleObj = plt.Circle(pCenter.var(), r, color='r', fill=False)
            ax = plt.gca()
            ax.add_patch(circleObj)
            plt.axis('scaled')    

        pO = Point.pivot
        plt.scatter(pO[0], pO[1], marker="o")
        plt.text(pO[0]+2, pO[1]+2, 'pivot')

        for p in self.points:
            plt.plot([pO[0], p.x], [pO[1], p.y], "o--r")

        # add sorted numbers to the dots
        id = 0
        for p in self.points[1:]:
            id += 1
            plt.text(p.x+2, p.y+2, str(id))

        # draw hull
        hxs = [p.x for p in self.hullps]
        hys = [p.y for p in self.hullps]
        hxs += [Point.pivot[0]]
        hys += [Point.pivot[1]]
        plt.axis('scaled')
        plt.plot(hxs, hys,  "o-g" )

        # draw min enclosing circle
        cirXs = [p.x for p in self.minCirclePs]
        cirYs = [p.y for p in self.minCirclePs]
        cirXs.append(cirXs[0])
        cirYs.append(cirYs[0])
        plt.plot(cirXs, cirYs,  "o-b")
        plt.show()

    def findCirclPoints(self):
        pA, pB = findChord(self.hullps)
        pK, kAngle = findSmallestAngle(pA, pB, self.hullps)
        if kAngle > 90:
            # print("minCirclePs is {}, {}".format(pA, pB)) #sjdb
            self.minCirclePs = [pA, pB]
        elif kAngle <= 90:
            # print("minCirclePs is {}, {}, {}".format(pA, pB, pK)) #sjdb
            self.minCirclePs = [pA, pB, pK]

        if len(self.minCirclePs) == 3:
            pCenter, r = findCircumscribedCircle(self.minCirclePs[0], self.minCirclePs[1], self.minCirclePs[2])
        elif len(self.minCirclePs) == 2:
            pA, pB = self.minCirclePs[0], self.minCirclePs[1]
            pCenter= Point((pA.x+pB.x)/2, (pA.y+pB.y)/2)
        # print("Center Point is {}".format(pCenter))
        return pCenter, self.minCirclePs

def findChord(pList):
    pairs = list(combinations(pList, 2))
    mxDist = 0
    mxDistPair = pairs[0]
    for pair in pairs:
        dist = distAB(pair[0].var(), pair[1].var())
        # print("dist for {}, {} is {}".format(pair[0], pair[1], dist)) #sjdb
        if dist > mxDist:
            mxDist = dist
            mxDistPair = pair
    return mxDistPair[0], mxDistPair[1]

def findSmallestAngle(pA, pB, pList):
    mxCos = -1 # max cos is the min angle
    retP = pList[0]
    # print("Cos P for ({}, {}):".format(pA,pB)) #sjdb
    for p in pList:
        if p == pA or p == pB : continue
        CosP = CosV(pA.var(), p.var(), pB.var())
        # print("k:{} cos={}, angle={:.1f}".format(p, CosP, angleCos(CosP)))  #sjdb
        if CosP > mxCos and CosP != 1:
            mxCos = CosP
            retP = p
    return retP, angleCos(mxCos)

def angleCos(cos):
    return acos(cos)*180/pi

def findCircumscribedCircle(pA, pB, pC):
    pNB = Point(pB.x-pA.x,  pB.y-pA.y) 
    pNC = Point(pC.x-pA.x, pC.y-pA.y)
    determ = 2*(pNB.x*pNC.y - pNB.y*pNC.x)  
    centreNX = (pNC.y*(pNB.x**2 + pNB.y**2) - pNB.y*(pNC.x**2 + pNC.y**2))/determ
    centreNY = (pNB.x*(pNC.x**2 + pNC.y**2) - pNC.x*(pNB.x**2 + pNB.y**2))/determ
    radius = sqrt(centreNX**2 + centreNY**2)
    pCentre = Point(pA.x+centreNX, pA.y+centreNY)
    return pCentre, radius

def drawCircumscribedCircle(pA,pB,pC):
    pCenter, r = findCircumscribedCircle(pA, pB, pC)
    circleObj = plt.Circle(pCenter.var(), radius = r)
    ax = plt.gca()
    ax.add_patch(circleObj)
    plt.axis('scaled')    
    plt.scatter(pA.x, pA.y, marker="o")
    plt.scatter(pB.x, pB.y, marker="o")
    plt.scatter(pC.x, pC.y, marker="o")


            
def distAB(pA, pB):
    return sqrt( (pA[0]-pB[0])**2 + (pA[1]-pB[1])**2)


def CosV(pA, pB, pC):
    sqAB = (pA[0]-pB[0])**2 + (pA[1]-pB[1])**2
    # print(sqAB) #sjdb
    sqCB = (pC[0]-pB[0])**2 + (pC[1]-pB[1])**2
    # print(sqCB) #sjdb
    sqAC = (pC[0]-pA[0])**2 + (pC[1]-pA[1])**2
    # print(sqAC) #sjdb
    ret = 0
    if sqAB != 0 and sqCB != 0:
        ret = (sqAB + sqCB - sqAC)/2/sqrt(sqAB)/sqrt(sqCB) 
    return  ret

def main():
    parser = argparse.ArgumentParser(description="Calculate the convex hull through stdin input or generated randomly.")
    parser.add_argument("-g", "--generate", action="store", help="Generate given number of points")
    args = parser.parse_args() 

    if args.generate != None and args.generate != "":
        if args.generate.isdigit() :
            num = int(args.generate)
            print("%d points will be generated" % num)
            g = Graph()
            for i in range(num):
                pt = Point(randrange(-501, 501), randrange(-501,501))
                g.points.append(pt)
                print(pt) #sjdb
        else:   
            print("you need give a number ")
            exit()
    else:
        g = Graph()
        print("Pls input your point number in line and then two numbers as a point each line:")
        line = sys.stdin.readline()
        num = int(line)
        for i in range(num):
            line = sys.stdin.readline()
            parts = line.split()
            g.points.append(Point(parts[0], parts[1]))

    # g.drawScatter()
    g.calcConvexHull()
    # g.drawScatter()
    g.findCirclPoints()
    g.drawScatter()

if __name__ == "__main__":
    main()

 # Bugs & defects
 # 4, not able to draw points by click on the canves  

 # Bugs resolved:
  # 1, There are dents in the final convex hull  ---- Resolved in calcConvexHull in the two "!!!!!!"
  # 2, not deal with the co-linear issue. Should resoulve. Haven't test with real data. 
  # 3, Crash with (1, 1) (1, 2) (1, 3) , root cause: co-liner and keep on removing the hull points to none.
  # --resolved by add len(hullps) > 2
  # 5, test with negative number  --- passed 