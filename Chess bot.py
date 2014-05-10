from PIL.ImageGrab import grab
from PIL import ImageOps, Image
import os, time, sys, subprocess, win32api, win32con
from numpy import *
from random import randrange

""" 
All coordinates assume a screen resolution of 1920*1080, left monitor
and Chrome maximized with the Bookmarks Toolbar enabled.
board setting extra large
board colour is irrelevant
white always on bottom, always queen on promotion
highlight squares of last move, show coords in board
make your profile pic this image(a solid red 200*200 box) - http://i.imgur.com/wUg1tqY.png
"""

def boardcords(img1, img2):
    img1 = asarray(img1) #what your looking for
    img2 = asarray(img2) #big
    img2y=img2.shape[0]
    img2x=img2.shape[1]
    stopy=img2y-img1.shape[0]+1
    stopx=img2x-img1.shape[1]+1
    for x1 in range(0,stopx):
        for y1 in range(0,stopy):
            x2=x1+img1.shape[1]
            y2=y1+img1.shape[0]
            pic=img2[y1:y2,x1:x2]
            test=pic==img1
            if test.all():
            	print (x1, y1)
            	return x1, y1
    print('board not found')
    sys.exit

#coords
newgame = (260, 654) #the new 1 min game button in the popup(rightside)
learnmore = (213, 554) #The learn more button
movelist1 = (870, 200) #to see when game is found(the move list, each row)
movelist2 = (870, 230)
movelist3 = (870, 250)
profpic = (45, 165) #location of profile pic
#colours
learnmorecolour = (255, 102, 0) #the learn more button colour
profpiccolour = (255, 35, 28) #colour of profile pic(should be solid)
movelight = (247, 236, 116) #light square after moving piece
movedark = (218, 195, 74) #dark square after moving piece
#coords for pics
timer = (540,150,580,170) #box around clock to see if red
boardcheck = (0,0,170,250) #top left corner, up to the bottom right of first square
s = 68 #distance between each square
c = 35 #distance to the centre of the first square
bx, by = boardcords(Image.open('small.png'),grab(boardcheck))
#bx2, by2
board = (bx,by,bx+543,by+543) #exact board dimensions(no black lines)

stockfish = subprocess.Popen('stockfish-dd-64-modern.exe',	universal_newlines=True, \
	stdin=subprocess.PIPE, stdout=subprocess.PIPE,)

houdini = subprocess.Popen('Houdini_15a_x64.exe',	universal_newlines=True, \
	stdin=subprocess.PIPE, stdout=subprocess.PIPE,)

critter = subprocess.Popen('Critter_1.6a_64bit.exe',	universal_newlines=True, \
	stdin=subprocess.PIPE, stdout=subprocess.PIPE,)


def leftDown():
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	time.sleep(0.02*(randrange(1,11)))
		 
def leftUp():
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def mouse_glide_to(x2,y2): #smoothly moves mouse
    x1,y1 = win32api.GetCursorPos()
    t = (0.05*(randrange(1,4)))
    distance_x = x2-x1
    distance_y = y2-y1
    intervals = 15
    for n in range(0, intervals+1):
        win32api.SetCursorPos((int(x1 + n * (distance_x/intervals)),int(y1 + n * (distance_y/intervals))))
        time.sleep(t*1.0/intervals)

def movecords(move): #convert long algebraic to coords(g2g4 > x1,y1,x2,y2)
	test = list(move)
	x1 = (ord(test[0])-97)*s + c
	x2 = (ord(test[2])-97)*s + c
	y1 = (8 - int(test[1]))*s + c
	y2 = (8 - int(test[3]))*s + c
	meinit = (x1,y1)
	mefin = (x2,y2)
	return(meinit, mefin)

def checkend():#checks for the ad that pops up when game finishes to see if its over
	im = grab()
	pixels = im.load()
	if pixels[learnmore] == learnmorecolour:
		win32api.SetCursorPos(newgame)
		leftDown()
		leftUp()
		while True:
			time.sleep(1)
			im = grab()
			pixels = im.load()
			if pixels[movelist1] == (255, 255, 255) and \
			   pixels[movelist2] == (255, 255, 255) and \
			   pixels[movelist3] == (255, 255, 255): #This checks if a new game started(movelist turns white)
			    break
		startgame()

def waiting():
	global line
	while True:
		if side() == turn():
			line += ' ' + oppmove()
			checkend()
			break
		else:
			x1,y1 = win32api.GetCursorPos()
			mouse_glide_to((x1+randrange(-50, 50)),(y1+(randrange(-50, 50))))
			checkend()

def oppmovein(pixels,isx,isy):
	for y in range(isy): #this is a stupid method 
		for x in range(isx): #it require the first point to be found first...
			if pixels[x, y] in (movelight, movedark): #The two possible colours
				if x%s-c == 0 and y%s-c == 0: #this correctly finds the initial position
					x1 = chr(97+(int(((x - c)/s))))
					y1 = int(8- (((y - c)/s)))
					return (x1,y1)

def oppmovefin(pixels, io, isy, isx):
	for y in range(isy):
		for x in range(isx):
			if pixels[x, y] in (movelight, movedark): #The two possible colours
				if x+1%s-c != 0 and (y)%s-c != 0: #x needs +1 for some reason
					x1 = chr(97+((x+1)//s))
					y1 = 8-((y)//s)
					if (x1,y1) != io:
						return (x1,y1)

def oppmove():
	im = grab(board)
	pixels = im.load()
	isx = im.size[0]
	isy = im.size[1]
	io = oppmovein(pixels, isy, isx)
	fo = oppmovefin(pixels, io, isy, isx)
	return str(io[0]) + str(io[1]) + \
	str(fo[0]) + str(fo[1])	

def startgame():
	global line
	global turncount
	turncount = 1
	line = 'position startpos moves'
	if side() == 1: #sometimes it's stupid so you make the first move for it.
		movepiece('e2e4')
		line += ' e2e4'
	else: #need to wait for them to go, sometimes it skips.
		waiting()
	while True:
		if side() == turn():
			go()
			turncount += 1
		else:
			waiting()

def movepiece(move):
	infi = movecords(move)
	ran = randrange(-15, 15)
	init = infi[0]
	init = (init[0] + ran, init[1] + ran)
	final = infi[1]
	final = (final[0] + ran, final[1] + ran)
	mouse_glide_to((board[0] + init[0]), ((board[1] + init[1])))
	leftDown()
	mouse_glide_to((board[0] + final[0]), ((board[1] + final[1])))
	leftUp()
	checkend()

def put(x, command):
	x.stdin.write(command+'\n')
	get(x)

def get(x):
	x.stdin.write('isready\n')
	while True:
		text = x.stdout.readline().strip()
		if text == 'readyok':
			break
		
def bestmove(x):
	if turncount < 10:
		depth = randrange(6,12)
	else:
		depth = randrange(10,14)
	put(x,line)
	x.stdin.write('go depth ' + str(depth)+'\n')
	while True:
		words = (x.stdout.readline().strip()).split()
		try:
			if words[0] == "bestmove":
				return(words[1])
		except:
			continue

def side(): #checks to see if your profile pic is on the top(and therefore you are black)
	im = grab()
	pixels = im.load()
	if pixels[profpic] == (profpiccolour): #This is the colour of your profile pic(mine is red)
		return(0)#black
	else:
		return(1)#white

def turn(): #check timer to see if it's red, and therefore who's turn
	time.sleep(0.03)#don't get ahead of yourself
	r = 0
	count = 0
	image = grab(timer).load()
	for s in range(0, 16):
		for t in range(0, 16):
			pixlr = (image[s, t])[0]
			r += pixlr
			count += 1
	if (r/count) >252:
		return(0)#black
	else:
		return(1)#white

def initiate(x):
	get(x)
	put(x, 'uci')
	put(x, 'setoption name Hash value 512')
	put(x, 'setoption name Threads value 1')
	put(x, 'setoption name Aggressiveness value 120')

def go(): #line is what is input into stockfish before each calc
	global line
	print(line)
	engi = randrange(1,4)
	print(engi)
	if engi == 1:
		move = bestmove(stockfish)
	elif engi == 2:
		move = bestmove(houdini)	
	
	else:
		move = bestmove(critter)
	
	line += ' ' + move
	movepiece(move)

if __name__ == '__main__':
	initiate(stockfish)
	initiate(houdini)
	initiate(critter)
	checkend()
	startgame()
