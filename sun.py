import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "140,40"

import pygame, sys, math
from pygame.locals import *
import random

FPS = 20                                 # frames per second, the general speed of the program
WINDOWWIDTH = 720                          # size of window's width in pixels
WINDOWHEIGHT = 720                         # size of windows' height in pixels
CELLSIZE = 12                               # size of box height & width in pixels

BLACK    = (  0,   0,   0)
DARK     = ( 50,  50,  50)
GRAY     = (100, 100, 100)
WHITE    = (255, 255, 255)
YELLOW   = (255, 255,   0)
BLUE     = (  0,   0, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)

                 
colours = [RED,BLUE,BLACK,GREEN]

def main():
    global DISPLAYSURF
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    DISPLAYSURF.fill(GRAY)
    pygame.display.set_caption('SUN')

    frames = 0
    readyToStart = False
    drawGrid()
    
    pygame.draw.circle(DISPLAYSURF, RED, sunPosition(frames % WINDOWWIDTH), 4, 0)
    
    
    painted = set()
    while True:                                # main loop
        for event in pygame.event.get():       # event handling loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()          
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos     
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    readyToStart = True
        
        if readyToStart:
            DISPLAYSURF.fill(GRAY)
            for p in painted:
                paintCell(p[0],p[1],YELLOW)
            drawGrid()
                   
            for cell in painted: pygame.draw.polygon(DISPLAYSURF,DARK,cellShadow(sunPosition(frames % WINDOWWIDTH),cell))
            for part in allParts(painted):
                colour = (random.randint(0,255),random.randint(0,255),random.randint(0,255)) # colours[i % len(colours)]
                for p in part:
                    paintCell(p[0],p[1],colour) 
                
            drawGrid() 
            
            pygame.draw.circle(DISPLAYSURF, RED, sunPosition(frames % WINDOWWIDTH), 4, 0)
                    
                    
                    
                    
                    

                                  
        if pygame.mouse.get_pressed()[0]: 
            (l,t) = cellCoordinates(mousex,mousey)
            
            paintCell(l,t,YELLOW)
            drawGrid()
            painted.add((l,t))
        
        frames += 1
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        

def allCellVertices(cells):
    result = set()
    for cell in cells:
        vert = tuple(c*CELLSIZE for c in cell)
        vert1 = (vert[0]+CELLSIZE,vert[1])
        vert2 = (vert[0]+CELLSIZE,vert[1]+CELLSIZE)
        vert3 = (vert[0],vert[1]+CELLSIZE)
        result.add(vert)
        result.add(vert1)
        result.add(vert2)
        result.add(vert3)
    return result

def allParts(obstacle):
    rest = obstacle
    lis = []
    while rest != set():
        lis.append(onePart(rest))
        rest = rest - onePart(rest)
    return lis

def onePart(obstacle):
    first = list(obstacle)[0]
    part = {first}
    part1 = {first}
    part2 = set()
    while part1 != set():  
        for p in part1:
            for n in cellNeighbors(p):
                if n in obstacle and n not in part: 
                    part2.add(n)
                    part.add(n)
        part1 = part2
        part2 = set()
    return part

def cellCoordinates(x,y):
    left = math.floor(x/CELLSIZE)
    top = math.floor(y/CELLSIZE)
    return (left,top)

def cellNeighbors(cell):
    a,b = cell[0],cell[1]
    return [(a+1,b+1),(a+1,b),(a+1,b-1),(a,b-1),(a-1,b-1),(a-1,b),(a-1,b+1),(a,b+1)]

def cellShadow(point,cell):
    surfCorners = [(0,0),(WINDOWWIDTH,0),(WINDOWWIDTH,WINDOWHEIGHT),(0,WINDOWHEIGHT)]
    if cell[0]*CELLSIZE <= point[0] <= cell[0]*CELLSIZE + CELLSIZE and cell[1]*CELLSIZE <= point[1] <= cell[1]*CELLSIZE + CELLSIZE:
        return surfCorners
    ext = extremeVertices(point,{cell})
    p0 = pointShadow(point,ext[0])
    p1 = pointShadow(point,ext[1])
    result = [p0] + ext + [p1]
    if p0[0] == p1[0] != point[0] or p0[1] == p1[1] != point[1]: return result
    else: 
        news = []
        for c in surfCorners:
            if not lineExists(point,c,{cell}): news.append(c)
        if len(news) == 1: result.append(news[0])
        elif news[0][0] == p1[0] or news[0][1] == p1[1]: result = result + news
        else: result = result + [news[1]] + [news[0]]
    return result

def cellVertices(cell):
    vert = tuple(c*CELLSIZE for c in cell)
    vert1 = (vert[0],vert[1]+CELLSIZE)
    vert2 = (vert[0]+CELLSIZE,vert[1]+CELLSIZE)
    vert3 = (vert[0]+CELLSIZE,vert[1])
    return [vert,vert1,vert2,vert3]


def check(point1,point2,point3):     # checks if point3 is on the line passing through point1, point2
    lineVector = (point2[0]-point1[0],point2[1]-point1[1])
    vector = (point3[0]-point1[0],point3[1]-point1[1])
    determinant = lineVector[0]*vector[1] - lineVector[1]*vector[0]
    if determinant == 0: return 0     # 0 if they are linear
    if determinant > 0: return 1      # 1 if point3 is at one side of the line
    if determinant < 0: return -1     # -1 if point3 is on the other side of the line

def corners(cells):
    result = set()
    verts = allCellVertices(cells)
    for v in verts:
        if len(set(pointNeighbors(v[0],v[1])).intersection(cells)) == 1: result.add(v)
    return result

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, BLACK, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, BLACK, (0, y), (WINDOWWIDTH, y))   


def edgeNeighbors(point1,point2):
    if point1[0] % CELLSIZE != 0 or point1[1] % CELLSIZE != 0 or point2[0] % CELLSIZE != 0 or point2[1] % CELLSIZE != 0: return None
    (x,y) = (point2[0]//CELLSIZE,point2[1]//CELLSIZE)
    (u,v) = (point1[0]//CELLSIZE,point1[1]//CELLSIZE)
    if point1[0] == point2[0] and point1[1] == point2[1] + CELLSIZE: return [(x,y),(x-1,y)]
    if point1[0] == point2[0] and point1[1] == point2[1] - CELLSIZE: return [(u-1,v),(u,v)]
    if point1[1] == point2[1] and point1[0] == point2[0] + CELLSIZE: return [(x,y-1),(x,y)]
    if point1[1] == point2[1] and point1[0] == point2[0] - CELLSIZE: return [(u,v),(u,v-1)]
    return None

def extremeVertices(point,obs):       
    result = []
    for v in corners(obs):
        if len(result) == 2: break
        if not rayPasses(point,v,obs):
            if result == []: result.append(v)
            elif check(point,result[0],v) == 0:
                if result[0][0] == v[0] and (result[0][1] - point[1])*(v[1] - point[1]) < 0: result.append(v)
                elif result[0][1] == v[1] and (result[0][0] - point[0])*(v[0] - point[0]) < 0: result.append(v)
            elif check(point,result[0],v) != 0: result.append(v)
    return result


def lineCells(point1,point2):
    lis = []
    if point1[0] % CELLSIZE == 0 and point1[0] ==point2[0]: return lis
    if point1[1] % CELLSIZE == 0 and point1[1] ==point2[1]: return lis

    dist = WINDOWWIDTH**2 + WINDOWHEIGHT**2
    for n in pointNeighbors(point2[0],point2[1]):
        if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point1[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point1[1])**2 < dist:
            last = n
            dist = (n[0]*CELLSIZE+CELLSIZE/2-point1[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point1[1])**2

    dist = WINDOWWIDTH**2 + WINDOWHEIGHT**2
    for n in pointNeighbors(point1[0],point1[1]):
        if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2 < dist:
            first = n
            dist = (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2
    
    lis.append(first)
    
    while True:
        verticeNeighbs = [cellNeighbors(first)[i] for i in range(8) if i % 2 == 0]
        edgeNeighbs = [cellNeighbors(first)[i] for i in range(8) if i % 2 == 1]
        for n in edgeNeighbs:
            if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2 < dist:
                first = n
                lis.append(first)
                dist = (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2
        if first == last: break
        for n in verticeNeighbs:
            if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2 < dist:
                first = n
                lis.append(first)
                dist = (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2
        if first == last: break

    return lis

def lineExists(point1,point2,obstacle):
    neigh1 = pointNeighbors(point1[0],point1[1])
    neigh2 = pointNeighbors(point2[0],point2[1])
    if point1 == point2: return True

    if point1[0] % CELLSIZE == 0 and point1[1] % CELLSIZE == 0 and point2[0] % CELLSIZE == 0 and point2[1] % CELLSIZE == 0:
        if neigh1[2] == neigh2[1] in obstacle and neigh1[3] == neigh2[0] in obstacle: return False
        if neigh1[1] == neigh2[2] in obstacle and neigh1[0] == neigh2[3] in obstacle: return False
        if neigh1[0] == neigh2[1] in obstacle and neigh1[3] == neigh2[2] in obstacle: return False
        if neigh1[1] == neigh2[0] in obstacle and neigh1[2] == neigh2[3] in obstacle: return False

    if set(lineCells(point1,point2)).intersection(obstacle) != set(): return False
    for v in allCellVertices(obstacle):
        neigh = pointNeighbors(v[0],v[1])
        if check(point1,point2,v) == 0:
            if point1[0] == point2[0] and (point1[1] < v[1] < point2[1] or point2[1] < v[1] < point1[1]):
                    if neigh[0] in obstacle and neigh[3] in obstacle: return False
                    if neigh[1] in obstacle and neigh[2] in obstacle: return False
            
            if point1[1] == point2[1] and (point1[0] < v[0] < point2[0] or point2[0] < v[0] < point1[0]):
                if neigh[0] in obstacle and neigh[1] in obstacle: return False
                if neigh[2] in obstacle and neigh[3] in obstacle: return False
            
            if point1[1] < v[1] < point2[1] or point2[1] < v[1] < point1[1]:
                if neigh[0] in obstacle and neigh[2] in obstacle: return False
                if neigh[1] in obstacle and neigh[3] in obstacle: return False

            if point1[0] < v[0] < point2[0] or point2[0] < v[0] < point1[0]:
                if neigh[0] in obstacle and neigh[2] in obstacle: return False
                if neigh[1] in obstacle and neigh[3] in obstacle: return False
    return True

def linePassesCell(point1,point2,cell):
    vertices = cellVertices(cell)
    if check(point1,point2,vertices[0]) * check(point1,point2,vertices[2]) == -1 or check(point1,point2,vertices[1]) * check(point1,point2,vertices[3]) == -1:
        return True
    else: return False

def neighbors(vertice):
    return [(vertice[0]+CELLSIZE,vertice[1]),(vertice[0],vertice[1]-CELLSIZE),(vertice[0]-CELLSIZE,vertice[1]),(vertice[0],vertice[1]+CELLSIZE)]


def rayPasses(point1,point2,obstacle):
    for cell in obstacle:
        a = (cell[0]*CELLSIZE,cell[1]*CELLSIZE)
        if 0 < point1[0] - a[0] < CELLSIZE and 0 < point1[1] - a[1] < CELLSIZE: return True
        if linePassesCell(point1,point2,cell): 
            if point1[0] - a[0] <= 0 and point1[0] - point2[0] <= 0: return True
            if point1[0] - a[0] >= CELLSIZE and point1[0] - point2[0] >= 0: return True 
            if point1[1] - a[1] <= 0 and point1[1] - point2[1] <= 0: return True
            if point1[1] - a[1] >= CELLSIZE and point1[1] - point2[1] >= 0: return True
            
    for v in allCellVertices(obstacle):
        if point1[0] == point2[0] == v[0] and len(set(pointNeighbors(v[0],v[1])).intersection(obstacle)) == 2:
            lis = list(set(pointNeighbors(v[0],v[1])).intersection(obstacle))
            if lis[0][0] == lis[1][0]: continue
        if point1[1] == point2[1] == v[1] and len(set(pointNeighbors(v[0],v[1])).intersection(obstacle)) == 2:
            lis = list(set(pointNeighbors(v[0],v[1])).intersection(obstacle))
            if lis[0][1] == lis[1][1]: continue
        if check(point1,point2,v) == 0 and v not in corners(obstacle): 
            if (point2[0]-point1[0])*(v[0]-point1[0]) > 0: return True
            if (point2[1]-point1[1])*(v[1]-point1[1]) > 0: return True
    return False


def paintCell(x,y,colour):
    pygame.draw.rect(DISPLAYSURF, colour, (CELLSIZE*x, CELLSIZE*y, CELLSIZE, CELLSIZE))

def pointNeighbors(x,y):
    left = math.floor(x/CELLSIZE)
    top = math.floor(y/CELLSIZE)
    if x % CELLSIZE == 0 and y % CELLSIZE == 0: return [(left,top),(left,top-1),(left-1,top-1),(left-1,top)]
    if x % CELLSIZE != 0 and y % CELLSIZE != 0: return [(left,top)]
    if x % CELLSIZE != 0: return [(left,top),(left,top-1)]     
    if y % CELLSIZE != 0: return [(left,top),(left-1,top)]

def pointShadow(point1,point2):
    if point1 == point2: return None
    
    if point1[0] == point2[0]:
        if point1[1] < point2[1]: return (point1[0],WINDOWHEIGHT)
        else: return (point1[0],0)
        
    if point1[1] == point2[1]:
        if point1[0] < point2[0]: return (WINDOWWIDTH,point1[1])
        else: return (0,point1[1])

    if point1[0] > point2[0] and point1[1] > point2[1]:
        x = (0-point1[1])*(point2[0]-point1[0])//(point2[1]-point1[1]) + point1[0]
        if 0 <= x <= WINDOWWIDTH: return (x,0)
        else: return (0,(0-point1[0])*(point2[1]-point1[1])//(point2[0]-point1[0]) + point1[1])
    
    if point1[0] < point2[0] and point1[1] < point2[1]:
        x = (WINDOWHEIGHT-point1[1])*(point2[0]-point1[0])//(point2[1]-point1[1]) + point1[0]
        if 0 <= x <= WINDOWWIDTH: return (x,WINDOWHEIGHT)
        else: return (WINDOWWIDTH,(WINDOWWIDTH-point1[0])*(point2[1]-point1[1])//(point2[0]-point1[0]) + point1[1])
    
    if point1[0] < point2[0] and point1[1] > point2[1]:
        x = (0-point1[1])*(point2[0]-point1[0])//(point2[1]-point1[1]) + point1[0]
        if 0 <= x <= WINDOWWIDTH: return (x,0)
        else: return (WINDOWWIDTH,(WINDOWWIDTH-point1[0])*(point2[1]-point1[1])//(point2[0]-point1[0]) + point1[1])

    if point1[0] > point2[0] and point1[1] < point2[1]:
        x = (WINDOWHEIGHT-point1[1])*(point2[0]-point1[0])//(point2[1]-point1[1]) + point1[0]
        if 0 <= x <= WINDOWWIDTH: return (x,WINDOWHEIGHT)
        else: return (0,(0-point1[0])*(point2[1]-point1[1])//(point2[0]-point1[0]) + point1[1])


def sunPosition(x):
    return (x,WINDOWHEIGHT - x)


main()