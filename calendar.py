import os  
import sys
import reportlab  
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.ttfonts import TTFont  
from reportlab.pdfgen.canvas import Canvas  
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import datetime

class Font(object):
	""" Font """
	def __init__(self,ttfFontName,ttfFontFile,size):
		self.folder = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'  
		self.ttfFile = os.path.join(self.folder, ttfFontFile)  
		pdfmetrics.registerFont(TTFont(ttfFontName, self.ttfFile))  

class Block(object):
	""" Block """
	left = 1
	top = 1
	width = 1.5
	height = 1.5
	
	def __init__(self,left,top,width,height):
		""" init """
		self.left = left
		self.top = top
		self.width = width
		self.height = height

	def render(self,c):
		""" render box by walking around counter-clockwise! """
		l = self.left 
		t = self.top
		w = self.width
		h = self.height
		r = l
		b = t + h
		c.line(l*inch,t*inch,r*inch,b*inch)
		t = b
		r = l + w
		b = b
		c.line(l*inch,t*inch,r*inch,b*inch)
		l = r
		b = t - h
		c.line(l*inch,t*inch,r*inch,b*inch)
		t = b
		r = l - w
		c.line(l*inch,t*inch,r*inch,b*inch)

class DayHeaderBlock(Block):
	""" Block with the additional feature of a Day Name """
	#daysOfWeek = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
	daysOfWeek = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
	dayLeft = .1
	dayTop = .1
	dayOfWeek = 0

	def __init__(self,left,top,width,height,dayOfWeek):
		self.dayOfWeek = dayOfWeek
		self.dayLeft = left + width / 2
		self.dayTop = top + 3 *height / 4
		Block.__init__(self,left,top,width,height)

	def render(self,c):
		Block.render(self,c)
		c.setFont('Vera', 12)  
		top = self.dayTop 
		dayOfWeekString = self.daysOfWeek[self.dayOfWeek]
		c.drawCentredString(self.dayLeft*inch, top*inch, dayOfWeekString)  
	
class MonthDayBlock(Block):
	""" Block with the additional feature of Date Number """
	dayOfMonth = 1
	dayLeft = .1
	dayTop = .1
	holidayLeft = 0
	holidayTop = 0
	holiday = None
	moon = None
	windmill = False
	monthsOfYear = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
	daysInMonth = {"Jan":31,"Feb":28,"Mar":31,"Apr":30,"May":31,"Jun":30,"Jul":31,"Aug":31,"Sep":30,"Oct":31,"Nov":30,"Dec":31}

	def __init__(self,left,top,width,height,dayOfMonth,holiday,moon,windmill):
		self.dayOfMonth = dayOfMonth
		self.dayLeft += left 
		self.dayTop += top
		self.holidayLeft = left + width / 2
		self.holidayTop = top + height - .1
		self.holiday = holiday
		self.moon = moon
		self.windmill = windmill
		Block.__init__(self,left,top,width,height)

	def render(self,c):
		Block.render(self,c)
		c.setFont('Vera', 16)  
		top = self.dayTop 
		top += .2		
		windmillLeft = self.left + .05
		windmillTop = self.top + .05
		if self.windmill:
			c.drawImage("windmill.jpg",windmillLeft*inch,windmillTop*inch,1.40*inch,1.10*inch)
		if self.dayOfMonth != -1:
			c.drawString(self.dayLeft*inch, top*inch, str(self.dayOfMonth))  
			if self.holiday is not None:
				c.setFont('Vera', 8)  
				c.drawCentredString(self.holidayLeft*inch,self.holidayTop*inch,self.holiday);
			if self.moon is not None:
				c.setFont('moon_phases',12)
				ll = self.dayLeft + self.width - .4
				if self.moon == "full":
					moonLetter="N"
				elif self.moon == "quarter":
					moonLetter="I"
				elif self.moon == "new":
					moonLetter="A"
				else:	
					moonLetter="Q"
				c.drawString(ll*inch, top*inch,moonLetter)

class Grid(object):
	""" Draws a Grid of Blocks """
	month = 1
	year = 2015
	breadth = 7
	depth = 5
	left = 1
	top = 1
	width = 1
	height = 1
	blocks = []
	days = []
	weekday = 0
	totalDays = 0
	holidays = {}
	pieces = {}
	daysOfWeek = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
	monthsOfYear = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
	daysInMonth = {"Jan":31,"Feb":28,"Mar":31,"Apr":30,"May":31,"Jun":30,"Jul":31,"Aug":31,"Sep":30,"Oct":31,"Nov":30,"Dec":31}

	def __init__(self,left,top,width,height,month,year,holidays,pieces,moons):
		self.left = left
		holiday=""
		moon=""
		windmill=False
		usedWindmillInOppositeCorner=False
		self.top = top
		self.width = width
		self.height = height
		self.month = month
		self.year = year
		self.holidays = holidays
		self.pieces = pieces
		self.moons = moons
		# what weekday is the 1st of the month?
		self.weekday=datetime.date(year,month,1).weekday()
		self.weekday += 1
		if self.weekday >= 7:
			self.weekday=0 
		self.dayOfWeek=self.daysOfWeek[self.weekday]
		self.totalDays = self.daysInMonth[self.monthsOfYear[month-1]]
		
		i = 1
		j = 1
		l = self.left
		t = self.top + .2
		w = self.width
		h = self.height	
		hh = h / 2
		for i in range(self.breadth):
			newDayBlock = DayHeaderBlock(l,t,w,hh,i)
			self.days.append(newDayBlock)
			l+=w
		t += hh 
		dayInWeek = 0
		go=False
		for i in range(self.depth):
			l = self.left
			for j in range(self.breadth):
				if i == (self.depth - 1) and j == (self.breadth - 1) and usedWindmillInOppositeCorner == False:
					#windmill=True
					windmill=False
				elif i == 0 and j == 0:
					#windmill=True
					windmill=False
				else:
					windmill=False
				if dayInWeek == self.weekday:
					go=True
				else:
					dayInWeek += 1
				if go:
					dayOfMonth = i*7+j+1-self.weekday
					if dayOfMonth > self.totalDays:
						newBlock = MonthDayBlock(l,t,w,h,-1,holiday,moon,windmill)
					else:
						windmill = False
						dateOfYear = str(self.month) + "/"  + str(dayOfMonth) +  "/" + str(self.year)
						if dateOfYear in holidays:
							holiday=self.holidays[dateOfYear]
						else:
							holiday=None
						if dateOfYear in moons:
							moon = self.moons[dateOfYear]
						else:
							moon = None
						newBlock = MonthDayBlock(l,t,w,h,i*7+j+1-self.weekday,holiday,moon,windmill)
				else:
					newBlock = MonthDayBlock(l,t,w,h,-1,holiday,moon,windmill)
					usedWindmillInOppositeCorner=True
				self.blocks.append(newBlock)
				l += w
			t += h
				
	def render(self,c):
		""" Render """
		useTop = self.top - 1.0
		useLeft = self.left + (3.5 * self.width)
		piece = pieces[self.monthsOfYear[self.month-1]]
		c.setFont('Vera',18)
		c.drawCentredString(useLeft*inch,useTop*inch,piece)
		useTop = self.top 
		useLeft = self.left + (3.5 * self.width)
		monthyear = self.monthsOfYear[self.month-1] + " " + str(self.year)
		c.setFont('Vera', 32)  
		c.drawCentredString(useLeft*inch, useTop*inch, monthyear)  
		map(lambda x: x.render(c),self.days)
		map(lambda x: x.render(c),self.blocks)

monthsOfYear = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
openfile = open('pieces','r')
line = openfile.readline()
pieces = {}
while line:
	colon=line.find(':')
	pieceMonth=line[0:colon]
	piece=line[colon+1:len(line)-1]
	pieces[pieceMonth]=piece
	line = openfile.readline()
openfile = open('holidays','r')
line = openfile.readline()
holidays = {}
while line:
	colon=line.find(':')
	holiday=line[0:colon]
	holidayDate=line[colon+1:len(line)-1]
	holidays[holidayDate]=holiday
	line = openfile.readline()
openfile = open('moons','r')
line = openfile.readline()
moons = {}
while line:
	colon=line.find(':')
	moon=line[0:colon]
	moonDate=line[colon+1:len(line)-1]
	moons[moonDate]=moon
	line = openfile.readline()
if len(sys.argv) == 2:
	month = int(sys.argv[1])
else:
	month = 1
monthName=monthsOfYear[month-1]
outputName=monthName+".pdf"
canvas = Canvas(outputName,pagesize=(8.5*inch,8.5*inch),bottomup=0)  
f=Font("Vera","Vera.ttf",32)
ff=Font("moon_phases","moon_phases.ttf",32)
#b=Grid(.15,1.54,1.52,1.2,month,2015,holidays,pieces,moons)
b=Grid(.15,1.0,1.0,1.0,month,2017,holidays,pieces,moons)
b.render(canvas)
canvas.showPage()  
canvas.save()  
