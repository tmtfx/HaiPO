#!/boot/system/bin/python3
from Be import BApplication, BWindow, BView, BMenu,BMenuBar, BMenuItem, BSeparatorItem, BMessage, window_type, B_NOT_RESIZABLE, B_CLOSE_ON_ESCAPE, B_QUIT_ON_WINDOW_CLOSE, BButton, BTextView, BTextControl, BAlert, BListItem,BMenuField, BListView, BScrollView,BRect, BBox, BFont, InterfaceDefs, BPath, BDirectory, BEntry, BStringItem, BFile, BStringView,BCheckBox,BTranslationUtils, BBitmap, AppDefs, BTab, BTabView, BNodeInfo, BMimeType, BScrollBar,BPopUpMenu,BScreen,BStatusBar,BPoint,BNode

# from Be.View import *
from Be.View import B_FOLLOW_NONE,set_font_mask,B_WILL_DRAW,B_NAVIGABLE,B_FULL_UPDATE_ON_RESIZE,B_FRAME_EVENTS,B_PULSE_NEEDED,B_FOLLOW_ALL_SIDES,B_FOLLOW_TOP,B_FOLLOW_LEFT_RIGHT,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT,B_FOLLOW_RIGHT,B_FOLLOW_TOP_BOTTOM
from Be.Menu import menu_info,get_menu_info
from Be.FindDirectory import *
from Be.Alert import alert_type
#from Be.InterfaceDefs import border_style,orientation
from Be.ListView import list_view_type
from Be.AppDefs import *
from Be.Font import be_plain_font, be_bold_font, font_height
from Be.Application import *
from Be.Menu import menu_layout
from Be.Entry import entry_ref, get_ref_for_path
from Be.FilePanel import *

from Be.InterfaceDefs import *
from Be.StorageDefs import node_flavor
from Be.TypeConstants import *
from Be.Accelerant import display_mode
from Be.GraphicsDefs import rgb_color
from Be.TabView import tab_side

import configparser,struct,threading,os,polib,re,datetime,time#,babel
from distutils.spawn import find_executable
from subprocess import Popen,STDOUT,PIPE
import socket,pickle,unicodedata
from threading import Thread
from babel import Locale
Config=configparser.ConfigParser()
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# global showspell
# showspell=True
# tm=True



version='HaiPO 2.0 beta'
(appname,ver,state)=version.split(' ')
class ScrollView:
	HiWhat = 53 #Doppioclick
	SectionSelection = 54

	def __init__(self, rect, name):
		self.lv = BListView(rect, name, list_view_type.B_SINGLE_SELECTION_LIST)
		self.lv.SetResizingMode(B_FOLLOW_ALL_SIDES)
		self.lv.SetSelectionMessage(BMessage(self.SectionSelection))
		self.lv.SetInvocationMessage(BMessage(self.HiWhat))
		self.sv = BScrollView(name, self.lv,B_FOLLOW_NONE,0,True,True,border_style.B_FANCY_BORDER)
		self.sv.SetResizingMode(B_FOLLOW_ALL_SIDES)
	def Clear(self):
		self.lv.DeselectAll()
		self.lv.MakeEmpty()
def Ent_config():
	perc=BPath()
	find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
	datapath=BDirectory(perc.Path()+"/HaiPO2")
	ent=BEntry(datapath,perc.Path()+"/HaiPO2")
	if not ent.Exists():
		datapath.CreateDirectory(perc.Path()+"/HaiPO2", datapath)
	ent.GetPath(perc)
	confile=BPath(perc.Path()+'/config.ini',None,False)
	ent=BEntry(confile.Path())
	return(ent,confile.Path())

class KListView(BListView):
	def __init__(self,frame, name,type):#,align,flags):
		BListView.__init__(self, frame, name, type,B_FOLLOW_RIGHT|B_FOLLOW_TOP)#, align, flags)
	def KeyDown(self,char,bytes):
		if ord(char) == 127:
			delmsg=BMessage(431110173)
			delmsg.AddString("sugj",self.ItemAt(self.CurrentSelection()).Text())#check if it needs encoding
			be_app.WindowAt(0).PostMessage(delmsg)
			self.RemoveItem(self.ItemAt(self.CurrentSelection()))
		# return BListView.KeyDown(self,char,bytes)

class ScrollSugj:
	HiWhat = 141# Doubleclick --> paste to trnsl TextView
	def __init__(self, rect, name):
		self.lv = KListView(rect, name, list_view_type.B_SINGLE_SELECTION_LIST)#,B_FOLLOW_LEFT_RIGHT|B_FOLLOW_BOTTOM,B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_FRAME_EVENTS)#B_FOLLOW_ALL_SIDES
		msg = BMessage(self.HiWhat)
		self.lv.SetInvocationMessage(msg)
		self.sv = BScrollView('ScrollSugj', self.lv, B_FOLLOW_RIGHT|B_FOLLOW_TOP|B_FOLLOW_RIGHT, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, True,True, border_style.B_FANCY_BORDER)#B_FOLLOW_ALL_SIDES
		
	def SelectedText(self):
		return self.lv.ItemAt(self.lv.CurrentSelection()).Text()

	def Clear(self):
		self.lv.DeselectAll()
		self.lv.MakeEmpty()
		#while self.lv.CountItems()>0:
		#		self.lv.RemoveItem(self.lv.ItemAt(0))

class TranslatorComment(BWindow):
	kWindowFrame = BRect(150, 150, 450, 300)
	kWindowName = "Translator comment"
	
	#def __init__(self,listindex,indextab,item,encoding):
	def __init__(self,listindex,item):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		ix=bounds.left
		iy=bounds.top
		fx=bounds.right
		fy=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		self.tcommentview=BTextView(BRect(4,4,fx-4,fy-50),"commentview",BRect(4,4,fx-12,fy-48),B_FOLLOW_ALL_SIDES)
		self.underframe.AddChild(self.tcommentview,None)
		kButtonFrame = BRect(fx-150, fy-40, fx-10, fy-10)
		kButtonName = "Save comment"
		self.savebtn = BButton(kButtonFrame, kButtonName, kButtonName, BMessage(5252))
		self.underframe.AddChild(self.savebtn,None)
		self.item=item
		# self.indextab=indextab
		self.listindex=listindex
		if self.item.tcomment!="":
			self.tcommentview.SetText(self.item.tcomment,None)#.encode(self.encoding))
		
	def Save(self):
		bckpmsg=BMessage(16893)
		cursel=be_app.WindowAt(0)
		bckpmsg.AddInt8('savetype',3)
		bckpmsg.AddInt32('tvindex',self.listindex)
		#bckpmsg.AddInt32('tabview',self.indextab)
		bckpmsg.AddString('tcomment',str(self.item.tcomment))#.encode(self.encoding)))#.decode(self.encoding)) ################### TODO verificare se va bene encode utf-8
		bckpmsg.AddString('bckppath',cursel.backupfile)
		be_app.WindowAt(0).PostMessage(bckpmsg)
		

	def MessageReceived(self, msg):
		if msg.what == 5252:
			self.item.tcomment=self.tcommentview.Text()#.decode(self.encoding)
			self.Save()
			#BApplication.be_app.WindowAt(0).postabview.Select(self.indextab)
			be_app.WindowAt(0).sourcestrings.lv.DeselectAll()
			be_app.WindowAt(0).sourcestrings.lv.Select(self.listindex)
			self.Quit()
		else:	
			return BWindow.MessageReceived(self, msg)

class translationtabview(BTabView):
	def __init__(self,frame,name,superself):#width,risizingMode,flags,
		self.superself=superself
		BTabView.__init__(self,frame,name,button_width.B_WIDTH_AS_USUAL,B_FOLLOW_LEFT_RIGHT)#B_FOLLOW_TOP_BOTTOM|B_FOLLOW_RIGHT)#width,risizingMode,flags
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
	def MouseDown(self,point):
		numtabs=len(self.superself.listemsgstr)
		
		gg=0
		while gg<numtabs:
			if (point[0]>=self.TabFrame(gg)[0]) and (point[0]<=self.TabFrame(gg)[2]) and (point[1]>=self.TabFrame(gg)[1]) and (point[1]<=self.TabFrame(gg)[3]):
				self.superself.srctabview.Select(gg)
			gg=gg+1
		be_app.WindowAt(0).PostMessage(12343)
		BTabView.MouseDown(self,point)
		self.superself.listemsgstr[self.Selection()].trnsl.MakeFocus()
		lngth=self.superself.listemsgstr[self.Selection()].trnsl.TextLength()
		self.superself.listemsgstr[self.Selection()].trnsl.Select(lngth,lngth)
		self.superself.listemsgstr[self.Selection()].trnsl.ScrollToSelection()

class sourcetabview(BTabView):
	def __init__(self,frame,name,superself):#,width,risizingMode,flags
		self.superself=superself
		BTabView.__init__(self,frame,name,button_width.B_WIDTH_AS_USUAL,B_FOLLOW_LEFT_RIGHT)#B_FOLLOW_TOP_BOTTOM|B_FOLLOW_LEFT) #,width,risizingMode,flags
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
	def MouseDown(self,point):
		numtabs=len(self.superself.listemsgstr)
		gg=0
		while gg<numtabs:
			if (point[0]>=self.TabFrame(gg)[0]) and (point[0]<=self.TabFrame(gg)[2]) and (point[1]>=self.TabFrame(gg)[1]) and (point[1]<=self.TabFrame(gg)[3]):
				self.superself.transtabview.Select(gg)
			gg=gg+1
		be_app.WindowAt(0).PostMessage(12343)
		BTabView.MouseDown(self,point)
		self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.MakeFocus()
		lngth=self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.TextLength()
		self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.Select(lngth,lngth)
		self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.ScrollToSelection()

class srctabbox(BBox):
	def __init__(self,playground1,name,altece):
		self.name = name
		BBox.__init__(self,BRect(0,0,playground1[2]-playground1[0],playground1[3]-playground1[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.hsrc = playground1[3] - playground1[1] - altece
		self.src = srcTextView(BRect(playground1[0],playground1[1],playground1[2]-playground1[0]-18,playground1[3]-playground1[1]),name+'_source_BTextView',BRect(5.0,5.0,playground1[2]-30,playground1[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.src.MakeEditable(False)
		self.AddChild(self.src,None)
		bi,bu,bo,ba = playground1
		self.scrollbsrc=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.src,0.0,0.0,B_VERTICAL)
		self.AddChild(self.scrollbsrc,None)

class trnsltabbox(BBox):
	def __init__(self,playground2,name,altece,superself): #TODO rimuovere altece non viene usato
		self.name = name
		BBox.__init__(self,BRect(0,0,playground2[2]-playground2[0],playground2[3]-playground2[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.trnsl = EventTextView(superself,BRect(playground2[0],playground2[1],playground2[2]-playground2[0]-18,playground2[3]-playground2[1]),name+'_translation_BTextView',BRect(5.0,5.0,playground2[2]-30,playground2[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.trnsl.MakeEditable(True)
		self.AddChild(self.trnsl,None)
		bi,bu,bo,ba = playground2
		self.scrollbtrans=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.trnsl,0.0,0.0,orientation.B_VERTICAL)#TODO: get scrollbarwidth not -20 or whatever
		self.AddChild(self.scrollbtrans,None)

class contexttabbox(BBox):
	def __init__(self,frame,superself):
		name="context"
		self.name = name
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.context = BTextView(BRect(frame[0],frame[1],frame[2]-frame[0]-18,frame[3]-frame[1]),name+'_context_BTextView',BRect(5.0,5.0,frame[2]-30,frame[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.context.MakeEditable(False)
		self.AddChild(self.context,None)
		bi,bu,bo,ba = frame
		self.scrollbcont=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.context,0.0,0.0,orientation.B_VERTICAL)#TODO: get scrollbarwidth not -20 or whatever
		self.AddChild(self.scrollbcont,None)
		
class commenttabbox(BBox):
	def __init__(self,frame,superself):
		name="comment"
		self.name = name
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.comment = BTextView(BRect(frame[0],frame[1],frame[2]-frame[0]-18,frame[3]-frame[1]),name+'_comment_BTextView',BRect(5.0,5.0,frame[2]-30,frame[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.comment.MakeEditable(False)
		self.AddChild(self.comment,None)
		bi,bu,bo,ba = frame
		self.scrollbcom=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.comment,0.0,0.0,orientation.B_VERTICAL)#TODO: get scrollbarwidth not -20 or whatever
		self.AddChild(self.scrollbcom,None)

class tcommenttabbox(BBox):
	def __init__(self,frame,superself):
		name="tcomment"
		self.name = name
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.tcomment = BTextView(BRect(frame[0],frame[1],frame[2]-frame[0]-18,frame[3]-frame[1]),name+'_comment_BTextView',BRect(5.0,5.0,frame[2]-30,frame[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.tcomment.MakeEditable(False)
		self.AddChild(self.tcomment,None)
		bi,bu,bo,ba = frame
		self.scrollbtcom=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.tcomment,0.0,0.0,orientation.B_VERTICAL)#TODO: get scrollbarwidth not -20 or whatever
		self.AddChild(self.scrollbtcom,None)

class previoustabbox(BBox):
	def __init__(self,frame,superself):
		name="prev_msgid"
		self.name = name
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.prev = BTextView(BRect(frame[0],frame[1],frame[2]-frame[0]-18,frame[3]-frame[1]),name+'_comment_BTextView',BRect(5.0,5.0,frame[2]-30,frame[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.prev.MakeEditable(False)
		self.AddChild(self.prev,None)
		bi,bu,bo,ba = frame
		self.scrollbprev=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.prev,0.0,0.0,orientation.B_VERTICAL)#TODO: get scrollbarwidth not -20 or whatever
		self.AddChild(self.scrollbprev,None)

class MsgStrItem(BListItem):
	nocolor = (0, 0, 0, 0)
	####  states table
	untranslated = 0
	translated = 1
	fuzzy = 2
	obslete = 3
	hasplural = False
	frame=[0,0,0,0]
	tosave=False
	txttosave=""	# nel lungo termine eliminare
	txttosavepl=[]  # nel lungo termine eliminare
	dragcheck=False
	comments=""
	context=""
	mycolors= {"untranslated":rgb_color(),"translated":rgb_color(),"fuzzy":rgb_color(),"obs_select":rgb_color(),"obsolete":rgb_color(),"clear":rgb_color()}
	mycolors["untranslated"].blue=255
	mycolors["fuzzy"].red=153
	mycolors["fuzzy"].green=153
	mycolors["obs_select"].red=150
	mycolors["obs_select"].green=75
	mycolors["obsolete"].red=150
	mycolors["obsolete"].green=75
	mycolors["clear"].red=255
	mycolors["clear"].green=255
	mycolors["clear"].blue=255
	mycolors["clear"].alpha=255
	
	def __init__(self, msgids,msgstrs,entry,comments,context,state,encoding,plural):
		if plural:
			self.text = msgids[0]#.encode(encoding)
			self.textpl = msgids[1]#.encode(encoding)
		else:
			self.text = msgids#.encode(encoding)
		self.comments = comments
		self.context = context
		self.msgids = msgids
		self.msgstrs = msgstrs
		self.state = state
		self.hasplural = plural
		self.previous=False
		self.previousmsgs=[]
		self.tcomment=""
		self.linenum=None
		self.entry=entry
		BListItem.__init__(self)

	def DrawItem(self, owner, frame,complete):
		#self.frame = frame
		#complete = True
		if self.IsSelected() or complete: # 
			#color = (200,200,200,255)
			owner.SetHighColor(200,200,200,255)
			owner.SetLowColor(200,200,200,255)
			owner.FillRect(frame)
			if self.state == self.untranslated:
				self.color=self.mycolors["untranslated"]
			elif self.state == self.translated:
				self.color=self.mycolors["translated"]
			elif self.state == self.fuzzy:
				self.color=self.mycolors["fuzzy"]
			elif self.state == self.obsolete:
				self.color=self.mycolors["obs_select"]

		if self.state == self.untranslated:
				self.color=self.mycolors["untranslated"]
		elif self.state == self.translated:
				self.color=self.mycolors["translated"]
		elif self.state == self.fuzzy:
				self.color=self.mycolors["fuzzy"]
		elif self.state == self.obsolete:
				self.color=self.mycolors["obsolete"]
		
		if self.hasplural:
			owner.MovePenTo(frame.left+5,frame.bottom-5)
			self.font = be_bold_font
			tempcolor = rgb_color()#(200,0,0,0)
			tempcolor.red=200
			owner.SetHighColor(tempcolor)
			owner.SetFont(self.font)
			xtxt='Pl >>'
			owner.DrawString(xtxt,None)
			ww=self.font.StringWidth(xtxt)
			owner.SetHighColor(self.color)
			self.font = be_plain_font
			owner.SetFont(self.font)
			owner.MovePenTo(frame.left+ww+10,frame.bottom-5)
			owner.DrawString(self.text,None)
		else:
			owner.SetHighColor(self.color)
			owner.MovePenTo(frame.left+5,frame.bottom-5)
			owner.DrawString(self.text,None)
			owner.SetLowColor(self.mycolors["clear"])
		#owner.StrokeTriangle((float(frame[2]-10),float(frame[3]+3)),(frame[2]-2,frame[3]+3),(frame[2]-6,frame[3]+7.5));#,B_SOLID_HIGH
		#should I? return BListItem.DrawItem(self, owner, frame,complete)
	
	def SetLineNum(self,value):
		self.linenum=value
		
	def SetPreviousMsgs(self,msgs):
		self.previousmsgs.append(msgs)
	
	def SetPrevious(self,bool):
		self.previous=bool

	def SetTranslatorComment(self,tcomment):
		self.tcomment=tcomment
		
	def Text(self):
		return self.text

class EventTextView(BTextView):
	global comm
	def __init__(self,superself,frame,name,textRect,resizingMode,flags):
		self.superself=superself
		self.oldtext=""
#		self.telptst=self.oldtext
		self.oldtextloaded=False
		self.tosave=False
		fin=be_plain_font
		fin.SetSize(superself.oldsize)
		color=rgb_color()
		BTextView.__init__(self,frame,name,textRect,fin,color,resizingMode,flags)
		self.mousemsg=struct.unpack('!l', b'_MMV')[0]
		self.dragmsg=struct.unpack('!l', b'MIME')[0]
		self.dragndrop = False
		self.event= threading.Event()
		self.SetStylable(1)
		self.evstile=[]
		self.analisi=[]
		self.analyzetxt=[]
		self.pop = BPopUpMenu('popup')
		
	def Save(self):
		#cursel=self.superself.editorslist[self.superself.postabview.Selection()]
		thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
		thisBlistitem.tosave=True
		tabs=len(self.superself.listemsgstr)-1
		bckpmsg=BMessage(16893)
		bckpmsg.AddInt8('savetype',1)
		bckpmsg.AddInt32('tvindex',self.superself.sourcestrings.lv.CurrentSelection())
		bckpmsg.AddInt8('plurals',tabs)
		#bckpmsg.AddInt32('tabview',self.superself.postabview.Selection())
		if tabs == 0:
			thisBlistitem.txttosave=self.Text()
			#thisBlistitem.msgstrs=self.Text().decode(self.superself.encoding)
			thisBlistitem.msgstrs=self.Text()#.decode(self.superself.encoding)#let's do utf-8 by default?
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
		else:
			thisBlistitem.txttosavepl=[]
			thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
			thisBlistitem.msgstrs=[]
			#thisBlistitem.msgstrs.append(self.superself.listemsgstr[0].trnsl.Text().decode(self.superself.encoding))
			thisBlistitem.msgstrs.append(self.superself.listemsgstr[0].trnsl.Text())#.decode(self.superself.encoding))
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
			cox=1
			while cox < tabs+1:
				#thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text().decode(self.superself.encoding))
				thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text())#.decode(self.superself.encoding))
				thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
				bckpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgstr[cox].trnsl.Text())
				cox+=1
		print("da eventtextview.Save backupfile:",self.superself.backupfile)
		bckpmsg.AddString('bckppath',self.superself.backupfile)
		be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
		#self.superself.infoprogress.SetText(str(self.superself.pofile.percent_translated())) #reinsert if something doesn't work properly but it should write in 16892/3
		self.superself.progressinfo.Update(1,None,str(self.superself.pofile.percent_translated())+"%")

	def checklater(self,name,oldtext,indexBlistitem):
			mes=BMessage(112118)
			#mes.AddInt8('cursel',cursel)#TODO: rimuovere non serve
			mes.AddInt32('indexBlistitem',indexBlistitem)
			mes.AddString('oldtext',oldtext)
			self.event.wait(0.1)
			be_app.WindowAt(0).PostMessage(mes)


	def MouseUp(self,point):
		self.superself.drop.acquire()
		if self.dragndrop:
			#cursel=self.superself.postabview.Selection()
			#selection=self.superself.editorslist[cursel]
			indexBlistitem=self.superself.sourcestrings.lv.CurrentSelection()
			name=time.time()
			BTextView.MouseUp(self,point)
			Thread(target=self.checklater,args=(str(name), self.Text(),indexBlistitem)).start()
			#thread.start_new_thread( self.checklater, (str(name), self.Text(),cursel,indexBlistitem,) )
			self.dragndrop = False
			self.superself.drop.release()
			return
		self.superself.drop.release()
		if showspell:
			ubi1=0
			ubi2=0
			self.GetSelection(ubi1,ubi2)
			if ubi1 == ubi2:
				self.FindWord(ubi1,ubi1,ubi2)
			perau = self.Text()[ubi1:ubi2]
			if len(self.analyzetxt)>0:
				for item in self.analyzetxt:
					if item.word == perau:
						menus=[]
						sut=len(item.sugg)
						ru=0
						while ru <sut:
							menus.append((ru, item.sugg[ru]))
							ru+=1
						self.pop = BPopUpMenu('popup')
						for aelem in menus:
							msz = BMessage(9631)
							msz.AddInt16('index',aelem[0])
							msz.AddString('sugg',aelem[1])
							msz.AddString('sorig',perau)
							msz.AddInt32('indi',ubi1)
							msz.AddInt32('indf',ubi2)
							self.pop.AddItem(BMenuItem(aelem[1], msz))
						pointo=self.PointAt(ubi2)
						point = self.ConvertToScreen(pointo[0])
						x = self.pop.Go(point, 1)
						if x:
							self.Looper().PostMessage(x.Message())
					else:
						fres= perau.find(item.word)
						if fres>-1:
							menus=[]
							sut=len(item.sugg)
							ru=0
							while ru <sut:
								menus.append((ru, item.sugg[ru]))
								ru+=1
							self.pop = BPopUpMenu('popup')
							for aelem in menus:
								msz = BMessage(9631)
								msz.AddInt16('index',aelem[0])
								msz.AddString('sugg',aelem[1])
								msz.AddString('sorig',perau[:fres])
								msz.AddInt32('indi',ubi1+fres)
								msz.AddInt32('indf',ubi1+fres+len(item.word))
								self.pop.AddItem(BMenuItem(aelem[1], msz))	
							pointo=self.PointAt(ubi1+fres+len(item.word))
							point = self.ConvertToScreen(pointo[0])
							x = self.pop.Go(point, 1)
							if x:
								self.Looper().PostMessage(x.Message())
			#else:
				#print "there's no analyzetxt"

		return BTextView.MouseUp(self,point)

	def MessageReceived(self, msg):
			
		if msg.what in [B_CUT,B_PASTE]:
			#cursel=self.superself.editorslist[self.superself.postabview.Selection()]
			thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
			thisBlistitem.tosave=True
			self.tosave=True
			
		if msg.what == self.mousemsg:
			try:
				mexico=msg.FindMessage('be:drag_message')
				self.superself.drop.acquire()
				self.dragndrop=True
				self.superself.drop.release()
				self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.MakeFocus()
			except:
				pass

		return BTextView.MessageReceived(self,msg)

	def KeyDown(self,char,bytes):
		try:
			ochar=ord(char)
			print(ochar,B_PAGE_DOWN)
			if ochar in (B_DOWN_ARROW,B_UP_ARROW,10,B_PAGE_UP,B_PAGE_DOWN,10,49,50,51,52,53): #B_ENTER =10?
				self.superself.sem.acquire()
				value=self.superself.modifier #CTRL pressed
				shrtctvalue=self.superself.shortcut
				self.superself.sem.release()
				item=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
				hasplural=item.hasplural
				kmesg=BMessage(130550)
				if ochar == B_DOWN_ARROW:
					if value:
						# one element down
						if hasplural:
							lung=len(self.superself.listemsgstr)
							pick=0
							gonogo=False
							while pick<lung:
								thistranslEdit=self.superself.listemsgstr[pick].trnsl
								if thistranslEdit.tosave:
									gonogo=True
								pick+=1
						else:
							gonogo=self.tosave
						if gonogo:
							self.Save()
						kmesg.AddInt8('movekind',0)
						be_app.WindowAt(0).PostMessage(kmesg)
						return
					return BTextView.KeyDown(self,char,bytes)
				elif ochar == B_UP_ARROW:
					if value:
						# one element up
						if hasplural:
							lung=len(self.superself.listemsgstr)
							pick=0
							gonogo=False
							while pick<lung:
								thistranslEdit=self.superself.listemsgstr[pick].trnsl
								if thistranslEdit.tosave:
									gonogo=True
								pick+=1
						else:
							gonogo=self.tosave
						if gonogo:
							self.Save()
						kmesg.AddInt8('movekind',1)
						be_app.WindowAt(0).PostMessage(kmesg)
						return
					return BTextView.KeyDown(self,char,bytes)
				elif ochar == B_PAGE_UP:
					if value:
						# one page up
						if hasplural:
							lung=len(self.superself.listemsgstr)
							pick=0
							gonogo=False
							while pick<lung:
								thistranslEdit=self.superself.listemsgstr[pick].trnsl
								if thistranslEdit.tosave:
									gonogo=True
								pick+=1
						else:
							gonogo=self.tosave
						if gonogo:
							self.Save()						
						kmesg.AddInt8('movekind',2)
						be_app.WindowAt(0).PostMessage(kmesg)
						return
					return BTextView.KeyDown(self,char,bytes)
				elif ochar == B_PAGE_DOWN:
					if value:
						# one page down
						if hasplural:
							lung=len(self.superself.listemsgstr)
							pick=0
							gonogo=False
							while pick<lung:
								thistranslEdit=self.superself.listemsgstr[pick].trnsl
								if thistranslEdit.tosave:
									gonogo=True
								pick+=1
						else:
							gonogo=self.tosave
						if gonogo:
							self.Save()
						kmesg.AddInt8('movekind',3)
						be_app.WindowAt(0).PostMessage(kmesg)
						return
					return BTextView.KeyDown(self,char,bytes)
				elif ochar == 49:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",0)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 50:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",1)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 51:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",2)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 52:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",3)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 53:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",4)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 10: #ENTER
					#CTRL + enter
					if value:
						# next string needing work
						if hasplural:
							lung=len(self.superself.listemsgstr)
							pick=0
							gonogo=False
							while pick<lung:
								thistranslEdit=self.superself.listemsgstr[pick].trnsl
								if thistranslEdit.tosave:
									gonogo=True
								pick+=1
						else:
							gonogo=self.tosave
						if gonogo:
							self.Save()
						kmesg.AddInt8('movekind',4)
						be_app.WindowAt(0).PostMessage(kmesg)
						return
					else:
						if self.superself.sourcestrings.lv.CurrentSelection()>-1:
							self.tosave=True
							return BTextView.KeyDown(self,char,bytes)
							
# commented out because already included?
#				if ochar != B_ENTER: # needed to pass up/down keys to textview	
#					return BTextView.KeyDown(self,char,bytes)
					
			elif ochar == 2 or ochar == 98:				# ctrl+B or ctrl+b key to mark/umark as fuzzy
				self.superself.sem.acquire()
				value=self.superself.modifier #CTRL pressed
				self.superself.sem.release()
				if value:
					be_app.WindowAt(0).PostMessage(BMessage(71))
					return
				else:
					#insert b char
					if self.superself.sourcestrings.lv.CurrentSelection()>-1:
						self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				return
			elif ochar == B_ESCAPE: # Restore to the saved string
				self.SetText(self.oldtext,None)
				self.tosave=False
				thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
				thisBlistitem.tosave=False
				thisBlistitem.txttosave=""
				#print "Seleziono la fine?"
				fine=len(self.oldtext)
				self.Select(fine,fine)
				return
			else:
				if self.superself.sourcestrings.lv.CurrentSelection()>-1:
					if ochar == 115:					#CTRL+SHIF+S
						self.superself.sem.acquire()
						value=self.superself.shortcut #CTRL SHIFT pressed
						self.superself.sem.release()
						if value:
							be_app.WindowAt(0).PostMessage(33)
							return


					BTextView.KeyDown(self,char,bytes)
					if self.oldtext != self.Text():
						thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self	.superself.sourcestrings.lv.CurrentSelection())
						thisBlistitem.tosave=True
						tabs=len(self.superself.listemsgstr)-1
						if tabs == 0:
							thisBlistitem.txttosave=self.Text()
						#if tabs != 0: ######################################## <--- check why it was ==0 and not !=0
						else:
							thisBlistitem.txttosavepl=[]
							thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
							cox=1
							while cox < tabs+1:
								thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
								cox+=1
						self.tosave=True  # This says you should save the string before proceeding the same for blistitem.tosave doublecheck

						be_app.WindowAt(0).PostMessage(333111)
					return
		except:
			if self.superself.sourcestrings.lv.CurrentSelection()>-1:
				thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
				thisBlistitem.tosave=True
				thisBlistitem.txttosave=self.Text()
				self.tosave=True   # This says you should save the string before proceeding
				return BTextView.KeyDown(self,char,bytes)
		
	def SetPOReadText(self,text):
		self.oldtext=text
		self.oldtextloaded=True
		self.SetText(text,None)
		self.tosave=False
	
	def Analisi(self):
		return self.analisi
		
	def CheckSpell(self):
		speller = Popen( comm, stdout=PIPE, stdin=PIPE, stderr=PIPE)
		eltxt=self.Text()
		l=[chr for chr in eltxt]
		self.analisi=[]
		sd=0
		se=len(l)
		while sd<se:
			#self.analisi.append((unicodedata.category(unichr(ord(l[sd]))),l[sd]))  # char by char examination category print
			self.analisi.append((unicodedata.category(chr(ord(l[sd]))),l[sd]))  # char by char examination category print
			if sd==0:
				try:
					if l[sd]+l[sd+1] in inclusion:
						pass
					else:
						#if unicodedata.category(unichr(ord(l[sd]))) in esclusion:
						if unicodedata.category(chr(ord(l[sd]))) in esclusion:
							l[sd]=" "
				except:
					pass
			if sd==se-1:
				try:
					if l[sd-1]+l[sd] in inclusion:
						pass
					else:
						#if unicodedata.category(unichr(ord(l[sd]))) in esclusion:
						if unicodedata.category(chr(ord(l[sd]))) in esclusion:
							l[sd]=" "
				except:
					pass
			if sd>0 and sd<se-1:
				try:
					if l[sd]+l[sd+1] in inclusion:
						pass
					elif l[sd-1]+l[sd] in inclusion:
						pass
					else:
						#if unicodedata.category(unichr(ord(l[sd]))) in esclusion:
						if unicodedata.category(chr(ord(l[sd]))) in esclusion:
							l[sd]=" "
				except:
					pass
			sd+=1
		eltxt="".join(l)
		
		#diffeltxt=eltxt.decode(self.superself.encoding,errors='replace')
		diffeltxt=eltxt.decode(self.superself.encoding,errors='replace')
		stdout_data = speller.communicate(input=eltxt)[0]
		reallength=len(diffeltxt)
		areltxt=eltxt.split(" ")
		ardiffeltxt=diffeltxt.split(" ")
		whe=0
		whd=0
		cop=0
		newareltxt=[]
		while cop < len(areltxt):
			lparola = len(areltxt[cop])
			lparoladiff = len(ardiffeltxt[cop])
			val=(areltxt[cop],(whd,whd+len(ardiffeltxt[cop])),(whe,whe+len(areltxt[cop])))
			whe=whe+len(areltxt[cop])+1
			whd=whd+len(ardiffeltxt[cop])+1
			newareltxt.append(val)
			cop+=1
		errors = []
		self.analyzetxt = []
		stdout_data=stdout_data.split('\n')
		for s in stdout_data:
			if s != "":
				words=s.split()
				if s[0] == "&":
					# there are suggestions
					liw = s.find(words[3]) #string start-index that indicates the beginning of the number
					lun = len(words[3])-1  #string lenght except ":"
					iz = liw+len(words[3])+1 #string end of the number that indicates the beginning of solutions
					solutions = s[iz:]
					sugi = solutions.split(", ")
					outs = s[liw:liw+lun]   # <<<<------ number that hunspell indicates as where is the word to fix
					# here you check where is the correct byte for that hunspell-index
					for items in newareltxt:
						if items[1][0] == int(outs):
							realouts=items[2][0]
					t=word2fix(words[1],int(outs),realouts)
					x=0
					while x < int(words[2]):
						t.add(sugi[x])
						x+=1
					errors.append(t)
					self.analyzetxt.append(t)
				elif s[0] == "#":
					# no suggestions
					liw=s.find(words[2])
					lun=len(words[2])
					outs=s[liw:liw+lun]
					for items in newareltxt:
						if items[1][0] == int(outs):
							realouts=items[2][0]
							
					t=word2fix(words[1],int(outs),realouts)
					errors.append(t)
		#### Ricreo stringa colorata ####
		stile=[(0, be_plain_font, (0, 0, 0, 0))]
		if len(errors)>0:
			be_app.WindowAt(0).PostMessage(982757)
			#self.superself.checkres.SetText("☒")
			if errors[0].pos>0 or errors == []:
				stile.append((0, be_plain_font, (0, 0, 0, 0)))
				stile=startinserting(stile,errors)
			else:
				stile = startinserting(stile,errors)
		else:
			be_app.WindowAt(0).PostMessage(735157)
			#self.superself.checkres.SetText("☑")
		
		evstyle.acquire()
		self.evstile=stile
		evstyle.release()
		posizion=self.GetSelection()
		mj=BMessage(222888)
		mj.AddInt32("start",posizion[0])
		mj.AddInt32("end",posizion[1])
		be_app.WindowAt(0).PostMessage(mj)

class srcTextView(BTextView):
	def __init__(self,frame,name,textRect,resizingMode,flags):
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)
		self.SetStylable(1)
		self.spaces=["\\x20","\\xc2\\xa0","\\xe1\x9a\\x80","\\xe2\\x80\\x80","\\xe2\\x80\\x81","\\xe2\\x80\\x82","\\xe2\\x80\\x83","\\xe2\\x80\\x84","\\xe2\\x80\\x85","\\xe2\\x80\\x86","\\xe2\\x80\\x87","\\xe2\\x80\\x88","\\xe2\\x80\\x89","\\xe2\\x80\\x8a","\\xe2\\x80\\x8b","\\xe2\\x80\\xaf","\\xe2\\x81\\x9f","\\xe3\\x80\\x80"]
	def Draw(self,suaze):
		BTextView.Draw(self,suaze)
		self.font = be_plain_font
		hrdwrk= self.Text()
		#multibyte spaces analisis
		#text analisys for multiple whitespaces, tabulations, carriage returns...
		#tst=hrdwrk.encode('utf-8')
		#tst=unicode(hrdwrk,'utf-8')
		tst=hrdwrk
		lis = list(tst)
		foundo = 0
		for index,ci in enumerate(lis):
			a=bytearray(ci.encode('utf-8'))
			bob=self.PointAt(index)
			a_hex=[hex(x) for x in a]
			if len(a_hex)>1:
				i=0
				stmp=""
				while i<len(a_hex):
					stmp+="\\"+a_hex[i][1:]
					i+=1
				if stmp in self.spaces:
					foundo=self.Text().find(ci,foundo)
					asd=self.PointAt(foundo)
					foundo+=1
					self.SetHighColor(0,0,200,0)
					self.MovePenTo(BPoinu(asd[0].x+(self.font.StringWidth(ci)/2),asd[0].y+asd[1]-3))
					self.DrawString('͜',None)#'̳')#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
					self.SetHighColor(0,0,0,0)
			else:
				mum="\\"+a_hex[0][1:]
				if mum in self.spaces:
					#foundo=self.Text().find(ci.encode('utf-8'),foundo)
					foundo=self.Text().find(ci,foundo)
					asd=self.PointAt(foundo)
					foundo+=1
					if index+1<len(lis):
						a=bytearray(lis[index+1].encode('utf-8'))
						a_hex=[hex(x) for x in a]
						if len(a_hex)==1:
							stmp="\\"+a_hex[0][1:]
							if stmp in self.spaces:
								self.SetHighColor(200,0,0,0)
								self.MovePenTo(BPoint(asd[0].x+(self.font.StringWidth(ci)/2),asd[0].y+asd[1]-3))
								self.DrawString('̳·̳',None)#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
								self.SetHighColor(0,0,0,0)
							elif stmp == "\\xa":
								self.SetHighColor(200,0,0,0)
								self.MovePenTo(BPoint(asd[0].x,asd[0].y+asd[1]-5))
								self.DrawString('̳',None)
								self.SetHighColor(0,0,0,0)
							elif stmp == "\\x9":
								self.SetHighColor(200,0,0,0)
								self.MovePenTo(BPoint(asd[0].x,asd[0].y+asd[1]-3))
								self.DrawString('̳',None)
								self.SetHighColor(0,0,0,0)
						else:
							i=0
							stmp=""
							while i<len(a_hex):
								stmp+="\\"+a_hex[i][1:]
								i+=1
							if stmp in self.spaces:
								self.SetHighColor(200,0,0,0)
								self.MovePenTo(BPoint(asd[0].x+(self.font.StringWidth(ci)/2),asd[0].y+asd[1]-3))
								self.DrawString('̳·̳',None)#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
								self.SetHighColor(0,0,0,0)
					else:
						self.SetHighColor(200,0,0,0)
						self.MovePenTo(BPoint(asd[0].x+self.font.StringWidth(ci)/2,asd[0].y+asd[1]-3))
						self.DrawString('̳')#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
						self.SetHighColor(0,0,0,0)
				elif mum=="\\xa":
					foundo=self.Text().find(ci,foundo)
					asd=self.PointAt(foundo)
					foundo+=1
					self.SetHighColor(200,0,0,0)
					fon=BFont()
					self.GetFont(fon)
					self.MovePenTo(BPoint(asd[0].x,asd[0].y+asd[1]-3))#(asd[0][0],asd[0][1]+asd[1]-3))
					self.DrawString('⏎',None)
					self.SetHighColor(0,0,0,0)
				elif mum=="\\x9":
					self.SetHighColor(200,0,0,0)
					foundo=self.Text().find(ci,foundo)
					asd=self.PointAt(foundo)
					foundo+=1
					self.MovePenTo(BPoint(asd[0].x,asd[0].y+asd[1]-3))
					wst='↹'
					if index+1<len(lis):
						a=bytearray(lis[index+1].encode('utf-8'))
						a_hex=[hex(x) for x in a]
						if len(a_hex)==1:
							stmp="\\"+a_hex[0][1:]
							if stmp in self.spaces:
								wst='↹·'
						else:
							i=0
							stmp=""
							while i<len(a_hex):
								stmp+="\\"+a_hex[i][1:]
								i+=1
							if stmp in self.spaces:
								wst='↹·'
					self.DrawString(wst,None)
					self.SetHighColor(0,0,0,0)

#		ii=0
#		decor=[]
#		while ii<len(hrdwrk):
#	 		#if hrdwrk[ii] == ' ':
#	 		zit = ii
#	 		zed = ii+1
#	 		if unicodedata.category(unichr(ord(hrdwrk[zit])))=='Zs': #spaces
#	 			if zed==len(hrdwrk):
#	 				asd=self.PointAt(zit)
#	 				color = (200,0,0,0)
#	 				self.SetHighColor(color)
#	 				self.MovePenTo((asd[0][0]+(self.font.StringWidth(hrdwrk[zit])/2),asd[0][1]+asd[1]-3))
#	 				self.DrawString(' ̳')#' ᪶ ')#'˽'
#	 				color = (0,0,0,0)
#	 				self.SetHighColor(color)
#	 			elif unicodedata.category(unichr(ord(hrdwrk[zed])))=='Zs':
#	 				asd=self.PointAt(zit)
#	 				color = (200,0,0,0)
#	 				self.SetHighColor(color)
#	 				self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
#	 				self.DrawString(' ̳')
#	 				self.MovePenTo((asd[0][0]+(self.font.StringWidth(hrdwrk[zit])/2),asd[0][1]+self.font.GetHeight()[0]))
#	 				self.DrawString('·')
#	 				color = (0,0,0,0)
#	 				self.SetHighColor(color)
#	 			elif unicodedata.category(unichr(ord(hrdwrk[zed]))) in ['Cc','Zl','Zp']:#=='Cc':
#	 				#zed=ii+1
#	 				if hrdwrk[zed]=='\n':
#	 					asd=self.PointAt(zit)
#	 					color = (200,0,0,0)
#	 					self.SetHighColor(color)
#	 					self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
#	 					self.DrawString(' ̳')
#	 					color = (255,0,0,0)
#						self.SetHighColor(color)
#						self.MovePenTo((asd[0][0]+(self.font.StringWidth(hrdwrk[zit])),asd[0][1]+asd[1]))#+8 replaced with +(self.font.StringWidth(hrdwrk[zit])/2)
#						self.DrawString('⏎')
#	 					color = (0,0,0,0)
#	 					self.SetHighColor(color)
#	 					ii+=1
#	 				elif hrdwrk[zed]=='\t':
#	 					asd=self.PointAt(zit)
#	 					color = (200,0,0,0)
#	 					self.SetHighColor(color)
#	 					self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
#	 					self.DrawString(' ̳')
#	 					color = (255,0,0,0)
#						self.SetHighColor(color)
#						self.MovePenTo((asd[0][0]+(self.font.StringWidth(hrdwrk[zit])/2),asd[0][1]+self.font.GetHeight()[0]))
#						self.DrawString('↹')
#	 					color = (0,0,0,0)
#	 					self.SetHighColor(color)
#	 					ii+=1
	 			#elif hrdwrk[ii+1]=='\n':
	 			#	asd=self.PointAt(ii)
	 			#	color = (200,0,0,0)
	 			#	self.SetHighColor(color)
	 			#	self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
	 			#	self.DrawString(' ̳')
	 			#	color = (255,0,0,0)
				#	self.SetHighColor(color)
				#	self.MovePenTo((asd[0][0]+8,asd[0][1]+asd[1]))
				#	self.DrawString('⏎')
	 			#	color = (0,0,0,0)
	 			#	self.SetHighColor(color)
	 			#	ii+=1
	 			#elif hrdwrk[ii+1]==' ':
	 			#	asd=self.PointAt(ii)
	 			#	color = (200,0,0,0)
	 			#	self.SetHighColor(color)
	 			#	self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
	 			#	self.DrawString(' ̳')
	 			#	self.MovePenTo((asd[0][0]+(self.font.StringWidth(hrdwrk[ii])/2),asd[0][1]+self.font.GetHeight()[0]))
	 			#	self.DrawString('·')
	 			#	color = (0,0,0,0)
	 			#	self.SetHighColor(color)
#	 		if unicodedata.category(unichr(ord(hrdwrk[zit])))=='Cc':
#	 			if hrdwrk[zit] == '\n':
#	 				asd=self.PointAt(zit)
#		 			color = (255,0,0,0)
#					self.SetHighColor(color)
#	 				self.MovePenTo((asd[0][0],asd[0][1]+asd[1]))
#	 				self.DrawString('⏎')
#		 			color = (0,0,0,0)
#		 			self.SetHighColor(color)
#	 			elif hrdwrk[zit] == '\t':
#	 				if zed==len(hrdwrk):
#	 					asd=self.PointAt(zit)
#		 				color = (255,0,0,0)
#						self.SetHighColor(color)
#	 					self.MovePenTo((asd[0][0],asd[0][1]+self.font.GetHeight()[0]))
#	 					self.DrawString('↹')
#		 				color = (0,0,0,0)
#		 				self.SetHighColor(color)
#	 				elif hrdwrk[zed] == '\n':
#	 					asd=self.PointAt(zit)
#	 					print "tab asd",asd,zit
#		 				color = (255,0,0,0)
#						self.SetHighColor(color)
#	 					self.MovePenTo((asd[0][0],asd[0][1]+self.font.GetHeight()[0]))
#	 					self.DrawString('↹')
#		 				color = (0,0,0,0)
#		 				self.SetHighColor(color)
#		 				color = (255,0,0,0)
#						self.SetHighColor(color)
#						self.MovePenTo((asd[0][0]+self.font.StringWidth('w '),asd[0][1]+asd[1]))
#						self.DrawString('⏎')
#	 					color = (0,0,0,0)
#	 					self.SetHighColor(color)
#	 					ii+=1
#		 			else:
#		 				asd=self.PointAt(zit)
#		 				color = (255,0,0,0)
#						self.SetHighColor(color)
#	 					self.MovePenTo((asd[0][0],asd[0][1]+self.font.GetHeight()[0]))
#	 					self.DrawString('↹')
#		 				color = (0,0,0,0)
#		 				self.SetHighColor(color)
#		 			
#			ii+=1
		return
		
def checklang(orderedata):
	ent,confile=Ent_config()
	Config.read(confile)
	confexists=False #esiste sezione utente
	samelang=-1 #1=non è la stessa lingua; -1=non è stata rilevata il metadata Language(B_ERROR); 0=Stessa lingua(B_OK)
	try:
		#controlla lingua in config
		llangs=ConfigSectionMap("Translator")['langs'].split(",")
		confexists=True
		# controllo per esistenza metadata Language
		for i in orderedata:
			if i[0]=="Language":
				if i[1] in llangs:
					samelang=0
					break
				else:
					samelang=1
	except:
		confexists=False

	return (confexists,samelang)
		#ottinei language da ordered meta data

class CreateUserBox(BBox):
	lli=[]
	ali=[]
	email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
	def __init__(self,frame):#,metadata):
		BBox.__init__(self,frame,"UserBox",0x0202|0x0404,InterfaceDefs.border_style.B_NO_BORDER)
		self.frame = frame
		box=[10,10,frame.right-10,frame.bottom-10]
		step = 34
		fon=BFont()
		self.name=BTextControl(BRect(box[0],box[1],box[2],box[1]+fon.Size()),"fullname","Full Name",None,BMessage(152))
		self.mail=BTextControl(BRect(box[0],box[1]+fon.Size()+step,box[2],box[1]+fon.Size()*2+step),"mail","E-mail",None,BMessage(153))
		self.lt=BTextControl(BRect(box[0],box[1]+fon.Size()*2+step*2,box[2],box[1]+fon.Size()*3+step*2),"lang_team","Language team",None,BMessage(154))
		self.ltmail=BTextControl(BRect(box[0],box[1]+fon.Size()*3+step*3,box[2],box[1]+fon.Size()*4+step*3),"team_mail","Language-team e-mail",None,BMessage(155))
		#lista di lingue
		self.lang=BStringView(BRect(box[0],box[1]+fon.Size()*5+step*4,box[2],box[1]+fon.Size()*6+step*4),"lang_string","Accepted languages:")
		self.langlist=ScrollView(BRect(box[0],box[1]+fon.Size()*5+step*5,box[2]/2-20,box[3]-80), 'LanguageList')
		selmsg=BMessage(333)
		self.langlist.lv.SetSelectionMessage(selmsg)
		self.acceptedlang=ScrollView(BRect(box[2]/2+20,box[1]+fon.Size()*5+step*5,box[2]-20,box[3]-80), 'LanguageList')
		self.acceptedlang.lv.SetSelectionMessage(selmsg)
		msg = BMessage(412)
		self.acceptedlang.lv.SetInvocationMessage(msg)
		msg = BMessage(312)
		self.langlist.lv.SetInvocationMessage(msg)
		self.AddChild(self.name,None)
		self.AddChild(self.mail,None)
		self.AddChild(self.lt,None)
		self.AddChild(self.lang,None)
		self.AddChild(self.ltmail,None)
		
		self.AddChild(self.langlist.sv,None)
		self.AddChild(self.acceptedlang.sv,None)
		#territori=[]
		languages=[]
		#locale=Locale('fur','IT')
		locale=Locale.default()
		#for i in locale.territories:
		#	territori.append(locale.territories[i])
		for i in locale.languages:
			suggested=False
			try:
				l=Locale.parse(i)
				dn=l.get_display_name()
			except:
				dn=locale.languages[i]
			if str(Locale.default()) in i:
				suggested=True
			self.lli.append(LangListItem(dn,i,suggested))
			self.langlist.lv.AddItem(self.lli[-1])#locale.languages[i]
		self.lli.append(LangListItem("Add custom iso code",None,False))
		self.langlist.lv.AddItem(self.lli[-1])
		self.BtnSave=BButton(BRect(box[2]/2+100,box[3]-50,box[2]-5,box[3]-5),'SaveUserSettingsBtn','Save',BMessage(612))
		self.BtnCancel=BButton(BRect(box[0]+5,box[3]-50,box[2]/2-100,box[3]-5), 'CancelUserSettingsBtn','Cancel',BMessage(B_QUIT_REQUESTED))
		self.AddChild(self.BtnSave,None)
		self.AddChild(self.BtnCancel,None)
		# import data from config.ini
		ent,confile=Ent_config()
		Config.read(confile)
		try:
			#controlla lingua in config
			llangs=ConfigSectionMap("Translator")['langs'].split(",")
			for l in llangs:
				locale=Locale(l)
				dn=locale.get_display_name()
				suggested=False
				if str(Locale.default()) in l:
					suggested=True
				self.ali.append(LangListItem(dn,l,suggested))
				self.acceptedlang.lv.AddItem(self.ali[-1])
		except Exception as e:
			print(e)#missing accepted languages
		try:
			self.name.SetText(ConfigSectionMap("Translator")['name'])
		except:
			pass#missing translator name
		try:
			self.mail.SetText(ConfigSectionMap("Translator")['mail'])
		except:
			pass#missing translator e-mail
		try:
			self.lt.SetText(ConfigSectionMap("Translator")['team'])
		except:
			pass#missing language team name
		try:
			self.ltmail.SetText(ConfigSectionMap("Translator")['ltmail'])
		except:
			pass#missing language team e-mail
		#pometadata
		#self.listBTextControl=[]
		#rect = [10,10,425,30]
		#step = 34
		#indexstring=0
		#for item in self.metadata:
		#	self.listBTextControl.append(BTextControl((rect[0],rect[1]+step*indexstring,rect[2],rect[3]+step*indexstring),'txtctrl'+str(indexstring),item[0],item[1],modmsg))
		#	indexstring+=1
class LangListItem(BListItem):
	def __init__(self, dn, iso, s):
		self.dn=dn
		self.s = s
		if iso!=None:
			self.iso=iso
			self.txt=self.dn+" ("+self.iso+")"
		else:
			self.iso=None
			self.txt=self.dn
		#fon=BFont()
		#self.font_height_value=font_height()
		#fon.GetHeight(self.font_height_value)
		BListItem.__init__(self)
		
	def DrawItem(self, owner, frame, complete):
		if self.IsSelected() or complete:
			owner.SetHighColor(200,200,200,255)
			owner.SetLowColor(200,200,200,255)
			owner.FillRect(frame)
		if self.s:
			owner.SetHighColor(0,200,0,0)
		else:
			owner.SetHighColor(0,0,0,0)
		owner.MovePenTo(5,frame.bottom-5)
		if self.iso==None:
			owner.SetFont(be_bold_font)
		else:
			owner.SetFont(be_plain_font)
		#if self.unread:
		#	owner.SetFont(be_bold_font)
		#else:
		#	owner.SetFont(be_plain_font)
		owner.DrawString(self.txt,None)
		owner.SetLowColor(255,255,255,255)

class infoTab(BTab):
	def __init__(self,contentsView):
		self.notify=False
		BTab.__init__(self,contentsView)
	def DrawLabel(self, owner, frame):
		if self.notify:
			fon = be_bold_font
		else:
			fon = be_plain_font
		#owner.GetFont(fon)
		fon.SetSize(10)
		owner.SetFont(fon)
		#owner.SetHighColor(200,200,0,0)
		#owner.SetLowColor(255,255,255,255)
		BTab.DrawLabel(self,owner,frame)

class FindRepTrans(BWindow):
	kWindowFrame = (250, 150, 755, 297)
	kWindowName = "Find/Replace translation"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		h=round(self.underframe.GetFontHeight()[0])
		kButtonFrame1 = (r*2/3+5,69,r-5,104)
		kButtonName1 = "Search"
		self.SearchButton = BButton(kButtonFrame1, kButtonName1, kButtonName1, BMessage(5348))
		self.underframe.AddChild(self.SearchButton)
		kButtonFrame2 = (r/3+5,69,r*2/3-5,104)
		kButtonName2 = "Replace"
		self.ReplaceButton = BButton(kButtonFrame2, kButtonName2, kButtonName2, BMessage(10240))#7047))
		self.underframe.AddChild(self.ReplaceButton)
		self.casesens = BCheckBox((5,79,r/2-15,104),'casesens', 'Case sensistive', BMessage(222))
		self.casesens.SetValue(1)
		self.underframe.AddChild(self.casesens)
		self.looktv=BTextControl((5,5,r-5,32),'txttosearch','Search:','',BMessage(8046))
		self.looktv.SetDivider(60.0)
		self.underframe.AddChild(self.looktv)
		self.looktv.MakeFocus()
		self.reptv=BTextControl((5,37,r-5,64),'replacetxt','Replace:','',BMessage(8046))
		self.reptv.SetDivider(60.0)
		self.underframe.AddChild(self.reptv)
		self.pb=BStatusBar((5,b-42,r-5,b+5),"searchpb",None,None)
		self.pb.SetBarHeight(float(14))
		self.underframe.AddChild(self.pb)
		lista=be_app.WindowAt(0).sourcestrings.lv
		total=lista.CountItems()
		self.pb.SetMaxValue(float(total))
		indaco=lista.CurrentSelection()
		self.pb.Update(float(indaco))
		self.ei=0
		self.ef=0
		#self.encoding=BApplication.be_app.WindowAt(0).encoding
		self.encoding = be_app.WindowAt(0).encoding
		i = 1
		w = be_app.CountWindows()
		while w > i:
			if be_app.WindowAt(i).Title()==self.kWindowName:
				self.thiswindow=i
			i=i+1

	def MessageReceived(self, msg):
		if msg.what == 5348:
			if self.looktv.Text() != "":
				self.pof=be_app.WindowAt(0).pofile
				lista=be_app.WindowAt(0).sourcestrings.lv
				indaco=lista.CurrentSelection()
				if indaco>-1:
						savin=False
						object=lista.ItemAt(indaco)
						if object.hasplural:
							if object.tosave:
								savin = True
							if not savin:
								listar=be_app.WindowAt(0).listemsgstr
								t=len(listar)
								x=0
								while x<t:
									if listar[x].trnsl.tosave:
										savin = True
										break
									x+=1
						else:
							if object.tosave:
								savin = True
							if be_app.WindowAt(0).listemsgstr[0].trnsl.tosave:
								savin = True
						if savin:
							be_app.WindowAt(0).listemsgstr[0].trnsl.Save()
				self.arrayview=be_app.WindowAt(0).poview
				total=lista.CountItems()
				applydelta=float(indaco-self.pb.CurrentValue())
				deltamsg=BMessage(7047)
				deltamsg.AddFloat('delta',applydelta)
				be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
				tl = len(self.looktv.Text())
				max = total
				now = indaco
				lastvalue=now
				partial = False
				partiali = False
				loopa =True
				epistola = BMessage(963741)
				while loopa:
					now+=1
					if now < total:
							delta=float(now-lastvalue)
							deltamsg=BMessage(7047)
							deltamsg.AddFloat('delta',delta)
							be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
							lastvalue=now
							blister=lista.ItemAt(now)
							if self.casesens.Value():
								if blister.hasplural:
									for ident,items in enumerate(blister.msgstrs):#enumerate(values):
										ret = items.encode(self.encoding).find(self.looktv.Text())
										if ret >-1:
											lista.Select(now)
											epistola.AddInt8('plural',ident)
											epistola.AddInt32('inizi',ret)
											epistola.AddInt32('fin',ret+tl)
											epistola.AddInt8('srctrnsl',1)
											be_app.WindowAt(0).PostMessage(epistola)
											loopa = False
											self.ei=ret
											self.ef=ret+tl
											break
								else:
									ret = blister.msgstrs.encode(self.encoding).find(self.looktv.Text())
									if ret >-1:
										lista.Select(now)
										epistola.AddInt8('plural',0)
										epistola.AddInt32('inizi',ret)
										epistola.AddInt32('fin',ret+tl)
										epistola.AddInt8('srctrnsl',1)
										be_app.WindowAt(0).PostMessage(epistola)
										loopa = False
										self.ei=ret
										self.ef=ret+tl
										break
							else:
								if blister.hasplural:
									for ident,items in enumerate(blister.msgstrs):
										ret = items.encode(self.encoding).lower().find(self.looktv.Text().lower())
										if ret >-1:
											lista.Select(now)
											epistola.AddInt8('plural',ident)
											epistola.AddInt32('inizi',ret)
											epistola.AddInt32('fin',ret+tl)
											epistola.AddInt8('srctrnsl',1)
											be_app.WindowAt(0).PostMessage(epistola)
											loopa = False
											self.ei=ret
											self.ef=ret+tl
											break
								else:
									ret = blister.msgstrs.encode(self.encoding).lower().find(self.looktv.Text().lower())
									if ret >-1:
										lista.Select(now)
										epistola.AddInt8('plural',0)
										epistola.AddInt32('inizi',ret)
										epistola.AddInt32('fin',ret+tl)
										epistola.AddInt8('srctrnsl',1)
										be_app.WindowAt(0).PostMessage(epistola)
										loopa = False
										self.ei=ret
										self.ef=ret+tl
										break
					if now == total:
							now = -1
							total = indaco+1
							partial = True
					if now == indaco:
							partiali = True
					if partial and partiali:
							loopa=False
							say = BAlert('not_found', 'No matches found on listed entries', 'Ok',None, None, None, 3)
							say.Go()
			return

		elif msg.what == 7047:
			addfloat=msg.FindFloat('delta')
			self.pb.Update(addfloat)
			return
		elif msg.what == 10240:
			if self.ef>self.ei:
				listar=be_app.WindowAt(0).listemsgstr
				repmsg=BMessage(10241)
				repmsg.AddInt16("ei",self.ei)
				repmsg.AddInt16("ef",self.ef)
				repmsg.AddString("subs",self.reptv.Text())#.encode('utf-8'))
				be_app.WindowAt(0).PostMessage(repmsg)
				#wt=listar[BApplication.be_app.WindowAt(0).transtabview.Selection()].trnsl#.Text()
				#wt.Delete(self.ei,self.ef)
		elif msg.what == 1010:
#			lftxt=
			self.looktv.SetText(msg.FindString('txt'))
			return
		return

class MainWindow(BWindow):
	iwheel=0
	alerts=[]
	Menus = (
		('File', ((295485, 'Open'), (2, 'Save'), (1, 'Close'), (5, 'Save as...'),(None, None),(B_QUIT_REQUESTED, 'Quit'))),
		('Translation', ((3, 'Copy from source (ctrl+shift+s)'), (32,'Edit comment'), (70,'Done and next'), (71,'Mark/Unmark fuzzy (ctrl+b)'), (72, 'Previous w/o saving'),(73,'Next w/o saving'),(None, None), (6, 'Find source'), (7, 'Find/Replace translation'))),
		('View', ((74,'Fuzzy'), (75, 'Untranslated'),(76,'Translated'),(77, 'Obsolete'))),
		('Settings', ((40, 'General'),(41, 'User settings'), (42, 'Po properties'), (43, 'Po header'), (44, 'Spellcheck'), (45,'Translation Memory'))),
		('About', ((8, 'Help'),(None, None),(9, 'About')))
		)
		
	def __init__(self,arg):
		#global confile
		BWindow.__init__(self, BRect(6,64,1024,768), "HaiPO 2.0", window_type.B_TITLED_WINDOW, B_QUIT_ON_WINDOW_CLOSE)#B_NOT_RESIZABLE |
		self.speloc = threading.Semaphore()
		self.intime=time.time()
		self.bckgnd = BView(self.Bounds(), "bckgnd_View", 8, 20000000)
		rect=self.bckgnd.Bounds()
		self.AddChild(self.bckgnd,None)
		self.bckgnd.SetResizingMode(B_FOLLOW_ALL_SIDES)
		bckgnd_bounds=self.bckgnd.Bounds()
		self.drop = threading.Semaphore()
		self.sem = threading.Semaphore()
		self.poview=[True,True,True,False]
		fon=BFont()
		self.oldsize=fon.Size()
		#perc=BPath()
		#find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
		#datapath=BDirectory(perc.Path()+"/HaiPO2")
		#ent=BEntry(datapath,perc.Path()+"/HaiPO2")
		#if not ent.Exists():
		#	datapath.CreateDirectory(perc.Path()+"/HaiPO2", datapath)
		#ent.GetPath(perc)
		#confile=BPath(perc.Path()+'/config.ini',None,False)
		#ent=BEntry(confile.Path())
		ent,confile=Ent_config()
		global tm,tmxsrv,tmxprt,tmsocket,showspell,comm
		showspell = False
		if ent.Exists():
			Config.read(confile)
			try:
				self.sort=int(ConfigSectionMap("General")['sort'])
			except:
				#no section
				cfgfile = open(confile,'w')
				Config.add_section('General')
				Config.set('General','sort', "0")
				self.sort=0
				Config.write(cfgfile)
				cfgfile.close()
				Config.read(confile)
			try:
				self.poview[0]=Config.getboolean('Listing', 'Fuzzy')
				self.poview[1]=Config.getboolean('Listing', 'Untranslated')
				self.poview[2]=Config.getboolean('Listing', 'Translated')
				self.poview[3]=Config.getboolean('Listing', 'Obsolete')
			except (configparser.NoSectionError):
				cfgfile = open(confile,'w')
				Config.add_section('Listing')
				Config.set('Listing','Fuzzy',"True")
				Config.set('Listing','Untranslated',"True")
				Config.set('Listing','Translated',"True")
				Config.set('Listing','Obsolete',"False")
				Config.write(cfgfile)
				cfgfile.close()
			except (configparser.NoOptionError):
				cfgfile = open(confile,'w')
				Config.set('Listing','Fuzzy',"True")
				Config.set('Listing','Untranslated',"True")
				Config.set('Listing','Translated',"True")
				Config.set('Listing','Obsolete',"False")
				Config.write(cfgfile)
				cfgfile.close()
			try:
				if ConfigSectionMap("General")['tm'] == "True":
					tm = True
				else:
					tm = False
				if tm:
					#tmsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					try:
						tmxsrv=ConfigSectionMap("TMSettings")['tmxsrv']
						tmxprt=int(ConfigSectionMap("TMSettings")['tmxprt'])
					except:
						cfgfile = open(confile,'w')
						try:
							Config.add_section("TMSettings")
						except:
							pass
						Config.set("TMSettings",'tmxsrv', '127.0.0.1')
						Config.set("TMSettings",'tmxprt', "2022")
						tmxsrv = '127.0.0.1'
						tmxprt = 2022
						Config.write(cfgfile)
						cfgfile.close()
			except:
				cfgfile = open(confile,'w')
				Config.set('General','tm', 'False')
				Config.write(cfgfile)
				cfgfile.close()
				tm=False
				tmxsrv = '127.0.0.1'
				tmxprt = 2022
			try:
				Config.read(confile)
				self.modifiervalue=int(Config.get('General','modifierkey'))
			except:
				cfgfile = open(confile,'w')
				Config.set('General','modifierkey',"4100")
				Config.write(cfgfile)
				cfgfile.close()
				self.modifiervalue=4100 #1058 ALT;4100 CTRL
			try:
				if ConfigSectionMap("General")['spellchecking'] == "True":
					setspellcheck=True
				else:
					setspellcheck=False
			except:
				cfgfile = open(confile,'w')
				Config.set('General','spellchecking', 'False')
				Config.write(cfgfile)
				cfgfile.close()
				setspellcheck=False
			# try:
				# resu=ConfigSectionMap("Timer")['enabled']
				# if resu == "True":
					# self.enabletimer= True
				# else:
					# self.enabletimer=False
			# except:
				# cfgfile = open(confile,'w')
				# Config.add_section('Timer')
				# Config.set('Timer','enabled', "False")
				# Config.set('Timer','timer', "300000000")
				# self.timer=300000000
				# self.enabletimer=False
				# Config.write(cfgfile)
				# cfgfile.close()
				# Config.read(confile)
			# if self.enabletimer:
				# try:
					# self.timer=int(ConfigSectionMap("Timer")['timer'])
				# except:
					# cfgfile = open(confile,'w')
					# Config.set('Timer','timer', "300000000")
					# self.timer=300000000
					# Config.write(cfgfile)
					# cfgfile.close()
					# Config.read(confile)
				# be_app.SetPulseRate(self.timer)
		else:
			#no file
			cfgfile = open(confile,'w')
			Config.add_section('General')
			Config.set('General','sort', "0")
			#Config.add_section('Timer')
			#Config.set('Timer','enabled', "False")
			#Config.set('Timer','timer', "300000000")
			self.sort=0
			#self.startmin=False
			#self.enabletimer=False
			#self.timer=300000000
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
		
		if setspellcheck:
			showspell=True
			try:
				global inclusion,esclusion
				#usero=ConfigSectionMap("Translator")['default']
				try:
					inctxt=ConfigSectionMap("Translator")['spell_inclusion']
					inclusion = inctxt.split(",")
				except:
					cfgfile = open(confile,'w')
					Config.set("Translator",'spell_inclusion', '')
					Config.write(cfgfile)
					cfgfile.close()
					inclusion = []
				try:
					esctxt=ConfigSectionMap("Translator")['spell_esclusion']
					esclusion=esctxt.split(",")
				except:
					cfgfile = open(confile,'w')
					Config.set("Translator",'spell_esclusion', 'Pc,Pd,Pe,Pi,Po,Ps,Cc,Pf')
					Config.write(cfgfile)
					cfgfile.close()
					esclusion = ["Pc","Pd","Pe","Pi","Po","Ps","Cc","Pf"]
				try:
					spelldict=ConfigSectionMap("Translator")['spell_dictionary']
				except:
					cfgfile = open(confile,'w')
					Config.set("Translator",'spell_dictionary', '/system/data/hunspell/en_US')
					Config.write(cfgfile)
					cfgfile.close()
					spelldict="/system/data/hunspell/en_US"
			except:
				spelldict="/system/data/hunspell/en_US"
				inclusion = []
				esclusion = ["Pc","Pd","Pe","Pi","Po","Ps","Cc","Pf"]
			try:
				exe=ConfigSectionMap("General")['spell_path']
			except:
				#TODO in base ad architettura scegliere l'eseguibile
				exe = "hunspell"#"hunspell-x86"
				cfgfile = open(confile,'w')
				Config.set("General",'spell_path', find_executable("hunspell"))
				Config.write(cfgfile)
				cfgfile.close()
			#if setencoding:
			#	comm = [exe,'-i',encoding,'-d',spelldict]
			#else:
			#	comm = [exe,'-d',spelldict]
			comm = [exe,'-d',spelldict]
		else:
			showspell=False
			
		self.steps=['˹','   ˺','   ˼','˻']
		self.ofp=BFilePanel(B_OPEN_PANEL,None,None,node_flavor.B_ANY_NODE,True, None, None, True, True)
		osdir="/boot/home"
		self.ofp.SetPanelDirectory(osdir)
		self.bar = BMenuBar(bckgnd_bounds, 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		self.viewarr = []
		for menu, items in self.Menus:
			menu = BMenu(menu)
			for k, name in items:
				if k is None:
						menu.AddItem(BSeparatorItem())
				else:
						mitm=BMenuItem(name, BMessage(k), name[1],0)
						if name == "Fuzzy":
							if self.sort == 0:
								mitm.SetMarked(True)
							self.viewarr.append(mitm)
						elif name == "Untranslated":
							if self.sort == 1:
								mitm.SetMarked(True)
							self.viewarr.append(mitm)
						elif name == "Translated":
							if self.sort == 2:
								mitm.SetMarked(True)
							self.viewarr.append(mitm)
						elif name == "Obsolete":
							if self.sort == 3:
								mitm.SetMarked(True)
							self.viewarr.append(mitm)
						menu.AddItem(mitm)
						
			self.bar.AddItem(menu)
		self.upperbox = BBox(BRect(0,barheight+2,bckgnd_bounds.Width(),bckgnd_bounds.Height()/2-1),"Under_upperbox",B_FOLLOW_TOP,border_style.B_FANCY_BORDER)#0x0202|0x0404
		self.lowerbox = BBox(BRect(0,bckgnd_bounds.Height()/2+1,bckgnd_bounds.Width()*2/3,bckgnd_bounds.Height()),"Under_lowerbox",B_FOLLOW_BOTTOM,border_style.B_FANCY_BORDER)#0x0202|0x0404
		self.spaceright=bckgnd_bounds.Width()/3
		self.bckgnd.AddChild(self.upperbox,None)
		self.bckgnd.AddChild(self.lowerbox,None)
		self.bckgnd.AddChild(self.bar,None)
		
		self.transtabview = translationtabview(BRect(2.0, self.lowerbox.Bounds().bottom/+2.0, self.lowerbox.Bounds().right-2, self.lowerbox.Bounds().bottom-2.0), 'transtabview',self)
		self.transtablabels=[]
		self.listemsgstr=[]
		self.srctabview = sourcetabview(BRect(2.0, 2.0, self.lowerbox.Bounds().right-2.0, self.lowerbox.Bounds().bottom/2-2.0), 'sourcetabview',self)
		self.srctablabels=[]
		self.listemsgid=[]
		altece = self.srctabview.TabHeight()
		altece2 = self.transtabview.TabHeight()
		tabrc = (3.0, 3.0, self.srctabview.Bounds().Width() - 3, self.srctabview.Bounds().Height()-altece)
		tabrc2 = (3.0, 3.0, self.transtabview.Bounds().Width() - 3, self.transtabview.Bounds().Height()-altece2)
		self.sourcebox=srctabbox(tabrc,'msgid',altece)
		self.listemsgid.append(self.sourcebox)
		self.srctablabels.append(BTab(None))
		self.srctabview.AddTab(self.listemsgid[0], self.srctablabels[0])
		# creare scheda con 
		# scheda=BTab(None)
		# scheda2=BTab(None)
		# self.tabslabels.append(scheda)
		# self.tabslabels.append(scheda2)
		# self.tabslabels=[]
		# self.tabsviews=[]
		# self.tabsviews.append(self.panel) <- BView
		# self.tabsviews.append(self.panel2) <- BView
		# self.maintabview.AddTab(self.tabsviews[0],self.tabslabels[0])
		# self.maintabview.AddTab(self.tabsviews[1],self.tabslabels[1])
		self.transbox=trnsltabbox(tabrc2,'msgstr',altece,self)
		self.listemsgstr.append(self.transbox)
		self.transtablabels.append(BTab(None))
		self.transtabview.AddTab(self.listemsgstr[0], self.transtablabels[0])
		self.lowerbox.AddChild(self.transtabview,None)
		self.lowerbox.AddChild(self.srctabview,None)
		self.sourcestrings = ScrollView(BRect(4 , 4, self.upperbox.Bounds().right*2/3-4, self.upperbox.Bounds().bottom-4), 'sourcestrings')
		sb=self.sourcestrings.sv.ScrollBar(B_HORIZONTAL)
		sbv=self.sourcestrings.sv.ScrollBar(B_VERTICAL)
		dx=sbv.Frame().Width()
		dy=sb.Frame().Height()
		sb.MoveBy(0,0-dy)
		sb.ResizeBy(0-dx,0)
		sbv.MoveBy(0-dx,0)
		sbv.ResizeBy(0,0-dy)
		self.sourcestrings.lv.ResizeBy(0-dx,0-dy)
		self.sourcestrings.sv.ResizeBy(0-dx,0-dy)
		#self.sourcestrings.sv.FindView("_HSB_")
		self.upperbox.AddChild(self.sourcestrings.sv,None)
		
		self.tmscrollsugj=ScrollSugj(BRect(self.upperbox.Bounds().right*2/3+4,4,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom-59), 'ScrollSugj')
		
		if showspell:
			rectcksp=BRect(self.upperbox.Bounds().right-55,self.upperbox.Bounds().bottom-55,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom-4)
			insetcksp=BRect(0,0,rectcksp.Width(),rectcksp.Height())
			insetcksp.InsetBy(5,5)
			self.checkres=BTextView(rectcksp,"checkres",insetcksp,B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM,B_WILL_DRAW|B_FRAME_EVENTS)
			self.font=be_bold_font
			self.font.SetSize(28.0)
			nocolor=rgb_color()
			self.checkres.SetAlignment(alignment.B_ALIGN_CENTER)
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,nocolor)
			self.checkres.SetText("☐",None)
			self.checkres.MakeEditable(False)
			self.upperbox.AddChild(self.checkres,None)
		else:
			fo=BFont()
			self.upperbox.GetFont(fo)
			l=fo.StringWidth("Spellcheck status: disabled")
			rectspellab=BRect(self.upperbox.Bounds().right-l-4,self.upperbox.Bounds().bottom-55,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom-4)
			self.spellabel= BStringView(rectspellab,"spellabel","Spellcheck status: disabled",B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM)
			self.upperbox.AddChild(self.spellabel,None)
		sb=self.tmscrollsugj.sv.ScrollBar(B_HORIZONTAL)
		sbv=self.tmscrollsugj.sv.ScrollBar(B_VERTICAL)
		dx=sbv.Frame().Width()
		dy=sb.Frame().Height()
		sb.MoveBy(0,0-dy)
		sb.ResizeBy(0-dx,0)
		sbv.MoveBy(0-dx,0)
		sbv.ResizeBy(0,0-dy)
		self.tmscrollsugj.lv.ResizeBy(0-dx,0-dy)
		self.tmscrollsugj.sv.ResizeBy(0-dx,0-dy)
		self.upperbox.AddChild(self.tmscrollsugj.sv,None)
		
		# check user accepted languages
		#
		self.overbox=CreateUserBox(self.bckgnd.Frame())#,ordmdata)
		self.AddChild(self.overbox,None)
		self.overbox.Hide()
		
		self.infobox=BBox(BRect(self.lowerbox.Bounds().right+10,self.upperbox.Bounds().Height()+barheight+10,self.bckgnd.Bounds().right-10,self.bckgnd.Bounds().bottom-10),"infobox",B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM,border_style.B_FANCY_BORDER)
		self.infoboxwidth=self.infobox.Bounds().Width()
		self.infoboxheight=self.infobox.Bounds().Height()
		self.bckgnd.AddChild(self.infobox,None)
		
		self.infobox.GetFont(fon)
		s="100000"
		x=fon.StringWidth(s)
		self.valueln=BStringView(BRect(self.infobox.Bounds().right-x-5,self.infobox.Bounds().bottom-fon.Size()-10,self.infobox.Bounds().right-5,self.infobox.Bounds().bottom-5),"line_number",None)
		w=fon.StringWidth("Line number:")
		self.infoln=BStringView(BRect(5,self.infobox.Bounds().bottom-fon.Size()-10,5+w,self.infobox.Bounds().bottom-5),"line_number","Line number:")
		self.valueln.SetAlignment(B_ALIGN_RIGHT)
		self.infobox.AddChild(self.valueln,None)
		self.infobox.AddChild(self.infoln,None)
		self.msgstabview = BTabView(BRect(5.0, 60.0, self.infobox.Bounds().right-5.0, self.infobox.Bounds().bottom-fon.Size()-15.0), 'msgs_tabview',button_width.B_WIDTH_FROM_LABEL,B_FOLLOW_LEFT_RIGHT)
		fun=BFont()
		
		fun.SetSize(10)
		self.msgstabview.SetFont(fun)
		self.msgstablabels=[]
		self.listemsgs=[]
		self.msgsRect=(3,3,self.msgstabview.Bounds().Width()-3,self.msgstabview.Bounds().Height()-3)
		self.listemsgs.append(previoustabbox(self.msgsRect,self))
		self.listemsgs.append(contexttabbox(self.msgsRect,self))
		self.listemsgs.append(commenttabbox(self.msgsRect,self))
		self.listemsgs.append(tcommenttabbox(self.msgsRect,self))
		for i in self.listemsgs:
			self.msgstablabels.append(infoTab(None))#BTab(None))
		i=0
		while i < len(self.listemsgs):
			self.msgstabview.AddTab(self.listemsgs[i], self.msgstablabels[i])
			i+=1
		#for i in self.msgstablabels:
		#	print(type(i))
		#br=self.infobox.Bounds()
		#self.scrollbtabs=BScrollBar(BRect(5,br.bottom-25,br.right-5,br.bottom-5),'tabview_ScrollBar',self.msgstabview,0.0,200.0,orientation.B_HORIZONTAL)
		
		self.msgstabview.SetTabSide(tab_side.kBottomSide)
		self.infobox.AddChild(self.msgstabview,None)
		#self.infobox.AddChild(self.scrollbtabs,None)
		self.msgstabview.Select(2)
		#self.msgstabview.Select(0)
		#print(arg)
		self.writter = threading.Semaphore()
		self.netlock=threading.Semaphore()
		if arg!="":
			f=os.path.abspath(arg)
			if BEntry(f).Exists():
				self.OpenPOFile(f)
	
	def NichilizeTabs(self):
		for i in self.listemsgstr:
			i.trnsl.SelectAll()
			i.trnsl.Clear()
		for i in self.listemsgid:
			i.src.SelectAll()
			i.src.Clear()

	#def NichilizeMsgs(self):
	#	ww=len(self.listemsgs)-1
	#	while ww>-1:
	#		tabboz = self.msgstabview.RemoveTab(ww)
	#		self.listemsgs.pop(ww)
	#		self.msgstablabels.pop(ww)
	#		del tabboz
	#		ww-=1
	#	print(self.listemsgs,self.msgstablabels)
	def NichilizeTM(self):
		if tm:
			self.tmscrollsugj.Clear()
			
	def FrameResized(self,x,y):	
		resiz=False
		if x<1022:#4:
			x=1022#4
			resiz=True
		if y<704:#768:
			y=704#768
			resiz=True
		if resiz:
			self.ResizeTo(x,y)
		w=self.lowerbox.Bounds().Width()
		h=self.lowerbox.Bounds().Height()
		BWindow.FrameResized(self,x,y)
		self.bar.ResizeTo(x,self.bar.Bounds().bottom)
		xx, barheight = self.bar.GetPreferredSize()
		self.upperbox.ResizeTo(x,y/2-barheight-2)
		self.lowerbox.MoveTo(0,y/2+2)
		self.lowerbox.ResizeTo(x-self.spaceright,y-y/2-2)
		self.infobox.MoveTo(self.bckgnd.Bounds().Width()-self.spaceright+10,y-y/2+8)
		self.infobox.ResizeTo(self.infoboxwidth,self.lowerbox.Bounds().Height()-16)
		self.srctabview.ResizeTo(self.lowerbox.Bounds().Width()-4,self.lowerbox.Bounds().Height()/2-4)
		srcrect=self.srctabview.Bounds()#.InsetBy(3.0,3.0)
		self.transtabview.MoveTo(2,self.lowerbox.Bounds().Height()/2+2)
		self.transtabview.ResizeTo(self.lowerbox.Bounds().Width()-4,self.lowerbox.Bounds().Height()/2-4)
		trnsrect=self.transtabview.Bounds().InsetBy(3.0,3.0)
		for i in self.listemsgid:
			i.MoveTo(0,0)
			i.ResizeTo(srcrect.Width()-3,srcrect.Height()-self.srctabview.TabHeight()-3)
		for i in self.listemsgstr:
			i.MoveTo(0,0)
			i.ResizeTo(srcrect.Width()-3,srcrect.Height()-self.transtabview.TabHeight()-3)
		fon=BFont()
		s="100000"
		x=fon.StringWidth(s)
		
		self.infobox.GetFont(fon)
		self.valueln.MoveTo(self.infobox.Bounds().right-x-5,self.infobox.Bounds().bottom-fon.Size()-10)
		self.infoln.MoveTo(5,self.infobox.Bounds().bottom-fon.Size()-10)
		self.msgstabview.ResizeTo(self.infobox.Bounds().right-10,self.infobox.Bounds().bottom-fon.Size()-self.msgstabview.TabHeight()-40)
		
	def Nichilize(self):
		if (len(self.listemsgid)-1) == 1:    #IF THERE'S A PLURAL MSGID, REMOVE IT
				self.srctabview.RemoveTab(1)
				self.listemsgid.pop(1)
				self.srctablabels.pop(1)
		ww=len(self.listemsgstr)-1
		while ww>0:					#removes plural translation tabs
			self.transtabview.RemoveTab(ww)
			self.listemsgstr.pop(ww)
			self.transtablabels.pop(ww)
			ww=ww-1
##### Removing tab 0 on translation tabview for renaming it as msgstr or msgstr[0]
		self.transtabview.RemoveTab(0)
		self.listemsgstr.pop(0)
		self.transtablabels.pop(0)
		
	def OpenPOFile(self, f):
		#controllare mimetype se ok aprire
		#altrimenti se mimetype non è corretto controllare estensione file e aprire con try
		
		#1)pulire tutto
		self.sourcestrings.Clear()
		self.NichilizeTM()
		self.NichilizeTabs()
		#TODO pulire infobox
		#Pulire scrollsugj
		
		#2)controllo mimetype
		filename, file_extension = os.path.splitext(f)
		static = BMimeType()
		mime = BMimeType.GuessMimeType(f,static)
		mimetype = repr(static.Type()).replace('\'','')
		boolgo=False
		try:
			supertype,subtype = mimetype.split('/')
			boolgo=True
		except:
			say = BAlert('Warn', 'This is a workaround, cannot detect correctly the file\'s mimetype', 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			say.Go()
			supertype = "text"
			subtype = "x-gettext-translation"
		if not boolgo:
			# mimetype not detected, check file extnsion
			print(file_extension)
			if not(file_extension in [".po", ".pot", ".mo"]):
				return
		else:
			# file correctly detected ... so open...
			# check user accepted languages
			fileenc = polib.detect_encoding(f)
			self.pof = polib.pofile(f,encoding=fileenc)
			ordmdata=self.pof.ordered_metadata()
			a,b = checklang(ordmdata)
			#overwrite "a", controllo config.ini per info Traduttore
			ent,confile=Ent_config()
			Config.read(confile)
			try:
				self.tname=ConfigSectionMap("Translator")['name']
				self.pemail=ConfigSectionMap("Translator")['mail']
				self.team=ConfigSectionMap("Translator")['team']
				self.temail=ConfigSectionMap("Translator")['ltmail']
			except:
				a=False
			if a:
				if b==-1:
					#non c'è language nei metadati del file po
					say = BAlert('Warn', 'There\'s no language section in metadata! Continue?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
					self.alerts.append(say)
					ret=say.Go()
					if ret==0:
						self.loadPO(f,self.pof)#openfile TODO ############################
					else:
						return
				elif b==1:
					#ci sono altre lingue nel file rispetto a quelle dell'utente
					say = BAlert('Warn', 'This po file is not for your language!', 'OK',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
					self.alerts.append(say)
					ret=say.Go()
				else:
					self.loadPO(f,self.pof)
			else:
				#mostra BBox per la creazione dell'utente
				say = BAlert('Warn', 'Please, fill the fields below, these informations will be written to saved po files and in config.ini', 'OK',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_IDEA_ALERT)
				self.alerts.append(say)
				ret=say.Go()
				self.bckgnd.Hide()
				self.overbox.Show()
	
	def loadPO(self, pth, pof):
		filen, file_ext = os.path.splitext(pth)
		self.wob=False
		backupfile = filen+".temp"+file_ext
		if os.path.exists(backupfile):
			if os.path.getmtime(backupfile)>os.path.getmtime(pth):
				say = BAlert('Backup exist', 'There\'s a recent temporary backup file, open it instead?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				out=say.Go()
				if out == 0:
#					apro il backup
					self.wob=True
					try:
						temppofile = polib.pofile(backupfile,encoding=polib.detect_encoding(backupfile))
						self.handlePO(temppofile,backupfile,self.wob)
					except:
						#BAlert "attenzione il file di backup potrebbe essere rovinato, o non è possibile leggerlo correttamente, verrà usato il file originale"
						#use pof
						self.handlePO(pof,pth,self.wob)
					#carica il po
				else:
					#carica il po originale
					self.handlePO(pof,pth,self.wob)
			else:
				#carica il po originale
				self.handlePO(pof,pth,self.wob)
		else:
			#carica il po originale
			self.handlePO(pof,pth,self.wob)

	def handlePO(self,pof,percors,workonbackup):
		p=BPath(BEntry(percors)).Leaf()
		title=self.Title()+": "+p
		self.SetTitle(title)
		self.pofile = pof
		if workonbackup:
			self.backupfile = percors
			percors = percors.replace('.temp','')
			self.filen, self.file_ext = os.path.splitext(percors)
			encoding = polib.detect_encoding(percors)
			self.encoding=encoding
		else:
			self.filen, self.file_ext = os.path.splitext(percors)	
			self.backupfile= self.filen+".temp"+self.file_ext
			encoding = polib.detect_encoding(percors)
			self.encoding=encoding
		self.orderedmetadata=self.pofile.ordered_metadata()
		self.fp=BFilePanel(B_SAVE_PANEL,None,None,0,False, None, None, True, True)
		pathorig,nameorig=os.path.split(percors)
		self.fp.SetPanelDirectory(pathorig)
		self.fp.SetSaveText(nameorig)
		#ind=0
		#for entry in self.pofile:
		#		ind+=1
		self.litms=[]
		if self.poview[0]:
			for entry in self.pofile.fuzzy_entries():
				#item=None
				if entry and entry.msgid_plural:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
							context = entry.msgctxt
					else:
							context = ""
					msgids=[entry.msgid,entry.msgid_plural]
					lenmsgstr=len(entry.msgstr_plural)
					msgstrs=[]
					xu=0
					while xu<lenmsgstr:
						msgstrs.append(entry.msgstr_plural[xu])
						xu+=1
					item = MsgStrItem(msgids,msgstrs,entry,comments,context,2,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))#.encode(encoding)))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)
				else:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
							context = entry.msgctxt
					else:
							context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,entry,comments,context,2,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))#.encode(encoding)))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)
				self.litms.append(item)
				self.sourcestrings.lv.AddItem(self.litms[-1])
		if self.poview[1]:
			for entry in self.pofile.untranslated_entries():
				if entry and entry.msgid_plural:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
						context = entry.msgctxt
					else:
						context = ""
					msgids=[entry.msgid,entry.msgid_plural]
					lenmsgstr=len(entry.msgstr_plural)
					msgstrs=[]
					xu=0
					while xu<lenmsgstr:
						msgstrs.append(entry.msgstr_plural[xu])
						xu+=1
					item = MsgStrItem(msgids,msgstrs,entry,comments,context,0,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)
				else:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
						context = entry.msgctxt
					else:
						context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,entry,comments,context,0,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)
				self.litms.append(item)
				self.sourcestrings.lv.AddItem(self.litms[-1])
		if self.poview[2]:
			for entry in self.pofile.translated_entries():
				if entry and entry.msgid_plural:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
						context = entry.msgctxt
					else:
						context = ""
					msgids=[entry.msgid,entry.msgid_plural]
					lenmsgstr=len(entry.msgstr_plural)
					msgstrs=[]
					xu=0
					while xu<lenmsgstr:
						msgstrs.append(entry.msgstr_plural[xu])
						xu+=1
					item = MsgStrItem(msgids,msgstrs,entry,comments,context,1,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)					
				else:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
						context = entry.msgctxt
					else:
						context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,entry,comments,context,1,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)					
				self.litms.append(item)
				self.sourcestrings.lv.AddItem(self.litms[-1])
		if self.poview[3]:
			for entry in self.pofile.obsolete_entries():
				if entry and entry.msgid_plural:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
						context = entry.msgctxt
					else:
						context = ""
					msgids=[entry.msgid,entry.msgid_plural]
					lenmsgstr=len(entry.msgstr_plural)
					msgstrs=[]
					xu=0
					while xu<lenmsgstr:
						msgstrs.append(entry.msgstr_plural[xu])
						xu+=1
					item = MsgStrItem(msgids,msgstrs,entry,comments,context,3,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)					
				else:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
						context = entry.msgctxt
					else:
						context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,entry,comments,context,3,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))#.encode(encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))#.encode(encoding)))
					item.SetLineNum(entry.linenum)
				self.litms.append(item)
				self.sourcestrings.lv.AddItem(self.litms[-1])
				
		self.progressinfo=BStatusBar(BRect(5,5,self.infobox.Bounds().right-5,35),'progress',"Progress:", None)#label,trailing_label
		self.potot=len(self.pofile.translated_entries())+len(self.pofile.untranslated_entries())+len(self.pofile.fuzzy_entries())
		self.progressinfo.SetMaxValue(self.potot)
		self.progressinfo.Update(len(self.pofile.translated_entries()),None,str(self.pofile.percent_translated())+"%")
		self.infobox.AddChild(self.progressinfo,None)
		
	def SaveAs(self, p):
		pass
	
	def Save(self, path):
		self.pofile.save(path)
		svdlns=[]  #moved to fix reference before assignment
		if path[-7:] != "temp.po":
			#TODO rileva architettura -> msgfmt-x86 o msgfmt
			execpath = find_executable("msgfmt")
			comtwo = execpath+" -c "+path
			checker = Popen( comtwo.split(' '), stdout=PIPE,stderr=PIPE)
			jessude,err= checker.communicate()
			#svdlns=[]
			for ries in err.decode('utf-8').split('\n'):
				svdlns.append(ries)
				
		msgdigj=str(os.getcwd())+'/messages.mo'
		if os.path.exists(msgdigj):
			os.remove(msgdigj)

		guut = []
		if len(svdlns)>1:
			try:
				#last row (len(x)-1) is always blank
				txttoshow=""
				x=0
				while x<len(svdlns)-2:
					if True:#x==0:
						posuno= svdlns[x].find(':')
						if posuno>-1:
							posuno+=1
							str1=svdlns[x][posuno:]
							posdue=str1.find(':')
							if posdue>-1:
								str2=str1[:posdue]
								rnwt=int(str2)
								polines = []
								with open (path, 'rt') as pf:
									for rie in pf:
										polines.append(rie)
								strtosrc = polines[rnwt-1]
					txttoshow=svdlns[x]
					say = BAlert(svdlns[len(svdlns)-2], txttoshow+"\n\nGo to this error?", 'Yes',"Skip", None, None , 4)
					out=say.Go()
					if out==0:
						#inserire la ricerca per la parola interessata
						guut.append(FindRepTrans())
						guut[len(guut)-1].SetTitle("Find/Replace "+str(len(guut)-1))
						guut[len(guut)-1].Show()
						i = 1
						w = be_app.CountWindows()
						while w > i:
							title=be_app.WindowAt(i).Title()
							if title=="Find/Replace "+str(len(guut)-1):
								mxg=BMessage(1010)
								diciri=strtosrc[8:]
								o=len(diciri)-2
								lockloop=True
								while lockloop:
									if diciri[o]=="\"":
										diciri=diciri[:o]
										lockloop=False
									else:
										if o>0:
											o-=1
										else:
											break
								mxg.AddString('txt',diciri)
								be_app.WindowAt(i).PostMessage(mxg)
							i+=1
					x+=1
			except:
				erout = ""
				for it in svdlns:
					erout=erout + it
				say = BAlert("Generic error",erout, 'OK',None, None, None , 4)
				out=say.Go()
				#self.Looper().PostMessage(ermsg)

		#################################################
		########## This should be done by OS ############
		st=BMimeType("text/x-gettext-translation")
		nd=BNode(path)
		ni = BNodeInfo(nd)
		ni.SetType("text/x-gettext-translation")
		#################################################
		self.writter.release()
	
	def tmcommunicate(self,src):
		self.netlock.acquire()
		#print "mando messaggio per cancellare scrollsugj"
#		showmsg=BMessage(83419)                                                    # valutare se reintrodurre
#		BApplication.be_app.WindowAt(0).PostMessage(showmsg)                       # valutare se reintrodurre
		#try:
		if True:
			if type(src)==str:
				##if it's a string we can request it at the TMserver
					if self.listemsgid[self.srctabview.Selection()].src.Text() == src: #check if it's still the same
						tmsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
						tmsocket.connect((tmxsrv,tmxprt))
						pck=[]
						pck.append(src)#.decode(self.encoding))#'utf-8'
						send_pck=pickle.dumps(pck)
						tmsocket.send(send_pck)
						pck_answer=tmsocket.recv(4096)#1024
						if self.listemsgid[self.srctabview.Selection()].src.Text() == src: #check again if I changed the selection
							answer=pickle.loads(pck_answer)
							sugjmsg=BMessage(5391359)
							ts=len(answer)
							sugjmsg.AddInt16('totsugj',ts)
							x=0
							while x <ts:
								sugjmsg.AddString('sugj_'+str(x),answer[x][0])#.encode('utf-8'))
								sugjmsg.AddInt8('lev_'+str(x),answer[x][1])
								x+=1
							be_app.WindowAt(0).PostMessage(sugjmsg)
						else:
							pass
						tmsocket.close()					
					else:
						pass
			else:
				#we are requesting either to add or remove a translation
				txt0=src[0]
				tmsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				tmsocket.connect((tmxsrv,tmxprt))
				pck=[]
				txt1=src[1]#.encode(self.encoding)
				if txt0==None:
					#add to tm dictionary
					txt2=src[2]#.encode(self.encoding)
					st2=txt2#.decode(self.encoding)
					st2.replace('<','&lt;')
					st2.replace('>','&gt;')
					st1=txt1#.decode(self.encoding)
					st1.replace('<','&lt;')
					st1.replace('>','&gt;')
					pck.append((txt0,st1,st2))
				else:
					#remove from tm dictionary
					txt2=src[2]#.decode(self.encoding)
					txt2.replace('<','&lt;')
					txt2.replace('>','&gt;')
					st1=txt1#.decode(self.encoding)
					st1.replace('<','&lt;')
					st1.replace('>','&gt;')
					pck.append((txt0,st1,txt2))
				send_pck=pickle.dumps(pck)
				tmsocket.send(send_pck)
				tmsocket.close()
		#except:
		#	hidemsg=BMessage(104501)
		#	BApplication.be_app.WindowAt(0).PostMessage(hidemsg)
		self.netlock.release()
	
	def MessageReceived(self, msg):
		if msg.what == B_MODIFIERS_CHANGED:
			value=msg.FindInt32("modifiers")
			self.sem.acquire()
			if value==self.modifiervalue or value==self.modifiervalue+8 or value ==self.modifiervalue+32 or value ==self.modifiervalue+40:
				#"modificatore"
				print("modificatore")
				self.modifier=True
				self.shortcut = False
			elif value == self.modifiervalue+4357 or value==self.modifiervalue+265 or value==self.modifiervalue+289 or value == self.modifiervalue+297:
				#"scorciatoia"
				print("scorciatoia")
				self.shortcut = True
				self.modifier = False
			else:
				#"altro"
				print("altro")
				self.modifier=False
				self.shortcut=False
			self.sem.release()
			return
		elif msg.what == B_KEY_DOWN:	#on tab key pressed, focus on translation or translation of first item list of translations
			key=msg.FindInt32('key')
			if key==38: #tab key
				if self.sourcestrings.lv.CurrentSelection()>-1:
					self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus() ###########à LOOK HERE 
				else:
					self.sourcestrings.lv.Select(0)
					self.sourcestrings.lv.ScrollToSelection()
			elif key in (98,87,54,33):
				if self.sourcestrings.lv.CurrentSelection() < 0:
					self.sourcestrings.lv.Select(0)
					self.sourcestrings.lv.ScrollToSelection()
#				elif key == 61: # s key      ######## TODO: check, because it seems useless
#					if self.sourcestrings.lv.CurrentSelection()>-1:
#						self.sem.acquire()
#						if self.shortcut:
#							BApplication.be_app.WindowAt(0).PostMessage(33)
#						else:
#							pass
#						self.sem.release()
			return
		elif msg.what == 1:
			# Close opened file
			if self.sourcestrings.lv.CountItems()>0:
				self.sourcestrings.lv.DeselectAll()
				self.sourcestrings.Clear()
				self.Nichilize()
				self.NichilizeTM()
				#self.NichilizeMsgs()
				altece2 = self.transtabview.TabHeight()
				tabrc2 = (3.0, 3.0, self.transtabview.Bounds().Width() - 3, self.transtabview.Bounds().Height()-altece2)
				self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece2,self))
				self.transtablabels.append(BTab(None))
				self.transtabview.AddTab(self.listemsgstr[0], self.transtablabels[0])
				self.transtabview.Select(1)									###### bug fix
				self.transtabview.Select(0)
				self.listemsgid[0].src.SelectAll()
				self.listemsgid[0].src.Clear()
				self.srctabview.Draw(self.srctabview.Bounds())
				self.SetTitle("HaiPO 2.0")
				
				#self.srctabview.Draw(self.srctabview.Bounds()) <<< look this!! bug fix
				#self.postabview.RemoveTab(whichrem)
				#self.postabview.Draw(self.postabview.Bounds())
#				self.postabview.Hide()     # <----- Bug fix
#				self.postabview.Show()	   # <----- Bug fix
			return
		elif msg.what == 2:
			if True:     ###### FIX HERE check condition if file is loaded
				if self.listemsgstr[self.transtabview.Selection()].trnsl.tosave:
					print("eventtextvie è cambiato, si esegue save interno")
					#eventtextview changed
					self.listemsgstr[self.transtabview.Selection()].trnsl.Save()
				try:
					Config.read(confile)
					namo=ConfigSectionMap("Translator")['name']
					defname=namo+' <'+ConfigSectionMap("Translator")['mail']+'>'
					grp=ConfigSectionMap("Translator")['team']+' <'+ConfigSectionMap("Translator")['ltmail']+'>'
				except:
					defname=self.pofile.metadata['Last-Translator']
					grp=self.pofile.metadata['Language-Team']
				now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
				savepath=self.filen+self.file_ext

				self.writter.acquire()
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['Language-Team']=grp
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(savepath,)).start()
				#thread.start_new_thread( self.Save, (savepath,) )
			return
		elif msg.what == 3:
			#copy from source from menu
			if self.sourcestrings.lv.CountItems()>-1:
				thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
				thisBlistitem.tosave=True
				tabs=len(self.listemsgstr)-1
				bckpmsg=BMessage(16893)
				bckpmsg.AddInt8('savetype',1)
				bckpmsg.AddInt32('tvindex',self.sourcestrings.lv.CurrentSelection())
				bckpmsg.AddInt8('plurals',tabs)
				#bckpmsg.AddInt32('tabview',self.postabview.Selection())
				if tabs == 0:   #->      if not thisBlistitem.hasplural:                         <-------------------------- or this?
					thisBlistitem.txttosave=thisBlistitem.text#.decode(self.cod)#(self.encoding)
					thisBlistitem.msgstrs=thisBlistitem.txttosave
					bckpmsg.AddString('translation',thisBlistitem.txttosave)#.encode(self.cod))#(self.encoding)) # <------------ check if encode in self.encoding or utf-8
				else:
					thisBlistitem.txttosavepl=[]
					thisBlistitem.txttosave=self.listemsgid[0].src.Text()#.decode(self.cod)#(self.encoding)
					thisBlistitem.msgstrs=[]
					thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
					bckpmsg.AddString('translation',thisBlistitem.txttosave)#.encode(self.cod))#(self.encoding)(self.encoding)) # <------------ check if encode in self.encoding or utf-8
					cox=1
					while cox < tabs+1:
						thisBlistitem.msgstrs.append(self.listemsgid[1].src.Text())#.decode(self.cod))#(self.encoding)(self.encoding))
						thisBlistitem.txttosavepl.append(self.listemsgid[1].src.Text())#.decode(self.cod))#(self.encoding)(self.encoding))
						bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())    #<------- check removed encode(self.encoding)
						cox+=1
				bckpmsg.AddString('bckppath',self.backupfile)
				be_app.WindowAt(0).PostMessage(bckpmsg)

				kmesg=BMessage(130550)
				kmesg.AddInt8('movekind',0)
				be_app.WindowAt(0).PostMessage(kmesg)
			return
		elif msg.what == 735157:
			color=rgb_color()
			color.green=150
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,color)
			self.checkres.SetText("☑")
		elif msg.what == 982757:
			color=rgb_color()
			color.red=150
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,color)
			self.checkres.SetText("☒")
		elif msg.what == 431110173:
			#delete a suggestion on remote tmserver
			txtdel=msg.FindString("sugj")
			srcdel=self.listemsgid[self.srctabview.Selection()].src.Text()
			cmd=("d","e","l")
			mx=[cmd,srcdel,txtdel]
			#thread.start_new_thread( self.tmcommunicate, (mx,) )
			Thread(target=self.tmcommunicate,args=(mx,)).start()
		elif msg.what == 8147420:
			# copy from tm suggestions
			if self.sourcestrings.lv.CurrentSelection()>-1:
				askfor=msg.FindInt8("sel")
				if self.tmscrollsugj.lv.CountItems()>askfor:
					self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.tmscrollsugj.lv.ItemAt(askfor).text,None)
					lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
					self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
					self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
					self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
#						print self.tmscrollsugj.lv.ItemAt(askfor).text #settext con tutte i vari controlli ortografici mettere tosave = True a eventtextview interessato
		elif msg.what == 33:
			#copy from source from keyboard
			if self.sourcestrings.lv.CurrentSelection()>-1:
				#self.cod=self.editorslist[self.postabview.Selection()].encodo
				#cursel=self.editorslist[self.postabview.Selection()]
				thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
				thisBlistitem.tosave=True
				tabs=len(self.listemsgstr)-1
				bckpmsg=BMessage(16893)
				bckpmsg.AddInt8('savetype',1)
				bckpmsg.AddInt32('tvindex',self.sourcestrings.lv.CurrentSelection())
				bckpmsg.AddInt8('plurals',tabs)
				#bckpmsg.AddInt32('tabview',self.postabview.Selection())
				if tabs == 0:   #->      if not thisBlistitem.hasplural:                         <-------------------------- or this?
					thisBlistitem.txttosave=thisBlistitem.text#.decode(self.cod)#(self.encoding)
					thisBlistitem.msgstrs=thisBlistitem.txttosave
					bckpmsg.AddString('translation',thisBlistitem.txttosave)#.encode(self.cod))#(self.encoding)) # <------------ check if encode in self.encoding or utf-8
				else:
					thisBlistitem.txttosavepl=[]
					thisBlistitem.txttosave=self.listemsgid[0].src.Text()#.decode(self.cod)#((self.encoding)
					thisBlistitem.msgstrs=[]
					thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
					bckpmsg.AddString('translation',thisBlistitem.txttosave)#.encode(self.cod))#(self.encoding)) # <------------ check if encode in self.encoding or utf-8
					cox=1
					while cox < tabs+1:
						thisBlistitem.msgstrs.append(self.listemsgid[1].src.Text())#.decode(self.cod))#(self.encoding))
						thisBlistitem.txttosavepl.append(self.listemsgid[1].src.Text())#.decode(self.cod))#(self.encoding))
						bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())    #<------- check removed encode(self.encoding)
						cox+=1
				bckpmsg.AddString('bckppath',self.backupfile)
				be_app.WindowAt(0).PostMessage(bckpmsg)
				if tabs == 0:
					self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.listemsgid[self.srctabview.Selection()].src.Text(),None)
				else:
					p=len(self.listemsgstr)
					pi=0
					while pi<p:
						if pi==0:
							self.listemsgstr[0].trnsl.SetText(self.listemsgid[0].src.Text(),None)
						else:
							self.listemsgstr[pi].trnsl.SetText(self.listemsgid[1].src.Text(),None)
						pi+=1
				self.sourcestrings.sv.Hide()
				self.sourcestrings.sv.Show() #Updates the MsgStrItem
				lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
				self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
				self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
				be_app.WindowAt(0).PostMessage(12343)
			return
		elif msg.what == 12343:
			if self.sourcestrings.lv.CurrentSelection()>-1:
				self.Looper().Lock()
				if True:
				#try:
					self.listemsgstr[self.transtabview.Selection()].trnsl.CheckSpell()
				#except:
				#	pass
				self.Looper().Unlock()
			return
		elif msg.what == 6:
			# Find source
			if len(self.editorslist)>0:
				self.Findsrc = Findsource()
				self.Findsrc.Show()
			return
		elif msg.what == 7:
			# Find/Replace translation
			if len(self.editorslist)>0:
				self.FindReptrnsl = FindRepTrans()
				self.FindReptrnsl.Show()
			return
		elif msg.what == 9:
			#ABOUT
			self.About = AboutWindow()
			self.About.Show()
			return
		elif msg.what == 40:
			self.gensettings=GeneralSettings()
			self.gensettings.Show()
			return
		elif msg.what == 41:
			#USER SETTINGS
			pass #TODO
		elif msg.what == 53:#32:
			#Double clic = translator comment
			if self.sourcestrings.lv.CountItems()>0:
				listsel=self.sourcestrings.lv.CurrentSelection()
				if listsel>-1:
					thisBlistitem=self.sourcestrings.lv.ItemAt(listsel)
					self.tcommentdialog=TranslatorComment(listsel,thisBlistitem)
					self.tcommentdialog.Show()
		elif msg.what == 66:
			# wheel-alive
			self.iwheel+=1
			if self.iwheel==4:
				self.iwheel=0
			#SetText(self.steps[self.iwheel])
			return
		elif msg.what == 16893:
			try:
				Config.read(confile)
				defname=ConfigSectionMap("Translator")['name']
			except:
				defname=self.pofile.metadata['Last-Translator']
			now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
			# save to backup and update the blistitem
			bckppath = msg.FindString('bckppath')
			print("path di backup",bckppath)
			savetype = msg.FindInt8('savetype')
			if savetype == 0: #simple save, used for fuzzy state and metadata change
				self.writter.acquire()
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#thread.start_new_thread( self.Save, (bckppath,) )
				#self.editorslist[self.postabview.Selection()].pofile.save(bckppath)
				return
			elif savetype == 2:
				#save of metadata #TODO: verificare se usato, visto che non abbiamo più multipli file po aperti
				indexroot=msg.FindInt8('indexroot')
				self.writter.acquire()
				self.pofile.metadata['Last-Translator']=defname # metadata saved from po settings
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#thread.start_new_thread( self.Save, (bckppath,) )
				#self.editorslist[indexroot].pofile.save(bckppath)
				return
			elif savetype == 1:
				#save
				if tm:
					needtopush=True
					iterz=self.tmscrollsugj.lv.CountItems()
					iteri=0
					while iteri<iterz:
						try:
							if self.tmscrollsugj.lv.ItemAt(iteri).percent == 100:
								for tabbi in self.listemsgstr:
									if self.tmscrollsugj.lv.ItemAt(iteri).text==tabbi.trnsl.Text():
										needtopush=False
								#TODO: check if trnsl.Text()!=da suggerimento
							iteri+=1
						except:
							#significa che ha problemi con la connessione magari gli elementi di tmscrollsugj.lv sono ErrorItem senza percent?
							break
					if needtopush:
						#print "serve aggiungere a tmx"
						#TODO tmcommunicate si fa in locale
						mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text(),self.listemsgstr[self.transtabview.Selection()].trnsl.Text())
						Thread(target=self.tmcommunicate,args=(mx,)).start()
						#thread.start_new_thread( self.tmcommunicate, (mx,) )


				tvindex=msg.FindInt32('tvindex')
				print(tvindex)
				textsave=msg.FindString('translation')
				tabbi=msg.FindInt8('plurals')
				#intscheda=msg.FindInt32('tabview') #TODO rimuovere usato per multipli po files aperti
				self.writter.acquire()
				entry = self.sourcestrings.lv.ItemAt(tvindex).entry
				if entry and entry.msgid_plural:
						y=0
						textsavepl=[]
						entry.msgstr_plural[0] = textsave#.decode(scheda.encodo)#self.encoding)
						while y < tabbi:
							varname='translationpl'+str(y)                                               ########################### give me one more eye?
							intended=msg.FindString(varname)
							textsavepl.append(intended) #useless???
							y+=1
							entry.msgstr_plural[y]=intended#.decode(scheda.encodo)#self.encoding)
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						if entry.previous_msgid:
							entry.previous_msgid=None
						if entry.previous_msgid_plural:
							entry.previous_msgid_plural=None
						if entry.previous_msgctxt:
							entry.previous_msgctxt=None
				elif entry and not entry.msgid_plural:
						entry.msgstr = textsave#.decode(scheda.encodo)#self.encoding)
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						if entry.previous_msgid:
							entry.previous_msgid=None
						if entry.previous_msgid_plural:
							entry.previous_msgid_plural=None
						if entry.previous_msgctxt:
							entry.previous_msgctxt=None
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#thread.start_new_thread( self.Save, (bckppath,) )
				#scheda.pofile.save(bckppath)
				self.sourcestrings.lv.ItemAt(tvindex).state=1
				self.sourcestrings.lv.ItemAt(tvindex).tosave=False
				self.sourcestrings.lv.ItemAt(tvindex).txttosave=""
				self.sourcestrings.lv.ItemAt(tvindex).txttosavepl=[]
				return
			elif savetype == 3:
				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('tcomment')
				intscheda=msg.FindInt32('tabview') #TODO Rimuovere non ci sono più multipli file aperti
				self.writter.acquire()
				entry = self.sourcestrings.lv.ItemAt(tvindex).entry
				entry.tcomment=textsave#.decode(self.encoding) ##### TODO should be passed scheda.encodo as above
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#thread.start_new_thread( self.Save, (bckppath,) )
				#scheda.pofile.save(bckppath)
				#self.postabview.Select(intscheda)
				self.sourcestrings.lv.DeselectAll()
				self.sourcestrings.lv.Select(tvindex)
				return
			elif savetype == 4:
				textsave=msg.FindString('header')
				intscheda=msg.FindInt32('tabview') # TODO rimuovere non ci sono più multipli file aperti
				self.writter.acquire()
				self.pofile.header=textsave
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#thread.start_new_thread( self.Save, (bckppath,) )
				#scheda.pofile.save(bckppath)
				return
			self.infoprogress.SetText(str(self.pofile.percent_translated()))
			return
		elif msg.what == 54: #selected sourcestring item
			altece2 = self.transtabview.TabHeight()
			tabrc2=(3.0, 3.0, self.transtabview.Bounds().Width() - 3, self.transtabview.Bounds().Height()-altece2)
			#self.NichilizeMsgs()
			if self.sourcestrings.lv.CurrentSelection()>-1:
				item=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
				if item.hasplural:
					beta=len(item.msgstrs)
					self.Nichilize()
					self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr[0]',altece2,self))
					self.transtablabels.append(BTab(None))
					self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
					self.listemsgid.append(srctabbox((3,3,self.listemsgid[0].Bounds()[2]+3,self.listemsgid[0].Bounds()[3]+3),'msgid_plural',altece2))
					self.srctablabels.append(BTab(None))
					self.srctabview.AddTab(self.listemsgid[1], self.srctablabels[1])
					x=len(self.listemsgid)-1
					self.srctabview.SetFocusTab(x,True)
					self.srctabview.Select(x)
					self.srctabview.Select(0)
					self.listemsgid[0].src.SetText(item.msgids[0],None)#.encode(self.encoding))#self.encoding))
					self.listemsgid[1].src.SetText(item.msgids[1],None)#.encode(self.encoding))#self.encoding))
					ww=0
					while ww<beta:
						self.transtablabels.append(BTab(None))
						if ww == 0:
							self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs[0])#.encode(self.encoding))#self.encoding))
							self.transtabview.SetFocusTab(x,True)
							self.transtabview.Select(x)
							self.transtabview.Select(0)
						else:
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr['+str(ww)+']',altece2,self))
							self.listemsgstr[ww].trnsl.SetPOReadText(item.msgstrs[ww])#.encode(self.encoding))#self.encoding))
							self.transtabview.AddTab(self.listemsgstr[ww],self.transtablabels[ww])
						ww=ww+1
				else:
					self.Nichilize()
					self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece2,self))
					self.transtablabels.append(BTab(None))
					self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
#######################################################################
					self.listemsgid[0].src.SetText(item.msgids,None)#.encode(self.encoding),None)#self.encoding))
					self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs)#.encode(self.encoding))#self.encoding))
############################### bugfix workaround? ####################						 
					self.transtabview.Select(1)									#################  <----- needed to fix
					self.transtabview.Select(0)									#################  <----- a bug, tab0 will not appear
					#self.transtabview.Draw(self.transtabview.Bounds())
					#self.srctabview.Select(1)									#################  <----- so forcing a tabview update
					#self.srctabview.Select(0)
					self.srctabview.Draw(self.srctabview.Bounds())
				self.valueln.SetText(str(item.linenum))
				if item.tcomment!="":
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="tcomment":
							i.notify=True
							self.listemsgs[n].tcomment.SetText(item.tcomment,None)
				else:
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="tcomment":
							i.notify=False
							self.listemsgs[n].tcomment.SelectAll()
							self.listemsgs[n].tcomment.Clear()
				if item.comments!="":
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="comment":
							i.notify=True
							self.listemsgs[n].comment.SetText(item.comments,None)
							self.msgstabview.Select(n)
				else:
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="comment":
							i.notify=False
							self.listemsgs[n].comment.SelectAll()
							self.listemsgs[n].comment.Clear()
				if item.context!="":
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="context":
							i.notify=True
							self.listemsgs[n].context.SetText(item.context,None)
							self.msgstabview.Select(n)
				else:
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="context":
							i.notify=False
							self.listemsgs[n].context.SelectAll()
							self.listemsgs[n].context.Clear()
				if item.previous:
					resultxt=""
					bolds=[]
					plain=[]
					color1=(0,0,0,0)
					color2=(50,50,50,0)
					command=[]
					for items in item.previousmsgs:
						actualtxt= items[0]+":\n"+items[1]+"\n"
						resultxt += actualtxt
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="prev_msgid":
							i.notify=True
							self.listemsgs[n].prev.SetText(resultxt,None)
							self.msgstabview.Select(n)
				else:
					for n,i in enumerate(self.msgstablabels):
						if i.Label()=="prev_msgid":
							i.notify=False
							self.listemsgs[n].prev.SelectAll()
							self.listemsgs[n].prev.Clear()
				self.infobox.Hide()
				self.listemsgstr[0].trnsl.MakeFocus()
				self.infobox.Show()
#							beta=len(sorted(entry.msgstr_plural.keys()))
				
				############################ GO TO THE END OF THE TEXT #############################
				lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
				self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
#				num=self.listemsgstr[self.transtabview.Selection()].trnsl.CountLines()
#				self.listemsgstr[self.transtabview.Selection()].trnsl.GoToLine(num)
				self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
				if tm:
					#TODO: azzerare ScrollSugj
					self.tmscrollsugj.Clear()
					#print "eseguo riga: 4984"
					riga=self.listemsgid[self.srctabview.Selection()].src.Text()
					Thread(target=self.tmcommunicate,args=(riga,)).start()
					#thread.start_new_thread( self.tmcommunicate, (self.listemsgid[self.srctabview.Selection()].src.Text(),) )
					
			else:
				if tm:
					self.NichilizeTM()
				self.Nichilize()				
				self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece2,self))
				self.transtablabels.append(BTab(None))
				self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
				################### BUG? ###################
				self.transtabview.Select(1)									#################  <----- needed to fix a bug
				self.transtabview.Select(0)
				#print "ho eseguito transtabview.Draw()"
				#self.transtabview.Draw(self.transtabview.Bounds())
				#############################################
				self.listemsgid[0].src.SelectAll()
				self.listemsgid[0].src.Clear()
			return
		elif msg.what == 74:
			if not(self.bar.FindItem("Fuzzy").IsMarked()):
				self.setMark(0)
			return
		elif msg.what == 75:
			if not(self.bar.FindItem("Untranslated").IsMarked()):
				self.setMark(1)
			return
		elif msg.what == 76:
			if not(self.bar.FindItem("Translated").IsMarked()):
				self.setMark(2)
			return
		elif msg.what == 77:
			if not(self.bar.FindItem("Obsolete").IsMarked()):
				self.setMark(3)
			return
		elif msg.what == 45371:
			percors=msg.FindString("path")
			self.OpenPOFile(percors)
			return
		elif msg.what == 295485:
			self.ofp.Show()
			return
		elif msg.what == 41:
			self.bckgnd.Hide()
			self.overbox.RemoveChild(self.overbox.BtnCancel)
			self.overbox.Show()
			return
		elif msg.what == 312:
			myitem=self.overbox.langlist.lv.ItemAt(self.overbox.langlist.lv.CurrentSelection())
			if myitem.iso!=None:
				for li in self.overbox.ali:
					if myitem.iso == li.iso:
						return
				alitem=LangListItem(myitem.dn,myitem.iso,myitem.s)
				self.overbox.ali.append(alitem)
				self.overbox.acceptedlang.lv.AddItem(self.overbox.ali[-1])
			else:
				self.overbox.lli.append(CustomISO())
				self.overbox.lli[-1].Show()
			self.savell()
			return
		elif msg.what == 412:
			self.overbox.acceptedlang.lv.RemoveItem(self.overbox.acceptedlang.lv.CurrentSelection())
			self.savell()
			return
		elif msg.what == 512:
			iso=msg.FindString("iso")
			newitem=LangListItem("Custom",iso,False)
			self.overbox.ali.append(newitem)
			self.overbox.acceptedlang.lv.AddItem(self.overbox.ali[-1])
			return
		elif msg.what == 612:
			gob=True
			s=self.overbox.name.Text()
			if s == "":
				gob=False
			s=self.overbox.mail.Text()
			if s == "":
				if not self.overbox.email_regex.match(s):
					gob=False
			s=self.overbox.lt.Text()
			if s == "":
				gob=False
			s=self.overbox.ltmail.Text()
			if s == "": #mail language team
				if not self.overbox.email_regex.match(s):
					gob=False
			if self.overbox.acceptedlang.lv.CountItems()==0:
				gob=False
			if gob:
				#save config.ini
				self.overbox.Hide()
				self.bckgnd.Show()
				ent,confile=Ent_config()
				Config.read(confile)
				cfgfile = open(confile,'w')
				try:
					Config.add_section('Translator')
				except:
					pass
				Config.set('Translator','name', self.overbox.name.Text())
				Config.set('Translator','mail', self.overbox.mail.Text())
				Config.set('Translator','team', self.overbox.lt.Text())
				Config.set('Translator','ltmail', self.overbox.ltmail.Text())
				Config.write(cfgfile)
				cfgfile.close()
				Config.read(confile)
				self.savell()
			else:
				say = BAlert('Warn', 'Please, fill the fields below, these informations will be written to saved po files and in config.ini', 'OK',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				ret=say.Go()
				#BAlert missing fields
			return
		elif msg.what == 152: #Save Translator name to config.ini
			ent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				Config.add_section('Translator')
			except:
				pass #section already exists
			Config.set('Translator','name', self.overbox.name.Text())
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			return
		elif msg.what == 153: #Save Translator name to config.ini
			s=self.overbox.mail.Text()
			if self.overbox.email_regex.match(s):
				self.overbox.mail.MarkAsInvalid(False)
			else:
				self.overbox.mail.MarkAsInvalid(True)
				return
			ent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				Config.add_section('Translator')
			except:
				pass #section already exists
			Config.set('Translator','mail', self.overbox.mail.Text())
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			return
		elif msg.what == 154: #Save Translator name to config.ini
			ent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				Config.add_section('Translator')
			except:
				pass #section already exists
			Config.set('Translator','team', self.overbox.lt.Text())
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			return
		elif msg.what == 155: #Save Translator name to config.ini
			s=self.overbox.ltmail.Text()
			if self.overbox.email_regex.match(s):
				self.overbox.ltmail.MarkAsInvalid(False)
			else:
				self.overbox.ltmail.MarkAsInvalid(True)
				return
			ent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				Config.add_section('Translator')
			except:
				pass #section already exists
			Config.set('Translator','ltmail', self.overbox.ltmail.Text())
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			return
		elif msg.what == 112118:
			#launch a delayed check
			oldtext=msg.FindString('oldtext')
			#cursel=msg.FindInt8('cursel')
			indexBlistitem=msg.FindInt32('indexBlistitem')
			tabs=len(self.listemsgstr)-1
			if cursel == self.postabview.Selection():
				tmp=self.editorslist[cursel]
				if indexBlistitem == self.sourcestrings.lv.CurrentSelection():
					if self.listemsgstr[self.transtabview.Selection()].trnsl.oldtext != self.listemsgstr[self.transtabview.Selection()].trnsl.Text():  ### o è meglio controllare nel caso di plurale tutti gli eventtextview?
						self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			self.intime=time.time()
			return
		elif msg.what == 130550: # change listview selection
			#print "changing selection"
			movetype=msg.FindInt8('movekind')
			#if tm:
			#	for items in self.scrollsugj.lv:
			#		
			if tm:
				self.NichilizeTM() #AZZERAMENTO TM PANEL
			if movetype == 0:
				#select one down
				if (self.sourcestrings.lv.CurrentSelection()>-1) and (self.sourcestrings.lv.CurrentSelection()<self.sourcestrings.lv.CountItems()):
					self.sourcestrings.lv.Select(self.sourcestrings.lv.CurrentSelection()+1)
					self.sourcestrings.lv.ScrollToSelection()
				elif self.sourcestrings.lv.CurrentSelection()==-1:
					self.sourcestrings.lv.Select(0)
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif movetype == 1:
				#select one up
				if self.sourcestrings.lv.CurrentSelection()>0 :
					self.sourcestrings.lv.Select(self.sourcestrings.lv.CurrentSelection()-1)
				elif self.sourcestrings.lv.CurrentSelection()==-1:
					self.sourcestrings.lv.Select(self.sourcestrings.lv.CountItems()-1)
				self.sourcestrings.lv.ScrollToSelection()
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif movetype == 2:
				#select one page up
				thisitem=self.sourcestrings.lv.CurrentSelection()
				if thisitem > -1:
					pass
				else:
					thisitem=0
				rectangular=self.sourcestrings.lv.ItemFrame(thisitem)
				hitem=rectangular.Height()#rectangular[3]-rectangular[1]
				rectangular=self.sourcestrings.lv.Bounds()
				hwhole=rectangular.Height()#rectangular[3]-rectangular[1]
				page=int(hwhole//hitem)
				if self.sourcestrings.lv.CurrentSelection()>(page-1) :
					self.sourcestrings.lv.Select(self.sourcestrings.lv.CurrentSelection()-page)
				else:
					self.sourcestrings.lv.Select(0)
				self.sourcestrings.lv.ScrollToSelection()
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif movetype == 3:
				#select one page down
				thisitem=self.sourcestrings.lv.CurrentSelection()
				if thisitem > -1:
					pass
				else:
					thisitem=0
				rectangular=self.sourcestrings.lv.ItemFrame(thisitem)
				hitem=rectangular.Height()#rectangular[3]-rectangular[1]
				rectangular=self.sourcestrings.lv.Bounds()
				hwhole=rectangular.Height()#rectangular[3]-rectangular[1]
				page=int(hwhole//hitem)
				if (self.sourcestrings.lv.CurrentSelection()>-1) and (self.sourcestrings.lv.CurrentSelection()<self.sourcestrings.lv.CountItems()-page):
					self.sourcestrings.lv.Select(self.sourcestrings.lv.CurrentSelection()+page)	
				else:
					self.sourcestrings.lv.Select(self.sourcestrings.lv.CountItems()-1)	
				self.sourcestrings.lv.ScrollToSelection()
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif  movetype == 4:
				#select next untranslated (or needing work) string
				if (self.sourcestrings.lv.CurrentSelection()>-1):
					spice = self.sourcestrings.lv.CurrentSelection()+1
					if spice == self.sourcestrings.lv.CountItems():
						spice = 0
				else:
					self.sourcestrings.lv.Select(0)
					self.sourcestrings.lv.ScrollToSelection()
					spice=0
				tt=0
				tt=spice
				counting=0
				lookingfor = True
				max = self.sourcestrings.lv.CountItems()
				while lookingfor:
					blistit=self.sourcestrings.lv.ItemAt(tt)
					if blistit.state==0 or blistit.state==2:
						lookingfor = False
						self.sourcestrings.lv.Select(tt)
						self.sourcestrings.lv.ScrollToSelection()
					tt+=1
					counting +=1
					if counting == max:
						lookingfor = False
					if tt==max:
						tt=0
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
			try:
				if thisBlistitem.tosave: #it happens when something SOMEHOW has not been saved
					print("testo da salvare (this shouldn\'t happen)",thisBlistitem.txttosave)
			except:
				pass
			if self.listemsgstr[self.transtabview.Selection()].trnsl.Text()!="":
				be_app.WindowAt(0).PostMessage(333111)
			#NON AGGIUNGERE QUI RICHIESTA TM PANEL
			return
		elif msg.what == 333111:
			self.speloc.acquire()
			self.intime=time.time()
			self.speloc.release()
			return	
			
		BWindow.MessageReceived(self, msg)
	
	def savell(self):
		isos=[]
		for it in self.overbox.acceptedlang.lv.Items():
			isos.append(it.iso)
		sout=",".join(isos)
		ent,confile=Ent_config()
		Config.read(confile)
		cfgfile = open(confile,'w')
		try:
			Config.add_section('Translator')
		except:
			pass #section already exists
		Config.set('Translator','langs', sout)
		Config.write(cfgfile)
		cfgfile.close()
		Config.read(confile)

	def setMark(self,index):
		x=0
		while x!=len(self.viewarr):
			if x==index:
				self.viewarr[x].SetMarked(1)
			else:
				self.viewarr[x].SetMarked(0)
			x+=1
		self.sort=index
		#perc=BPath()
		#find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
		#datapath=BDirectory(perc.Path()+"/HaiPO2")
		#ent=BEntry(datapath,perc.Path()+"/HaiPO2")
		#ent.GetPath(perc)
		#confile=BPath(perc.Path()+'/config.ini',None,False)
		ent,confile=Ent_config()
		Config.read(confile)
		cfgfile = open(confile,'w')
		if not ("General" in Config.sections()):
			Config.add_section("General")
		Config.set('General','sort', str(self.sort))
		Config.write(cfgfile)
		cfgfile.close()
		Config.read(confile)

class CustomISO(BWindow):
	def __init__(self):
		a=display_mode()
		BScreen().GetMode(a)
		w=a.virtual_width
		h=a.virtual_height
		fon=BFont()
		BWindow.__init__(self, BRect(w/2-200, h/2-fon.Size(), w/2+200, h/2+fon.Size()),"CustomISO",window_type.B_BORDERED_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		self.bckgnd=BBox(self.Bounds(),"bckgnd_customiso",B_FOLLOW_NONE,B_WILL_DRAW,border_style.B_NO_BORDER)
		self.input=BTextControl(self.bckgnd.Bounds(),"isoinput","ISO code:","",BMessage(252))
		self.bckgnd.AddChild(self.input,None)
		self.AddChild(self.bckgnd,None)
	def MessageReceived(self, msg):
		if msg.what == 252:
			mg=BMessage(512)
			mg.AddString("iso",self.input.Text())
			be_app.WindowAt(0).PostMessage(mg)
			self.Quit()
		BWindow.MessageReceived(self,msg)
		
class App(BApplication):
	def __init__(self):
		BApplication.__init__(self, "application/x-python-HaiPO2")
		self.realargs=[]
		self.Wins=[]
		self.SetPulseRate(1000000)
	def ReadyToRun(self):
		if len(self.realargs) == 0:
			self.Wins.append(MainWindow(""))
			self.Wins[-1].Show()
		else:
			for i in self.realargs:
				self.Wins.append(MainWindow(i))
				self.Wins[-1].Show()
	def ArgvReceived(self,num,args):
		realargs=args
		if args[1][-8:]=="HaiPO.py":
			realargs.pop(1)
			realargs.pop(0)
			self.realargs=realargs
	def RefsReceived(self, msg):
		if msg.what == B_REFS_RECEIVED:
			i = 0
			while True:
				try:
					exitr=False
					er = entry_ref()
					rito=msg.FindRef("refs", i,er)
					entry = BEntry(er,True)
					if entry.Exists():
						percors=BPath()
						entry.GetPath(percors)
						ofpmsg=BMessage(45371)
						ofpmsg.AddString("path",percors.Path())
						be_app.WindowAt(0).PostMessage(ofpmsg)
					else:
						break
				except:
					exitr=True
				if exitr:
					break
				i+=1
		BApplication.RefsReceived(self,msg)
	def Pulse(self):
		be_app.WindowAt(0).PostMessage(BMessage(66))
def main():
	global be_app
	be_app = App()
	be_app.Run()
	
 
if __name__ == "__main__":
    main()