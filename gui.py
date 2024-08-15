#this will be a gui calling class for RM2C. All this will do is provide a frontend
#for the RM2C calls, all processing will occur within a subprocess call

#if you are using linux and get a core dump from QT5, try running this dependency install
#sudo apt-get install --reinstall libxcb-xinerama0

import sys, os, subprocess
from pathlib import Path
from functools import partial
try:
	from PyQt5.QtCore import *
	from PyQt5.QtGui import *
	from PyQt5.QtWidgets import *
except:
	print("you must install pyqt5 to use this GUI, run \"pip3 install PyQt5\" then run this file again.")

#rom selection window
class RomSel(QFrame):
	_style = """
	QFrame {
		background-color: #c0c0c0;
		border: 2px solid black;
		border-radius: 9px;
		padding: 15px;
		padding-left: 30px;
		padding-right: 30px;
	}
	QLabel {
		margin: 0px;
		background-color: #ebefdc;
		border: 2px dashed black;
		padding: 2px;
	}
	"""
	def __init__(self, status):
		super().__init__()
		self.setAcceptDrops(True)
		self.layout = QVBoxLayout(self)
		self.setLayout(self.layout)
		self.status = status #use this to update the status obj
		self.setStyleSheet(self._style)
		self.setMinimumHeight(90)
		#add label of text
		self.label = QLabel("Drop in ROM")
		self.layout.addWidget(self.label)
		self.label.setAlignment(Qt.AlignCenter)
		self.rom = None
	def dragLeaveEvent(self, e):
		self.UpdateLabel("Drop in ROM")
	def dragEnterEvent(self, e):
		print("drag event")
		if e.mimeData().hasText():
			e.accept() #leave event is only triggered if event is accepted
			if 'file' in e.mimeData().text() and ('.z64' in e.mimeData().text()):
				self.UpdateLabel(f"ROM {Path(e.mimeData().text()[8:])} detected")
			else:
				self.UpdateLabel("File is not type .z64, please drop in valid ROM")
	def dropEvent(self, e):
		if 'file' in e.mimeData().text() and ('' in e.mimeData().text()):
			self.rom = Path(e.mimeData().text()[8:].strip())
			self.UpdateStatus(f"ROM accepted, {self.rom.name} is ready to be extracted")
	def UpdateStatus(self, s):
		self.status.setText(s)
	def UpdateLabel(self, s):
		self.label.setText(s)
	def ExportDat(self, options, textOpts, e):
		if not self.rom:
			self.UpdateStatus("Please drop in valid ROM file before extracting")
		else:
			print(textOpts)
			opts = [f"{k}={v.isChecked()}" for k,v in options.items()]
			ret = subprocess.run([f"python3", "RM2C.py", f"rom={self.rom}", *opts], capture_output = True)
			print(ret.stderr, ret.args)
			print(self.rom)

#text input options
class OptInput(QFrame):
	def __init__(self, label, opts, entrytip = None):
		super().__init__()
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		self.layout.addWidget(QLabel(label))
		self.options = dict()
		for o in opts:
			btn = QRadioButton(o, parent = self)
			self.options[o] = btn
			self.layout.addWidget(btn)
			btn.clicked.connect(partial(self.UpdateEntry, btn))
			btn.setChecked(1)
		#create radio button for text input field
		btn = QRadioButton("list entry", parent = self)
		self.options["list"] = btn
		self.layout.addWidget(btn)
		btn.clicked.connect(partial(self.UpdateEntry, btn))
		self.Entry = QLineEdit("enter a list", parent = self)
		self.layout.addWidget(self.Entry)
		self.Entry.hide()
	def UpdateEntry(self, btn, *args):
		if "list" in btn.text():
			if btn.isChecked():
				self.Entry.show()
			else:
				self.Entry.hide()
		else:
			if btn.isChecked():
				self.Entry.hide()
	def EvalOpt(self):
		pass

#root window that holds all the other stuff
class Window(QWidget):
	def __init__(self):
		super().__init__()
		self.resize(400, 200) #idk
		self.setWindowTitle("RM2C Front - End GUI")
		font = QFont()
		font.setPointSize(11)
		self.setFont(font)
		self.layout = QVBoxLayout(self)
		self.setLayout(self.layout)
		self.options = dict()
	def AddLayout(self, LY, parent = None):
		if parent is not None:
			parent.addLayout(LY)
		else:
			self.layout.addLayout(LY)
		return LY
	def AddWidget(self, widg, LY = None, **kwargs):
		if LY is None:
			self.layout.addWidget(widg, *kwargs.values())
		else:
			LY.addWidget(widg, *kwargs.values())
	def AddOption(self, GUIname, OPTname, parent = None, radio = None):
		if radio:
			widg = QRadioButton(GUIname, parent = parent)
		else:
			widg = QCheckBox(GUIname, parent = parent)
		self.options[OPTname] = widg
		return widg
	def UpdateStatus(self, s):
		self.status.setText(s)
	#if condition, then send condition, else send None
	#(default would be 0/False etc., but I want None specifically)
	def ArgSend(self, cond):
		if cond:
			return cond
		return None
	def clean(varStr): return re.sub('\W|^(?=\d)','_', varStr)

#style sheets are basically CSS, aka evil
def EmbossStyleSheet(widget):
	style = """
	background-color: #dee5da;
	border: 2px solid black;
	padding: 2px;
	"""
	widget.setStyleSheet(style)
	font = QFont()
	font.setPointSize(11)
	widget.setFont(font)

def ButtonStyleSheet(widget):
	style = """QPushButton {
    border: 2px solid black;
    border-radius: 6px;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
    min-width: 80px;
	}
	QPushButton:pressed {
	    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
	                                      stop: 0 #dadbde, stop: 1 #f6f7fa);
	}
	"""
	widget.setStyleSheet(style)

def BoldStyleSheet(widget):
	style = """
	QAbstractButton {
		background-color: #ebefdc;
		border: 1px solid black;
		margin: 2px;
		padding: 4px;
	}
	QLabel {
		border: 0px;
		margin: 0px;
		padding: 0px;
		padding-bottom: 3px;
	}
	"""
	widget.setStyleSheet(style)
	font = QFont()
	font.setPointSize(11)
	font.setBold(True)
	widget.setFont(font)

def FrameStyleSunken(widget):
	style = """
	border: 3px solid black;
	border-radius: 2px;
	background-color: #c0c0c0;
	margin: 4px;
	"""
	widget.setStyleSheet(style)

def FrameStyleRaised(widget):
	style = """
	background-color: #e0e0e0;
	border: 1px dotted black;
	padding: 1px;
	"""
	widget.setStyleSheet(style)

#options, label, [((option name, option var), (row, col), radio)]
Options = [
	[	"Export Filters",
		(("Water Only", "WaterOnly"), (0, 0), 1),
		(("Object Only", "ObjectOnly"), (0, 1), 1),
		(("Music Only", "MusicOnly"), (0, 2), 1),
	],
	[	"Export Extras",
		(("Export Text", "Text"), (1, 0), 0),
		(("Export Title", "Title"), (1, 1), 0),
		(("Export Textures", "Textures"), (1, 2), 0),
		(("Export Inst Banks", "Sound"), (1, 3), 0),
	],
	[	"Change Export Methodology",
		(("Inherit Prev Export", "Inherit"), (2, 0), 0),
		(("Is editor ROM", "editor"), (2, 1), 0),
	]
]

def InitGui():
	#create window
	app = QApplication([])
	wnd = Window()
	#add widgets
	Run = QPushButton("Extract C data from ROM")
	#status
	sts = "Select Options, drop in ROM, then hit Run"
	Status = QLabel(sts)
	wnd.status = Status
	Status.setFixedHeight(30)
	Status.setAlignment(Qt.AlignCenter)

	#frame container for options
	RootF = QFrame()
	FrameStyleSunken(RootF)

	#ROM selection frame
	rom = RomSel(Status)

	#layouts
	sts = QHBoxLayout()
	top = QHBoxLayout()
	TextOptions = QHBoxLayout()
	optionsD = QHBoxLayout()
	options = dict()
	bot = QHBoxLayout()

	wnd.AddLayout(sts)
	wnd.AddLayout(top)
	wnd.AddLayout(TextOptions)
	wnd.AddLayout(optionsD)
	wnd.AddLayout(bot)

	#add widgets to layouts
	wnd.AddWidget(RootF, LY = optionsD)
	wnd.AddWidget(Status, LY = sts)
	wnd.AddWidget(Run, LY = bot)
	wnd.AddWidget(rom, LY = top)

	ButtonStyleSheet(Run)

	#set frame layout to contain options
	optionsBox = QHBoxLayout()
	RootF.setLayout(optionsBox)

	#various options, each has their own frame
	#should really be its own class made with some constructor or something but this
	#is just fine I guess
	frames = dict()
	for j, OptionGroup in enumerate(Options):
		frame = frames.get(j, QFrame())
		frames[j] = frame
		opt = options.get(j, QVBoxLayout())
		options[j] = opt
		wnd.AddWidget(lbl := QLabel(OptionGroup[0]), LY = opt)
		BoldStyleSheet(lbl)
		lbl.setSizePolicy(1, 0)
		for o, pos, radio in OptionGroup[1:]:
			#each row has its own QFrame
			widg = wnd.AddOption(*o, parent = frame, radio = radio)
			#style option
			BoldStyleSheet(widg)
			#kwargs don't work for add layout, they need to be in order
			#I unroll them in the class, and just use the naming so it
			#is clear what is going on
			wnd.AddWidget(widg, LY = opt)

	#in order to create a frame around a widget, this hierarchy is needed
	#frame has a layout set called X
	#things within frame are added as widgets to layout X
	#frame is added as a widget to a larger layout, or as a child of window

	#frame needs to have set layout, this will manage the layout
	#of all the widgets added to it, which will keep them within the frame
	for f, opt in zip(frames.values(), options.values()):
		# f.setFrameShape(QFrame.Box)
		# f.setLineWidth(1)
		f.setLayout(opt)
		FrameStyleRaised(f)
		wnd.AddWidget(f, LY = optionsBox)

	#add in text options
	textOpts = []
	wnd.AddWidget(opt := OptInput("levels", ["all"]), LY = TextOptions)
	opt.setSizePolicy(0, 1)
	textOpts.append(opt)
	wnd.AddWidget(opt := OptInput("actors", ["all", "old", "new"]), LY = TextOptions)
	opt.setSizePolicy(0, 1)
	textOpts.append(opt)
	wnd.AddWidget(opt := OptInput("objects", ["all", "new"]), LY = TextOptions)
	opt.setSizePolicy(0, 1)
	textOpts.append(opt)

	#add functions
	Run.clicked.connect( partial(rom.ExportDat, wnd.options, textOpts) )

	return wnd, app

def RunGui(window, app):
	window.show()
	sys.exit(app.exec_())

def Main():
	#make GUI
	wnd, app = InitGui()
	#run GUI
	RunGui(wnd, app)

if __name__== '__main__':
	Main()
