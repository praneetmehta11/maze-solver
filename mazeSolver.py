from tkinter import *
from PIL import ImageTk,Image
import cv2
import collections
from threading import Thread
from tkinter.filedialog import askopenfilename

class MazeSolver:
	def __init__(self,root):
		self.root=root
		self.TITLE="Maze Solver"
		self.MIN_WIDTH=650
		self.url=''
		self.startX=-1
		self.startY=-1
		self.endX=-1
		self.endY=-1
		self.pointSize=3
		self.root.title(self.TITLE)
		self.initComponents()
		self.packComponents()

	def initComponents(self):
		self.canvas=Canvas(self.root)
		self.canvas.update()
		self.frame=Frame(self.root)
		self.scaleGroup = LabelFrame(self.frame, text="Point Size", padx=5)
		self.openMazeButton=Button(self.frame,text="Select Maze",command=self.openMaze)
		self.solveButton=Button(self.frame,text="Solve",state=DISABLED,command=self.solve)
		self.startPointButton=Button(self.frame,text="Start Point",command=self.selectStartPoint)
		self.endPointButton=Button(self.frame,text="End Point",command=self.selectEndPoint)
		self.clearButton=Button(self.frame,text="Clear",command=self.clearMaze)
		self.statusBar=Frame(self.root)
		self.statusLabel=Label(self.statusBar,text="Select Maze Image.",font=("Verdana", 14))
		self.scale = Scale(self.scaleGroup, from_=3, to=20 ,orient=HORIZONTAL ,command=self.changePointSize)
		self.sizeCanvas=Canvas(self.scaleGroup,height=20,width=20)
		self.sizeCanvas.create_rectangle(0,0,20,20,fill="white",outline="white")
		temp=self.pointSize/2
		x=self.pointSize
		self.sizeCanvas.create_rectangle(10-temp,10-temp,10-temp+x,10-temp+x,fill="blue",outline="blue")
		self.scale.set(self.pointSize)

	def packComponents(self):
		self.openMazeButton.pack(side=LEFT,padx=5,pady=5)
		self.startPointButton.pack(side=LEFT,padx=5,pady=5)
		self.endPointButton.pack(side=LEFT,padx=5,pady=5)
		self.clearButton.pack(side=RIGHT,padx=5,pady=5)
		self.solveButton.pack(side=RIGHT,padx=5,pady=5)
		self.scale.pack(side=RIGHT,pady=0)
		self.sizeCanvas.pack(side=RIGHT,padx=5,pady=5)
		self.scaleGroup.pack(side=RIGHT,padx=5,pady=5)
		self.frame.pack()
		self.canvas.pack()
		self.statusLabel.pack(side=LEFT)
		self.statusBar.pack(side=LEFT)
	
	def openMaze(self,event=None):
		try:
			url = askopenfilename()
			if url:
				self.url=url
				self.clearMaze()
		except:
			self.statusLabel.config(text="Unable to open file.")

	def clearMaze(self):
		self.startX=-1
		self.startY=-1
		self.endX=-1
		self.endY=-1
		self.pointSize=3
		self.initMaze(self.url)
		self.startPointButton.config(state=NORMAL)
		self.endPointButton.config(state=NORMAL)
		self.solveButton.config(state=DISABLED)

	def initMaze(self,url):
		self.statusLabel.config(text="Select start point and end point.")
		self.orignal=Image.open(url)
		self.image=ImageTk.PhotoImage(self.orignal)
		self.mazeImage=cv2.imread(url)
		self.mazeHeight,self.mazeWidth,no_channels=self.mazeImage.shape
		if self.mazeWidth<self.MIN_WIDTH:
			ratio=self.MIN_WIDTH/self.mazeWidth
			newH=int(self.mazeHeight*ratio)
			self.image=ImageTk.PhotoImage(self.orignal.resize((self.MIN_WIDTH,newH),Image.ANTIALIAS))
			self.mazeImage = cv2.resize(self.mazeImage,(self.MIN_WIDTH,newH), interpolation = cv2.INTER_AREA)
			self.mazeHeight,self.mazeWidth,no_channels=self.mazeImage.shape
		self.canvas.config(height=self.mazeHeight,width=self.mazeWidth)
		self.canvas.create_image(0,0,image=self.image,anchor=NW)
		self.createMaze()		

	def findPath(self):
		start=(self.startY,self.startX)
		queue = collections.deque([[start]])
		seen = set([start])
		path=[[-1 for i in range(0,self.mazeWidth)] for i in range(0,self.mazeHeight)]
		while queue:
			current = queue.popleft()
			x, y = current[-1]
			for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1),(x+1,y+1), (x-1,y+1), (x+1,y-1), (x-1,y-1)):
				if 0 <= x2 < self.mazeHeight and 0 <= y2 < self.mazeWidth:
					if self.maze[x2][y2] != 0 and (x2, y2) not in seen:
						seen.add((x2, y2))
						queue.append([(x2, y2)])
						path[x2][y2]=(x, y)
						if self.maze[x2][y2]==100:
							return path

	def click(self,event=None,color="blue",point=None):
		x=event.x
		y=event.y
		self.canvas.unbind("<Button-1>")
		tx=ty=sx=sy=self.pointSize
		if x-tx<0:
			tx=x
		if y-ty<0:
			ty=y
		if (x+sx)>self.mazeWidth:
			sx=self.mazeWidth-x
		if (y+sy)>self.mazeHeight:
			sy=self.mazeHeight-y	
		self.canvas.create_rectangle(x-tx/2,y-ty/2,x+sx/2,y+sy/2,fill=color,outline=color)
		
		if point=="start":
			self.startX=x
			self.startY=y
			self.startPointButton.config(state=DISABLED)
		
		if point=="end":
			self.endX=x
			self.endY=y
			self.maze[y][x]=100
			self.endPointButton.config(state=DISABLED)

		if self.startX!=-1 and self.startY!=-1 and self.endX!=-1 and self.endY!=-1:
			self.solveButton.config(state=NORMAL)

	def changePointSize(self,event=None):
		self.sizeCanvas.create_rectangle(0,0,20,20,fill="white",outline="white")
		self.pointSize=self.scale.get()
		temp=self.pointSize/2
		x=self.pointSize
		self.sizeCanvas.create_rectangle(10-temp,10-temp,10-temp+x,10-temp+x,fill="blue",outline="blue")

	
	def selectEndPoint(self):
		color="GREEN"
		self.canvas.bind("<Button-1>",lambda event,c=color,point="end":self.click(event,color,point))		
		
	def selectStartPoint(self):
		color="BLUE"
		self.canvas.bind("<Button-1>",lambda event,c=color,point="start":self.click(event,color,point))		

	def createMaze(self):
		img = cv2.cvtColor(self.mazeImage, cv2.COLOR_BGR2GRAY) 
		ret,self.maze=cv2.threshold(img,120,255,cv2.THRESH_BINARY)

	def solve(self):
		thread = Thread(target = self.solveThread)
		thread.start()

	def solveThread(self):
		self.statusLabel['text']="Trying to find a path."
		self.solveButton.config(state=DISABLED)
		path=self.findPath()
		x,y=self.endY,self.endX
		if path:
			self.statusLabel['text']="Success"	
			while True:
				temp=path[x][y]
				if temp==-1:
					break
				x=temp[0]
				y=temp[1]    
				self.canvas.create_rectangle(y,x,y,x,fill="red",outline="red")
		else:
			self.statusLabel['text']="Path does not exist."
			
if __name__ == '__main__':
	root=Tk()
	mazeSolver=MazeSolver(root)
	root.mainloop()

		