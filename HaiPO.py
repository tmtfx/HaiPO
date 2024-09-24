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
from Be.Font import B_BOLD_FACE,B_ITALIC_FACE

from Be.InterfaceDefs import *
from Be.StorageDefs import node_flavor
from Be.TypeConstants import *
from Be.Accelerant import display_mode
from Be.GraphicsDefs import rgb_color
from Be.TabView import tab_side
from Be.TextView import text_run,text_run_array

import configparser,struct,threading,os,polib,re,datetime,time#,babel
import enchant
import pickle,socket,os,sys,html
from translate.storage.tmx import tmxfile
from Levenshtein import distance as lev
from distutils.spawn import find_executable
from subprocess import Popen,STDOUT,PIPE
import socket,pickle,unicodedata
from threading import Thread
from babel import Locale
global evstyle
evstyle=threading.Semaphore()

version='HaiPO 2.0 beta'
(appname,ver,state)=version.split(' ')

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

def startinserting(stile,errors):
	fontz=BFont()
	fontz.SetFace(B_BOLD_FACE) #strikeout and underscore don't work
	fontx=BFont()
	fontx.SetFace(B_ITALIC_FACE)
	for er in errors:
		if len(er.sugg)>0:
			stile.append((er.pos, fontz, (255,0,0,0)))
			stile.append(((er.pos+len(er.word)), be_plain_font, (0,0,0,0)))
		else:
			#type 1 no suggestions
			stile.append((er.pos, fontx, (255,0,0,0)))
			stile.append(((er.pos+len(er.word)), be_plain_font, (0,0,0,0)))
	return stile


class ScrollView:
	HiWhat = 53 #Doppioclick
	SectionSelection = 54

	def __init__(self, rect, name):
		self.lv = MyListView(rect, name, list_view_type.B_SINGLE_SELECTION_LIST)
		self.lv.SetResizingMode(B_FOLLOW_ALL_SIDES)
		self.lv.SetSelectionMessage(BMessage(self.SectionSelection))
		self.lv.SetInvocationMessage(BMessage(self.HiWhat))
		self.sv = BScrollView(name, self.lv,B_FOLLOW_NONE,0,True,True,border_style.B_FANCY_BORDER)
		self.sv.SetResizingMode(B_FOLLOW_ALL_SIDES)
	def Clear(self):
		self.lv.DeselectAll()
		self.lv.MakeEmpty()
	def reload(self,arrayview,pofile,encoding):
		self.occumemo=[]
		i=0
		self.Clear()
		if arrayview[0]:
			for entry in pofile.fuzzy_entries():
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
					item.SetLineNum(entry.linenum)
				self.lv.AddItem(item)
		if arrayview[1]:
			for entry in pofile.untranslated_entries():
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
					item.SetLineNum(entry.linenum)				
				self.lv.AddItem(item)
		if arrayview[2]:
			for entry in pofile.translated_entries():
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
					item.SetLineNum(entry.linenum)					
				self.lv.AddItem(item)
		if arrayview[3]:
			for entry in pofile.obsolete_entries():
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
					item.SetLineNum(entry.linenum)					
				self.lv.AddItem(item)
			
	def SelectedText(self):
			return self.lv.ItemAt(self.lv.CurrentSelection()).Text()

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

class MyListView(BListView):
	def __init__(self, frame, name, type):
		BListView.__init__(self, frame, name, type)
	
	def MouseDown(self,point):
		if self.CurrentSelection() >-1:
			if self.ItemAt(self.CurrentSelection()).hasplural:
				lmsgstr=be_app.WindowAt(0).listemsgstr
				lung=len(lmsgstr)
				bonobo=False
				pick=0
				while pick<lung:
					thistranslEdit=lmsgstr[pick].trnsl
					if thistranslEdit.tosave:
						bonobo=True
					pick+=1
				if bonobo:
					thistranslEdit.Save() #it's not importat which EventTextView launches the Save() procedure, it will save both anyway
			else:
				itemtext=be_app.WindowAt(0).listemsgstr[0].trnsl
				if itemtext.tosave:
					if itemtext.Text()!= itemtext.oldtext:
						itemtext.Save()
			if showspell:
				be_app.WindowAt(0).PostMessage(333111)
			if tm:
				cirmsg=BMessage(738033)
				cirmsg.AddString('s',self.ItemAt(self.CurrentSelection()).Text())
				be_app.WindowAt(0).PostMessage(cirmsg)
#				thread.start_new_thread( self.tmcommunicate, (self.listemsgid[self.srctabview.Selection()].src.Text(),) )
		return BListView.MouseDown(self,point)

class KListView(BListView):
	def __init__(self,frame, name,type):
		BListView.__init__(self, frame, name, type,B_FOLLOW_RIGHT|B_FOLLOW_TOP)
	def KeyDown(self,char,bytes):
		if ord(char) == 127:
			delmsg=BMessage(431110173)
			delmsg.AddString("sugj",self.ItemAt(self.CurrentSelection()).Text())
			be_app.WindowAt(0).PostMessage(delmsg)
			self.RemoveItem(self.ItemAt(self.CurrentSelection()))
		return BListView.KeyDown(self,char,bytes) # TODO: check why this was commented out

class ScrollSugj:
	HiWhat = 141# Doubleclick --> paste to trnsl TextView
	SectionSelection = 140
	def __init__(self, rect, name):
		self.lv = KListView(rect, name, list_view_type.B_SINGLE_SELECTION_LIST)
		self.lv.SetInvocationMessage(BMessage(self.HiWhat))
		self.lv.SetSelectionMessage(BMessage(self.SectionSelection))
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
	def __init__(self,listindex,item,backupfile):#,oldsize):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		self.backupfile=backupfile
		ix=bounds.left
		iy=bounds.top
		fx=bounds.right
		fy=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		be_plain_font.SetSize(14)
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
			self.tcommentview.SetText(self.item.tcomment,None)
		#be_plain_font.SetSize(oldsize)
		
	def Save(self):
		bckpmsg=BMessage(16893)
		bckpmsg.AddInt8('savetype',3)
		bckpmsg.AddInt32('tvindex',self.listindex)
		bckpmsg.AddString('tcomment',str(self.item.tcomment))
		bckpmsg.AddString('bckppath',self.backupfile)
		be_app.WindowAt(0).PostMessage(bckpmsg)
		

	def MessageReceived(self, msg):
		if msg.what == 5252:
			self.item.tcomment=self.tcommentview.Text()
			self.Save()
			mxg=BMessage(7485)
			msg.AddBool("First_step",True)
			be_app.WindowAt(0).PostMessage(mxg)
			mxg=BMessage(7485)
			msg.AddBool("First_step",False)
			msg.AddInt32('tvindex',self.listindex)
			be_app.WindowAt(0).PostMessage(mxg)
			self.Quit()
		else:	
			return BWindow.MessageReceived(self, msg)

class translationtabview(BTabView):
	def __init__(self,frame,name,superself):#width,risizingMode,flags,
		self.superself=superself
		BTabView.__init__(self,frame,name,button_width.B_WIDTH_AS_USUAL,B_FOLLOW_LEFT_RIGHT)
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
	def MouseDown(self,point):
		numtabs=len(self.superself.listemsgstr)
		
		gg=0
		while gg<numtabs:
			if (point.x>=self.TabFrame(gg).left) and (point.x<=self.TabFrame(gg).right) and (point.y>=self.TabFrame(gg).top) and (point.y<=self.TabFrame(gg).bottom):
				self.superself.srctabview.Select(gg)
			gg=gg+1
		be_app.WindowAt(0).PostMessage(12343)
		BTabView.MouseDown(self,point)
		self.superself.listemsgstr[self.Selection()].trnsl.MakeFocus()
		lngth=self.superself.listemsgstr[self.Selection()].trnsl.TextLength()
		self.superself.listemsgstr[self.Selection()].trnsl.Select(lngth,lngth)
		self.superself.listemsgstr[self.Selection()].trnsl.ScrollToSelection()

class sourcetabview(BTabView):
	def __init__(self,frame,name,superself):
		self.superself=superself
		BTabView.__init__(self,frame,name,button_width.B_WIDTH_AS_USUAL,B_FOLLOW_LEFT_RIGHT)
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
	def MouseDown(self,point):
		numtabs=len(self.superself.listemsgstr)
		gg=0
		while gg<numtabs:
			if (point.x>=self.TabFrame(gg).left) and (point.x<=self.TabFrame(gg).right) and (point.y>=self.TabFrame(gg).top) and (point.y<=self.TabFrame(gg).bottom):
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
	obsolete = 3
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
			self.text = msgids[0]
			self.textpl = msgids[1]
		else:
			self.text = msgids
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
		if self.IsSelected() or complete:
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
		self.oldtextloaded=False
		self.tosave=False
		color=rgb_color()
		BTextView.__init__(self,frame,name,textRect,be_plain_font,color,resizingMode,flags)
		self.mousemsg=struct.unpack('!l', b'_MMV')[0]
		self.dragmsg=struct.unpack('!l', b'MIME')[0]
		self.dragndrop = False
		self.event= threading.Event()
		self.SetStylable(1)
		self.evstile=[]
		self.pop = BPopUpMenu('popup')
		
	def Save(self):
		thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
		thisBlistitem.tosave=True
		tabs=len(self.superself.listemsgstr)-1
		bckpmsg=BMessage(16893)
		bckpmsg.AddInt8('savetype',1)
		bckpmsg.AddInt32('tvindex',self.superself.sourcestrings.lv.CurrentSelection())
		bckpmsg.AddInt8('plurals',tabs)
		if tabs == 0:
			thisBlistitem.txttosave=self.Text()
			thisBlistitem.msgstrs=self.Text()
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
		else:
			thisBlistitem.txttosavepl=[]
			thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
			thisBlistitem.msgstrs=[]
			thisBlistitem.msgstrs.append(self.superself.listemsgstr[0].trnsl.Text())
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
			cox=1
			while cox < tabs+1:
				thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text())
				thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
				bckpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgstr[cox].trnsl.Text())
				cox+=1
		#print("da eventtextview.Save backupfile:",self.superself.backupfile)
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

#	def MouseDown(self,point):
#		self.superself.sem.acquire()
#		self.mod=self.superself.modifier
#		self.superself.sem.release()
#		return BTextView.MouseDown(self,point)

	def MouseUp(self,point):
		self.superself.drop.acquire()
		if self.dragndrop:
			indexBlistitem=self.superself.sourcestrings.lv.CurrentSelection()
			name=time.time()
			BTextView.MouseUp(self,point)
			Thread(target=self.checklater,args=(str(name), self.Text(),indexBlistitem)).start()
			self.dragndrop = False
			self.superself.drop.release()
			return
		self.superself.drop.release()
		if showspell:
			self.superself.sem.acquire()
			self.mod=self.superself.modifier
			self.superself.sem.release()
			if self.mod:
				self.superself.sem.acquire()
				self.superself.modifier=False
				self.superself.sem.release()
				ubi1,ubi2=self.GetSelection()
				if ubi1 == ubi2:
					(ubi1,ubi2)= self.FindWord(ubi1)
				tot,bc=byte_count(self.Text())
				i=0
				counted=0
				perau=""
				#risali a posizione parola in base a bytes (ubi1 e ubi2 sono offsets in bytes)
				while i<len(bc):
					if counted>ubi1-1 and counted<ubi2+1:
						perau=perau+bc[i][0]
					counted+=bc[i][1]
					if counted>ubi2:
						break
					i+=1
				if perau!="":
					sugg=self.superself.spellchecker.suggest(perau)
					menus=[]
					sut=len(sugg)
					ru=0
					while ru <sut:
						menus.append((ru, sugg[ru]))
						ru+=1
					self.pop = BPopUpMenu('popup')
					for aelem in menus:
						msz = BMessage(9631)
						msz.AddInt16('index',aelem[0])
						msz.AddString('sugg',aelem[1])
						msz.AddString('sorig',perau)
						msz.AddInt32('indi',ubi1)
						msz.AddInt32('indf',ubi2)
						self.pop.AddItem(BMenuItem(aelem[1], msz," ",0))
					pointo=self.PointAt(ubi2)
					self.ConvertToScreen(pointo[0])#overwrites pointo[0] with screen BPoint values
					x = self.pop.Go(pointo[0], True,False,False)
					if x:
						self.superself.Looper().PostMessage(x.Message())
		return BTextView.MouseUp(self,point)

	def MessageReceived(self, msg):
		if msg.what in [B_CUT,B_PASTE]:
			#print("da EventTextView rilevato cut o paste")
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
				#print(mexico)
			except:
				pass

		return BTextView.MessageReceived(self,msg)

	def KeyDown(self,char,bytes):
		try:
			ochar=ord(char)
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
				#fine=len(self.oldtext)
				fine,bca=byte_count(self.oldtext)
				self.Select(fine,fine)
				be_app.WindowAt(0).PostMessage(12343)
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
						thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
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
		
	def CheckSpell(self):
		try:
			txt=self.Text()
			indi,indf=self.GetSelection()
			ret=True
			error_font=be_bold_font
			error_font.SetSize(self.superself.oldsize)
			normal_font=be_plain_font
			normal_font.SetSize(self.superself.oldsize)
			error_color=rgb_color()
			error_color.red=255
			normal_color=rgb_color()
			
			TXT_ARR=[text_run()]
			TXT_ARR[-1].offset=0
			TXT_ARR[-1].font=normal_font
			TXT_ARR[-1].color=normal_color
			
			
			newarr=[]
			txtarr=get_all_splits(txt)
			for w in txtarr:
				if w[0]:
					parola=w[1]
					l=[chr for chr in parola]
					for n,c in enumerate(l):
						if c in inclusion:
							pass #è un carattere da accettare
						else:
							if unicodedata.category(c) in esclusion:
								if n+1==len(parola):
									eliso=parola[n:]
									t,lc=byte_count(eliso)
									parola=parola[:n]
									newvalue=w[2]-t
									w=(w[0],w[1],newvalue,w[3])
								else:
									parola=parola[:n]+" "+parola[n+1:]
					if not self.superself.spellchecker.check(parola):
						ret=False
						TXT_ARR.append(text_run())
						TXT_ARR[-1].offset=w[3]
						TXT_ARR[-1].font=error_font
						TXT_ARR[-1].color=error_color
						TXT_ARR.append(text_run())
						TXT_ARR[-1].offset=w[3]+w[2]
						TXT_ARR[-1].font=normal_font
						TXT_ARR[-1].color=normal_color

			#Method 1: Maybe this creates memory leaks as my_txt_run_arr is not freed/destroyed?
			#my_txt_run_arr=BTextView.AllocRunArray(len(TXT_ARR))
			#my_txt_run_arr.runs=TXT_ARR
			#self.SetText(txt,my_txt_run_arr)
			#Method 2: Implemented in Haiku-PyAPI side text_run_array is automatically set and destroyed within SetText function
			self.SetText(txt,TXT_ARR)
			
			self.Select(indi,indf)
			return ret
		except:
			#be_app.WindowAt(0).PostMessage(12343)
			return None
		#return ret
def find_byte(lookf,looka,offset=0):
	retc=looka.find(lookf,offset)
	if retc>-1:
		trunc=looka[:retc]
		return byte_count(trunc)[0]
	else:
		return -1
def byte_count(stringa, encoding='utf-8'):
		byte_counts = []
		start = 0
		total = 0
		for char in stringa:
			end = start + len(char.encode(encoding))
			total+=(end- start)
			byte_counts.append((char,end - start))
			start = end
		return (total,byte_counts)

def is_text_before_first(text,word):
	r=text.find(word)
	if r==-1:
		return(False,None)
	elif r==0:
		return(False,"")
	else:
		return(True,text[:r])

def get_all_splits(text):
	words = text.split()
	newarr=[]
	spacing_list = []
	i=0
	byte_offset=0
	b,t=is_text_before_first(text,words[0])
	if b:
		bc=byte_count(t)
		newarr.append((False,t,bc[0],byte_offset))#False = non analizzare con spellcheck
		text=text[:text.find(words[0])]
		byte_offset+=bc[0]
	while i<len(words)-1:
		bc=byte_count(words[i])
		newarr.append((True,words[i],bc[0],byte_offset))
		byte_offset+=bc[0]
		text=text[text.find(words[i])+len(words[i]):]
		tst=text[:text.find(words[i+1])]
		bc=byte_count(tst)
		newarr.append((False,tst,bc[0],byte_offset))
		byte_offset+=bc[0]
		text=text[text.find(words[i+1]):]
		words=text.split()
		
	bc=byte_count(words[-1])
	newarr.append((True,words[-1],bc[0],byte_offset))
	byte_offset+=bc[0]
	text=text[text.find(words[-1])+len(words[-1]):]
	if text!="":
		bc=byte_count(text)
		newarr.append((False,text,bc[0],byte_offset))

	return newarr


class srcTextView(BTextView):
	def __init__(self,frame,name,textRect,resizingMode,flags):
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)
		self.SetStylable(1)
		self.spaces=["\\x20","\\xc2\\xa0","\\xe1\x9a\\x80","\\xe2\\x80\\x80","\\xe2\\x80\\x81","\\xe2\\x80\\x82","\\xe2\\x80\\x83","\\xe2\\x80\\x84","\\xe2\\x80\\x85","\\xe2\\x80\\x86","\\xe2\\x80\\x87","\\xe2\\x80\\x88","\\xe2\\x80\\x89","\\xe2\\x80\\x8a","\\xe2\\x80\\x8b","\\xe2\\x80\\xaf","\\xe2\\x81\\x9f","\\xe3\\x80\\x80"]
	def Draw(self,suaze):
		BTextView.Draw(self,suaze)
		self.font = be_plain_font
		tst=self.Text()
		#hrdwrk= self.Text()
		#tst=hrdwrk
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
	def __init__(self,frame):
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
		oldsize=fon.Size()
		fon.SetSize(10)
		owner.SetFont(fon)
		#owner.SetHighColor(200,200,0,0)
		#owner.SetLowColor(255,255,255,255)
		BTab.DrawLabel(self,owner,frame)
		fon.SetSize(oldsize)
		#owner.SetFont(fon)
		

class FindRepTrans(BWindow):
	kWindowFrame = BRect(250, 150, 755, 317)
	kWindowName = "Find/Replace translation"
	alerts = []
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l=bounds.left
		t=bounds.top
		r=bounds.right
		b=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		be_plain_font.SetSize(14)
		h=be_plain_font.Size()
		#h=round(self.underframe.GetFontHeight()[0])
		kButtonFrame1 = BRect(r*2/3+5,69,r-5,104)
		kButtonName1 = "Search"
		self.SearchButton = BButton(kButtonFrame1, kButtonName1, kButtonName1, BMessage(5348))
		self.underframe.AddChild(self.SearchButton,None)
		kButtonFrame2 = BRect(r/3+5,69,r*2/3-5,104)
		kButtonName2 = "Replace"
		self.ReplaceButton = BButton(kButtonFrame2, kButtonName2, kButtonName2, BMessage(10240))#7047))
		self.underframe.AddChild(self.ReplaceButton,None)
		self.casesens = BCheckBox(BRect(5,79,r/2-15,104),'casesens', 'Case sensistive', BMessage(222))
		self.casesens.SetValue(1)
		self.underframe.AddChild(self.casesens,None)
		self.looktv=BTextControl(BRect(5,5,r-5,32),'txttosearch','Search:','',BMessage(8046))
		self.looktv.SetDivider(60.0)
		self.underframe.AddChild(self.looktv,None)
		self.looktv.MakeFocus()
		self.reptv=BTextControl(BRect(5,37,r-5,64),'replacetxt','Replace:','',BMessage(8046))
		self.reptv.SetDivider(60.0)
		self.underframe.AddChild(self.reptv,None)
		self.pb=BStatusBar(BRect(5,b-63,r-5,b-5),"searchpb",None,None)
		#self.pb.SetBarHeight(float(24))
		self.underframe.AddChild(self.pb,None)
		lista=be_app.WindowAt(0).sourcestrings.lv
		total=lista.CountItems()
		self.pb.SetMaxValue(float(total))
		indaco=lista.CurrentSelection()
		self.pb.Update(float(indaco),None,None)
		self.ei=0
		self.ef=0
		#self.encoding=BApplication.be_app.WindowAt(0).encoding
		#self.encoding = be_app.WindowAt(0).encoding
		i = 1
		#w = be_app.CountWindows()
		#while w > i:
		#	if be_app.WindowAt(i).Title()==self.kWindowName:
		#		self.thiswindow=i
		#	i=i+1

	def MessageReceived(self, msg):
		if msg.what == 5348:
			self.pb.Hide()
			self.pb.Show()
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
				#be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
				self.PostMessage(deltamsg)
				#tl = len(self.looktv.Text())
				tl = byte_count(self.looktv.Text())[0]
				max = total
				now = indaco
				lastvalue=now
				partial = False
				partiali = False
				loopa =True
				epistola = BMessage(963741)
				scrollmsg = BMessage(1712)
				while loopa:
					now+=1
					if now < total:
							delta=float(now-lastvalue)
							deltamsg=BMessage(7047)
							deltamsg.AddFloat('delta',delta)
							#be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
							self.PostMessage(deltamsg)
							lastvalue=now
							blister=lista.ItemAt(now)
							if self.casesens.Value():
								if blister.hasplural:
									for ident,items in enumerate(blister.msgstrs):#enumerate(values):
										# TODO ERR: find ritorna la posizione del carattere non del byte
										ret=find_byte(self.looktv.Text(),items)
										#ret = items.encode(self.encoding).find(self.looktv.Text())
										#ret = items.find(self.looktv.Text())
										if ret >-1:
											scrollmsg.AddInt32("where",now)
											be_app.WindowAt(0).PostMessage(scrollmsg)
											#lista.Select(now)
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
									# TODO ERR: find ritorna la posizione del carattere non del byte
									ret=find_byte(self.looktv.Text(),blister.msgstrs)	
									#ret = blister.msgstrs.find(self.looktv.Text())
									if ret >-1:
										#lista.Select(now)
										scrollmsg.AddInt32("where",now)
										be_app.WindowAt(0).PostMessage(scrollmsg)
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
										#ret = items.encode(self.encoding).lower().find(self.looktv.Text().lower())
										ret = items.lower().find(self.looktv.Text().lower())
										if ret >-1:
											#lista.Select(now)
											scrollmsg.AddInt32("where",now)
											be_app.WindowAt(0).PostMessage(scrollmsg)
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
									#ret = blister.msgstrs.encode(self.encoding).lower().find(self.looktv.Text().lower())
									ret = blister.msgstrs.lower().find(self.looktv.Text().lower())
									if ret >-1:
										#lista.Select(now)
										scrollmsg.AddInt32("where",now)
										be_app.WindowAt(0).PostMessage(scrollmsg)
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
							say = BAlert('not_found', 'No matches found on listed entries', 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
							self.alerts.append(say)
							say.Go()
			return

		elif msg.what == 7047:
			addfloat=msg.FindFloat('delta')
			self.pb.Update(addfloat,None,None)
			return
		elif msg.what == 10240:
			if self.ef>self.ei:
				listar=be_app.WindowAt(0).listemsgstr
				repmsg=BMessage(10241)
				repmsg.AddInt16("ei",self.ei)
				repmsg.AddInt16("ef",self.ef)
				repmsg.AddString("subs",self.reptv.Text())
				be_app.WindowAt(0).PostMessage(repmsg)
				#wt=listar[BApplication.be_app.WindowAt(0).transtabview.Selection()].trnsl#.Text()
				#wt.Delete(self.ei,self.ef)
		elif msg.what == 1010:
#			lftxt=
			self.looktv.SetText(msg.FindString('txt'))
			return
		return

class Findsource(BWindow):
	kWindowFrame = BRect(250, 150, 655, 226)
	kWindowName = "Find source"
	alerts=[]
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l=bounds.left
		t=bounds.top
		r=bounds.right
		b=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		#h=round(self.underframe.GetFontHeight()[0])
		be_plain_font.SetSize(14)
		h=be_plain_font.Size()
		kButtonFrame1 = BRect(r/2+15,b-40,r-5,b-5)
		kButtonName1 = "Search"
		self.SearchButton = BButton(kButtonFrame1, kButtonName1, kButtonName1, BMessage(5348))
		self.underframe.AddChild(self.SearchButton,None)
		self.casesens = BCheckBox(BRect(5,b-30,r/2-15,b-5),'casesens', 'Case sensistive', BMessage(222))
		self.casesens.SetValue(1)
		self.underframe.AddChild(self.casesens,None)
		self.looktv=BTextControl(BRect(5,5,r-5,32),'txttosearch','Search:','',BMessage(8046))
		self.looktv.SetDivider(60.0)
		self.underframe.AddChild(self.looktv,None)
		self.looktv.MakeFocus()
		self.encoding=be_app.WindowAt(0).encoding
		#self.encoding = BApplication.be_app.WindowAt(0).encoding


	def MessageReceived(self, msg):
		if msg.what == 5348:
			if self.looktv.Text() != "":
				lista=be_app.WindowAt(0).sourcestrings.lv
				total=lista.CountItems()
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
				#tl = len(self.looktv.Text())
				tl = byte_count(self.looktv.Text())[0]
				max = total
				now = indaco
				partial = False
				partiali = False
				loopa =True
				scrollmsg=BMessage(1712)
				while loopa:
					now+=1
					if now < total:
						if self.casesens.Value():
							item = lista.ItemAt(now)
							if item.hasplural:
								#ret = item.msgids[0].encode(self.encoding).find(self.looktv.Text())
								#ret = item.msgids[0].find(self.looktv.Text())
								ret=find_byte(self.looktv.Text(),item.msgids[0])
								if ret >-1:
									#evidenziare-correggere
									scrollmsg.AddInt32("where",now)
									be_app.WindowAt(0).PostMessage(scrollmsg)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									#messace.AddInt8('index',0)
									be_app.WindowAt(0).PostMessage(messace)
									break
								#ret = item.msgids[1].encode(self.encoding).find(self.looktv.Text())
								#ret = item.msgids[1].find(self.looktv.Text())
								ret=find_byte(self.looktv.Text(),item.msgids[1])
								if ret >-1:
									scrollmsg.AddInt32("where",now)
									be_app.WindowAt(0).PostMessage(scrollmsg)
									messace=BMessage(963741)
									messace.AddInt8('plural',1)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									#messace.AddInt8('index',1)
									be_app.WindowAt(0).PostMessage(messace)
									break
							else:
								#ret = item.msgids.encode(self.encoding).find(self.looktv.Text())
								#ret = item.msgids.find(self.looktv.Text())
								ret=find_byte(self.looktv.Text(),item.msgids)
								if ret >-1:
									scrollmsg.AddInt32("where",now)
									be_app.WindowAt(0).PostMessage(scrollmsg)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									#messace.AddInt8('index',0)
									be_app.WindowAt(0).PostMessage(messace)
									break
					
						else:
							item = lista.ItemAt(now)
							if item.hasplural:
								#ret = item.msgids[0].encode(self.encoding).lower().find(self.looktv.Text().lower())
								#ret = item.msgids[0].lower().find(self.looktv.Text().lower())
								ret=find_byte(self.looktv.Text().lower(),item.msgids[0].lower())
								if ret >-1:
									scrollmsg.AddInt32("where",now)
									be_app.WindowAt(0).PostMessage(scrollmsg)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									be_app.WindowAt(0).PostMessage(messace)
									break
								#ret = item.msgids[1].encode(self.encoding).lower().find(self.looktv.Text().lower())
								#ret = item.msgids[1].lower().find(self.looktv.Text().lower())
								ret=find_byte(self.looktv.Text().lower(),item.msgids[1].lower())
								if ret >-1:
									scrollmsg.AddInt32("where",now)
									be_app.WindowAt(0).PostMessage(scrollmsg)
									messace=BMessage(963741)
									messace.AddInt8('plural',1)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									be_app.WindowAt(0).PostMessage(messace)
									break
							else:
								#ret = item.msgids.encode(self.encoding).lower().find(self.looktv.Text().lower())
								#ret = item.msgids.lower().find(self.looktv.Text().lower())
								ret=find_byte(self.looktv.Text().lower(),item.msgids.lower())
								if ret >-1:
									scrollmsg.AddInt32("where",now)
									be_app.WindowAt(0).PostMessage(scrollmsg)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									be_app.WindowAt(0).PostMessage(messace)
									break
					if now == total:
						now = -1
						total = indaco+1
						partial = True
					if now == indaco:
						partiali = True
					if partial and partiali:
						loopa=False
						say = BAlert('not_found', 'No matches found on other entries', 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
						self.alerts.append(say)
						say.Go()

class POmetadata(BWindow):
	kWindowFrame = BRect(150, 150, 585, 480)
	kWindowName = "POSettings"
	
	def __init__(self,pofile,ordereddata):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		self.listBTextControl=[]
		self.pofile = pofile
		self.metadata = ordereddata
		self.LoadMe()
		
	def LoadMe(self):
		conta=self.underframe.CountChildren()
		while conta > 0:
			self.underframe.ChildAt(conta).RemoveSelf()
			conta=conta-1
		
		rect = [10,10,425,30]
		step = 34
		
		indexstring=0
		be_plain_font.SetSize(12)
		for item in self.metadata:
			modmsg=BMessage(51973)
			modmsg.AddString('itemstring',item[0])
			modmsg.AddInt8('itemindex',indexstring)
			tc=BTextControl(BRect(rect[0],rect[1]+step*indexstring,rect[2],rect[3]+step*indexstring),'txtctrl'+str(indexstring),item[0],item[1],modmsg)
			fon=BFont()
			self.underframe.GetFont(fon)
			fon.SetSize(14)
			tc.SetFont(fon)
			
			self.listBTextControl.append(tc)
			indexstring+=1

		if self.kWindowFrame.Height()< rect[3]+step*(indexstring):
			self.ResizeTo(self.Bounds().right,float(rect[3]+step*(indexstring)-20))
			
		for element in self.listBTextControl:
			self.underframe.AddChild(element,None)
	def MessageReceived(self, msg):
		#if msg.what == 99111: # elaborate pofile
		#	conta=self.underframe.CountChildren()
		#	while conta > 0:
		#		self.underframe.ChildAt(conta).RemoveSelf()
		#		conta=conta-1
#
#			self.metadata = self.pofile.ordered_metadata()
#			
#			rect = [10,10,425,30]
#			step = 34
#			
#			indexstring=0
#			for item in self.metadata:
#				modmsg=BMessage(51973)
#				modmsg.AddString('itemstring',item[0])
#				modmsg.AddInt8('itemindex',indexstring)
#				self.listBTextControl.append(BTextControl(BRect(rect[0],rect[1]+step*indexstring,rect[2],rect[3]+step*indexstring),'txtctrl'+str(indexstring),item[0],item[1],modmsg))
#				indexstring+=1

#			if self.kWindowFrame.Height()< rect[3]+step*(indexstring):
#				self.ResizeTo(self.Bounds().right,float(rect[3]+step*(indexstring)-20))
				
#			for element in self.listBTextControl:
#				self.underframe.AddChild(element,None)

		if msg.what == 51973:
			# save metadata to self.pofile
			ind=msg.FindString('itemstring')
			indi=msg.FindInt8('itemindex')
			self.pofile.metadata[ind]=self.listBTextControl[indi].Text()#.decode(BApplication.be_app.WindowAt(0).encoding)   ################### possible error? check encoding
			# save self.pofile to backup file
			smesg=BMessage(16893)
			smesg.AddInt8('savetype',2)
			#smesg.AddInt8('indexroot',self.indexroot)
			pth=be_app.WindowAt(0).backupfile
			smesg.AddString('bckppath',be_app.WindowAt(0).backupfile)
			be_app.WindowAt(0).PostMessage(smesg)


			#entry = self.pofile.metadata_as_entry()
#		self.po.metadata = {
 #           'Project-Id-Version': "%s %s" % (release.description, release.version),
  #          'Report-Msgid-Bugs-To': '',
   #         'POT-Creation-Date': now,
    #        'PO-Revision-Date': now,
     #       'Last-Translator': '',
      #      'Language-Team': '',
       #     'MIME-Version': '1.0',
        #    'Content-Type': 'text/plain; charset=UTF-8',
         #   'Content-Transfer-Encoding': '',
          #  'Plural-Forms': '',
        #} 
        

#			poobj.metadata["Content-Type"] = "text/plain; charset=UTF-8"

class MyListItem(BListItem):
	nocolor = (0, 0, 0, 0)
	frame=[0,0,0,0]

	def __init__(self, txt):
		self.text = txt
		BListItem.__init__(self)
	
	def DrawItem(self, owner, frame,complete):
		self.frame = frame
		l=frame.left
		b=frame.bottom
		#complete = True
		if self.IsSelected() or complete: # 
			#color = (200,200,200,255)
			owner.SetHighColor(200,200,200,255)
			owner.SetLowColor(200,200,200,255)
			owner.FillRect(frame)
		self.color = rgb_color()#self.nocolor
		owner.SetHighColor(self.color)
		owner.MovePenTo(l,b-2)
		owner.DrawString(self.text,None)
		owner.SetLowColor(255,255,255,255)

	def Text(self):
		return self.text

class SugjItem(BListItem):
	nocolor = (0, 0, 0, 0)
	frame=[0,0,0,0]
	def __init__(self,sugj,lev):
		self.text=sugj
		tl=len(sugj)
		self.percent=int(round((100*(tl-lev))/tl))
		BListItem.__init__(self)

	def DrawItem(self, owner, frame,complete):
		self.frame = frame
		l=frame.left
		font_height_value=font_height()
		be_plain_font.GetHeight(font_height_value)
		#t=frame.top
		#r=frame.right
		b=frame.bottom
		if self.IsSelected() or complete:
			owner.SetHighColor(200,200,200,255)
			owner.SetLowColor(200,200,200,255)
			owner.FillRect(frame)
		self.color = rgb_color()
		owner.MovePenTo(l+5,b-font_height_value.descent)#2)
		tempcolor = rgb_color()
		if self.percent == 100:
			self.font = be_bold_font
			self.font.SetSize(be_plain_font.Size())#16)
			tempcolor.green=200
			#(0,200,0,0)
		else:
			self.font = be_plain_font
			#self.font.SetSize(16)
			tempcolor.red = 170
			tempcolor.green = 20
			tempcolor.blue = 170
		owner.SetHighColor(tempcolor)
		owner.SetFont(self.font)
		xtxt=str(self.percent)+"%"
		owner.DrawString(xtxt,None)
		ww=self.font.StringWidth(xtxt)
		owner.SetHighColor(self.color)
		self.font = be_plain_font
		owner.SetFont(self.font)
		owner.MovePenTo(l+ww+10,b-2)#40
		owner.DrawString(self.text,None)

	def Text(self):
		return self.text

class ErrorItem(BListItem):
	nocolor = (0, 0, 0, 0)
	frame=[0,0,0,0]
	def __init__(self,sugj):
		self.text=sugj
		BListItem.__init__(self)

	def DrawItem(self, owner, frame,complete):
		self.frame = frame
		l=frame.left
		b=frame.bottom
		if self.IsSelected() or complete: # 
			color = (200,200,200,255)
			owner.SetHighColor(200,200,200,255)
			owner.SetLowColor(200,200,200,255)
			owner.FillRect(frame)
		self.color = rgb_color()#self.nocolor
		owner.MovePenTo(l+5,b-2)
		self.font = be_plain_font
		#tempcolor = (20,20,20,0)
		owner.SetHighColor(20,20,20,0)
		owner.SetFont(self.font)
		owner.DrawString(self.text,None)

class GeneralSettings(BWindow):
	kWindowFrame = BRect(250, 150, 755, 297)
	kWindowName = "General Settings"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l=bounds.left
		t=bounds.top
		r=bounds.right
		b=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		self.langcheck = BCheckBox(BRect(5,79,r-15,104),'langcheck', 'Check language compliance between pofile and user', BMessage(242))
		self.mimecheck = BCheckBox(BRect(5,109,r-15,134),'mimecheck', 'Check mimetype of file', BMessage(262))
		self.underframe.AddChild(self.langcheck,None)
		self.underframe.AddChild(self.mimecheck,None)
		ent,confile=Ent_config()
		Config.read(confile)
		try:
			#langcheck
			checklang = Config.getboolean('General','checklang')
			if checklang:
				self.langcheck.SetValue(1)
			else:
				self.langcheck.SetValue(0)
		except:
			# "eccezione creo checklang in config.ini"
			cfgfile = open(confile,'w')
			Config.set('General','checklang', "True")
			Config.write(cfgfile)
			self.langcheck.SetValue(1)
			cfgfile.close()
		try:
			mimecheck = Config.getboolean('General','mimecheck')
			if mimecheck:
				self.mimecheck.SetValue(1)
			else:
				self.mimecheck.SetValue(0)
		except:
			#"eccezione creo mimecheck in config.ini"
			cfgfile = open(confile,'w')
			Config.set('General','mimecheck', "True")
			Config.write(cfgfile)
			self.mimecheck.SetValue(1)
			cfgfile.close()

	def MessageReceived(self, msg):
		if msg.what == 242:
			ent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				if self.langcheck.Value():
					Config.set('General','checklang', "True")
					Config.write(cfgfile)
				else:
					Config.set('General','checklang', "False")
					Config.write(cfgfile)
			except:
				print("Error enabling language compliance check, missing config section?")
			cfgfile.close()
		elif msg.what == 262:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.mimecheck.Value():
					Config.set('General','mimecheck', "True")
					Config.write(cfgfile)
				else:
					Config.set('General','mimecheck', "False")
					Config.write(cfgfile)
			except:
				print("Error enabling mimechecking, missing config section?")
			cfgfile.close()

class TMSettings(BWindow):
	kWindowFrame = BRect(250, 150, 755, 240)
	kWindowName = "Translation Memory Settings"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l=bounds.left
		t=bounds.top
		r=bounds.right
		b=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		#h=round(self.underframe.GetFontHeight()[0])
		be_plain_font.SetSize(16)
		h=be_plain_font.Size()
		self.AddChild(self.underframe,None)
		self.enablecheck = BCheckBox(BRect(5,5,r-5,h+6),'enabcheck', 'Enable/Disable translation memory', BMessage(222))
		if tm:
			self.enablecheck.SetValue(1)
		else:
			self.enablecheck.SetValue(0)
		ent,confile=Ent_config()
		Config.read(confile)
		try:
			bret = ConfigSectionMap("TMSettings")['tmxsrv']
		except (configparser.NoSectionError):
			cfgfile = open(confile,'w')
			Config.add_section('TMSettings')
			Config.set('TMSettings','tmxsrv',"127.0.0.1")
			Config.write(cfgfile)
			cfgfile.close()
			bret = "127.0.0.1"
		except (configparser.NoOptionError):
			cfgfile = open(confile,'w')
			Config.set('TMSettings','tmxsrv',"127.0.0.1")
			Config.write(cfgfile)
			cfgfile.close()
			bret = "127.0.0.1"
		self.tmxsrvBTC = BTextControl(BRect(5,h+15,r-5,2*h+25),'tmxsrv','Server address:',bret,BMessage(8080))
		try:
			bret = ConfigSectionMap("TMSettings")['tmxprt']
		except:
			cfgfile = open(confile,'w')
			Config.set('TMSettings','tmxprt',"2022")
			Config.write(cfgfile)
			cfgfile.close()
			bret = "2022"
		self.tmxprtBTC = BTextControl(BRect(5,2*h+26,r-5,3*h+37),'tmxprt','Server port:',bret,BMessage(8086))
		self.underframe.ResizeTo(r,3*h+42)
		self.ResizeTo(r,3*h+42)
		self.underframe.AddChild(self.enablecheck,None)
		self.underframe.AddChild(self.tmxsrvBTC,None)
		self.underframe.AddChild(self.tmxprtBTC,None)

	def MessageReceived(self, msg):
		if msg.what == 222:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.enablecheck.Value():
					Config.set('General','tm', "True")
					Config.write(cfgfile)
					tm=True
				else:
					Config.set('General','tm', "False")
					Config.write(cfgfile)
					tm=False
			except:
				print("Error writing tm setting in config.ini, missing config section?")
			cfgfile.close()
		elif msg.what == 8080:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				Config.set("TMSettings",'tmxsrv',self.tmxsrvBTC.Text())
				Config.write(cfgfile)
				tmxsrv=self.tmxsrvBTC.Text()
			except:
				print("Cannot save TM server address")
			cfgfile.close()
		elif msg.what == 8086:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				tmxprt=int(self.tmxprtBTC.Text())
				Config.set("TMSettings",'tmxprt',self.tmxprtBTC.Text())
				Config.write(cfgfile)
			except:
				print("Cannot save TM server port. Port value:",self.tmxprtBTC.Text())
			cfgfile.close()
		BWindow.MessageReceived(self, msg)

class SpellcheckSettings(BWindow):
	kWindowFrame = BRect(250, 150, 755, 297)
	kWindowName = "Spellchecking Settings"
	def __init__(self,showspell,oldsize):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l = bounds.left
		t = bounds.top
		r = bounds.right
		b = bounds.bottom
		be_plain_font.SetSize(oldsize)
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		h=oldsize
		#h=round(self.underframe.GetFontHeight()[0])
		self.AddChild(self.underframe,None)
		ent,confile=Ent_config()
		self.enablecheck = BCheckBox(BRect(5,5,r-5,h+4),'enabcheck', 'Enable/Disable spellcheck', BMessage(222))
		
		if ent.Exists():
			Config.read(confile)
			if showspell:
				self.enablecheck.SetValue(1)
			else:
				self.enablecheck.SetValue(0)
			try:
				bret = ConfigSectionMap("Translator")['spell_dictionary'] #it's ascii
			except:
				bret = "/boot/system/data/hunspell/en_US"
				
			self.diz = BTextControl(BRect(5,2*h+27,r-5,3*h+37),'dictionary','Dictionary path:',bret,BMessage(8086))
			try:
				bret = ConfigSectionMap("Translator")['spell_inclusion']
			except:
				bret = ""
			self.inclus = BTextControl(BRect(5,3*h+39,r-5,4*h+49),'inclusion','Chars included in words:',bret,BMessage(8087))
			try:
				bret = ConfigSectionMap("Translator")['spell_esclusion']
			except:
				bret = ""
		self.esclus = BTextControl(BRect(5,4*h+51,r-5,5*h+61),'inclusion','Chars-categories escluded in words:',bret,BMessage(8088))
		self.esclus.SetText("Pc,Pd,Pe,Pi,Po,Ps,Cc,Pf")
		self.ResizeTo(r,5*h+71)
		self.underframe.AddChild(self.enablecheck,None)
		self.underframe.AddChild(self.diz,None)
		self.underframe.AddChild(self.inclus,None)
		self.underframe.AddChild(self.esclus,None)
		#TODO integrare un rilevatore di categorie TextView a singolo carattere+StringView per indicare unicodedata.category
	def MessageReceived(self, msg):
		if msg.what == 222:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.enablecheck.Value():
					Config.set('General','spellchecking', "True")
					Config.write(cfgfile)
				else:
					Config.set('General','spellchecking', "False")
					Config.write(cfgfile)
			except:
				print("Error enabling spellcheck, missing config section?")
			cfgfile.close()
		elif msg.what == 8086:
			confent,confile=Ent_config()
			ent=BEntry(self.diz.Text()+".dic")
			if ent.Exists():
				Config.read(confile)
				cfgfile = open(confile,'w')
				try:
					Config.set("Translator",'spell_dictionary',self.diz.Text())
				except:
					print("Cannot save dictionary path")
				Config.write(cfgfile)
				cfgfile.close()
			else:
				print("wrong path")
		elif msg.what == 8087:
			confent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				Config.set("Translator",'spell_inclusion',self.inclus.Text())
				Config.write(cfgfile)
			except:
				print("Cannot save inclusion chars")
			cfgfile.close()
			Config.read(confile)
			inctxt=ConfigSectionMap("Translator")['spell_inclusion']
			inclusion = inctxt.split(",")
		elif msg.what == 8088:
			confent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				Config.set("Translator",'spell_esclusion',self.esclus.Text())
				Config.write(cfgfile)
			except:
				print("Cannot save esclusion chars")
			cfgfile.close()
			Config.read(confile)
			esctxt=ConfigSectionMap("Translator")['spell_esclusion']
			esclusion=esctxt.split(",")

class HeaderWindow(BWindow):
	kWindowFrame = BRect(150, 150, 500, 600)
	kWindowName = "Po header"
	def __init__(self,pofile,backupfile,oldsize):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		self.backupfile=backupfile
		ix=bounds.left
		iy=bounds.top
		fx=bounds.right
		fy=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		be_plain_font.SetSize(oldsize)
		self.headerview=BTextView(BRect(4,4,fx-4,fy-50),"headerview",BRect(4,4,fx-12,fy-48),B_FOLLOW_ALL_SIDES)
		self.underframe.AddChild(self.headerview,None)
		kButtonFrame = BRect(fx-150, fy-40, fx-10, fy-10)
		kButtonName = "Save header"
		self.savebtn = BButton(kButtonFrame, kButtonName, kButtonName, BMessage(5252))
		self.underframe.AddChild(self.savebtn,None)
		self.pofile=pofile
		if self.pofile.header!="":
			self.headerview.SetText(self.pofile.header,None)

	def Save(self):
		bckpmsg=BMessage(16893)
		bckpmsg.AddInt8('savetype',4)
		bckpmsg.AddString('header',self.headerview.Text())
		bckpmsg.AddString('bckppath',self.backupfile)
		BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)

	def MessageReceived(self, msg):
		if msg.what == 5252:
			self.Save()
			self.Quit()
		else:
			return BWindow.MessageReceived(self, msg)

class MainWindow(BWindow):
	alerts=[]
	sugjs=[]
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
		self.t1=time.time()
		self.bckgnd = BView(self.Bounds(), "bckgnd_View", 8, 20000000)
		rect=self.bckgnd.Bounds()
		self.AddChild(self.bckgnd,None)
		self.bckgnd.SetResizingMode(B_FOLLOW_ALL_SIDES)
		bckgnd_bounds=self.bckgnd.Bounds()
		self.drop = threading.Semaphore()
		self.sem = threading.Semaphore()
		self.event= threading.Event()
		self.keeperoftheloop = False
		self.modifier=False
		self.shortcut=False
		self.poview=[True,True,True,False]
		fon=BFont()
		self.oldsize=be_plain_font.Size()
		ent,confile=Ent_config()
		global tm,tmxsrv,tmxprt,tmsocket,showspell,comm,esclusion,inclusion
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
				tm = Config.getboolean('General','tm')
				if tm:
					#tmsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					try:
						tmxsrv=ConfigSectionMap("TMSettings")['tmxsrv']
					except:
						cfgfile = open(confile,'w')
						try:
							Config.add_section("TMSettings")
						except:
							pass
						Config.set("TMSettings",'tmxsrv', '127.0.0.1')
						tmxsrv = '127.0.0.1'
						Config.write(cfgfile)
						cfgfile.close()
					try:
						tmxprt=int(ConfigSectionMap("TMSettings")['tmxprt'])
					except:
						cfgfile = open(confile,'w')
						try:
							Config.add_section("TMSettings")
						except:
							pass
						Config.set("TMSettings",'tmxprt', "2022")
						tmxprt = 2022
						Config.write(cfgfile)
						cfgfile.close()
					try:
						builtin_srv=Config.getboolean('TMSettings','builtinsrv')
					except:
						cfgfile = open(confile,'w')
						try:
							Config.add_section("TMSettings")
						except:
							pass
						Config.set("TMSettings",'builtinsrv', "False")
						builtin_srv = False
						Config.write(cfgfile)
						cfgfile.close()
					try:
						header=int(ConfigSectionMap("TMSettings")['header'])
					except:
						cfgfile = open(confile,'w')
						try:
							Config.add_section("TMSettings")
						except:
							pass
						Config.set("TMSettings",'header', "4096")
						header = 4096
						Config.write(cfgfile)
						cfgfile.close()
					try:
						log_srv=Config.getboolean('TMSettings','logSrv')
					except:
						cfgfile = open(confile,'w')
						try:
							Config.add_section("TMSettings")
						except:
							pass
						Config.set("TMSettings",'logSrv', "False")
						log_srv = True
						Config.write(cfgfile)
						cfgfile.close()
					if builtin_srv:
						#server(self,addr,PORT=2022,HEADER=4096,log=False)
						self.serv=Thread(target=self.server,args=(tmxsrv,tmxprt,header,log_srv,))
						self.serv.start()
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
		else:
			#no file
			cfgfile = open(confile,'w')
			Config.add_section('General')
			Config.set('General','sort', "0")
			self.sort=0
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
		
		if setspellcheck:
			showspell=True
			try:
				global inclusion,esclusion
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
			ento=BEntry(spelldict+".dic")
			if ento.Exists():
				pth=BPath()
				ento.GetPath(pth)
				fuee=pth.Leaf()
				filename, file_extension = os.path.splitext(fuee)
				self.spellchecker = enchant.Dict(filename) # TODO check initialization (correctly loading dictionary)
		else:
			showspell=False
		
		
		self.steps=['˹','   ˺','   ˼','˻']
		self.indsteps=0
		self.ofp=BFilePanel(B_OPEN_PANEL,None,None,node_flavor.B_ANY_NODE,True, None, None, True, True)
		osdir="/boot/home"
		self.ofp.SetPanelDirectory(osdir)
		self.bar = BMenuBar(bckgnd_bounds, 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		self.viewarr = []		
		for menu, items in self.Menus:
			if menu == "View":
				savemenu=True
			else:
				savemenu=False
			menu = BMenu(menu)
			for k, name in items:
				if k is None:
						menu.AddItem(BSeparatorItem())
				else:
						menuitem=BMenuItem(name, BMessage(k), name[1],0)
						#in base a Settings
						if name == "Fuzzy":
							menuitem.SetMarked(self.poview[0])
						elif name == "Untranslated":
							menuitem.SetMarked(self.poview[1])
						elif name == "Translated":
							menuitem.SetMarked(self.poview[2])
						elif name == "Obsolete":
							menuitem.SetMarked(self.poview[3])
						self.viewarr.append(menuitem)
						menu.AddItem(menuitem)
			if savemenu:
				self.savemenu = menu
				self.bar.AddItem(self.savemenu)
			else:
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
		
		self.tmscrollsugj=ScrollSugj(BRect(self.upperbox.Bounds().right*2/3+4,4,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom/2), 'ScrollSugj')
		
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
			l=self.font.StringWidth("  ˺")
			rectspellab=BRect(self.upperbox.Bounds().right*2/3+4,self.upperbox.Bounds().bottom-80,self.upperbox.Bounds().right*2/3+l+10,self.upperbox.Bounds().bottom-4)
			self.spellabel= BStringView(rectspellab,"spellabel","Spellcheck status:",B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM)
			self.spellabel.SetFont(self.font)
			self.upperbox.AddChild(self.spellabel,None)
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
		
		######## expander for sugj #########
		rectcksp=BRect(self.upperbox.Bounds().right*2/3+4,self.upperbox.Bounds().bottom/2+10,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom-70)
		insetcksp=BRect(0,0,rectcksp.Width(),rectcksp.Height())
		insetcksp.InsetBy(5,5)
		self.expander = srcTextView(rectcksp,"checkres",insetcksp,B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM,B_WILL_DRAW|B_FRAME_EVENTS)#BTextView(rectcksp,"checkres",insetcksp,B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM,B_WILL_DRAW|B_FRAME_EVENTS)
		self.expander.MakeEditable(0)
		self.upperbox.AddChild(self.expander,None)
		
		# check user accepted languages
		#
		self.overbox=CreateUserBox(self.bckgnd.Frame())
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
		#be_plain_font.SetSize(8)
		self.msgstabview = BTabView(BRect(5.0, 60.0, self.infobox.Bounds().right-5.0, self.infobox.Bounds().bottom-fon.Size()-15.0), 'msgs_tabview',button_width.B_WIDTH_FROM_LABEL,B_FOLLOW_LEFT_RIGHT)
		#be_plain_font.SetSize(self.oldsize)
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
		
		self.msgstabview.SetTabSide(tab_side.kBottomSide)
		self.infobox.AddChild(self.msgstabview,None)
		self.msgstabview.Select(2)
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
			self.sugjs=[]
			self.expander.SelectAll()
			self.expander.Clear()
			
	def FrameResized(self,x,y):	
		resiz=False
		if x<1022:
			x=1022
			resiz=True
		if y<704:
			y=704
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
		self.tmscrollsugj.sv.ResizeTo(self.tmscrollsugj.sv.Bounds().right,self.upperbox.Bounds().Height()/2)
		sbh=self.tmscrollsugj.sv.ScrollBar(orientation.B_HORIZONTAL).Frame().Height()
		self.tmscrollsugj.lv.ResizeTo(self.tmscrollsugj.lv.Bounds().right,self.upperbox.Bounds().Height()/2-sbh)
		self.expander.MoveTo(self.upperbox.Bounds().right-4-self.expander.Bounds().Width(),4+self.tmscrollsugj.sv.Bounds().Height()+10)
		self.expander.ResizeTo(self.expander.Bounds().right,self.upperbox.Bounds().Height()/2-80)
		
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
		
		ent,confile=Ent_config()
		Config.read(confile)
		try:
			mimecheck = Config.getboolean('General','mimecheck')
		except:
			cfgfile = open(confile,'w')
			Config.set('General','mimecheck', "True")
			Config.write(cfgfile)
			mimecheck=True
			cfgfile.close()
		if mimecheck:
			static = BMimeType()
			mime = BMimeType.GuessMimeType(f,static)
			mimetype = repr(static.Type()).replace('\'','')
			boolgo=False
			try:
				supertype,subtype = mimetype.split('/')
				if supertype=="text" and subtype=="x-gettext-translation":
					boolgo=True
				else:
					say = BAlert('Warn', 'This is a workaround, the file\'s mimetype is not a x-gettext-translation. Do you want to open the file despite this?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
					self.alerts.append(say)
					ret=say.Go()
					if ret==0:
						# mimetype not detected, check file extnsion
						boolgo=False
						if not(file_extension in [".po", ".pot", ".mo"]):
							return
						else:
							boolgo=True
					else:
						return
			except:
				say = BAlert('Warn', 'This is a workaround, cannot detect correctly the file\'s mimetype. Do you want to open the file despite this?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				ret=say.Go()
				if ret==0:
					# mimetype not detected, check file extnsion
					boolgo=False
					supertype = "text"
					subtype = "x-gettext-translation"
					if not(file_extension in [".po", ".pot", ".mo"]):
						return
					else:
						boolgo=True
				else:
					return
		else:
			if file_extension in [".po", ".pot", ".mo"]:
				boolgo=True
			else:
				return
		if boolgo:
			# file correctly detected ... so open...
			# check user accepted languages
			fileenc = polib.detect_encoding(f)
			self.pof = polib.pofile(f,encoding=fileenc)
			ordmdata=self.pof.ordered_metadata()
			a,b = checklang(ordmdata)
			#overwrite "a", controllo config.ini per info Traduttore
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
						self.loadPO(f,self.pof)
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt))
					item.SetLineNum(entry.linenum)
				self.litms.append(item)
				self.sourcestrings.lv.AddItem(self.litms[-1])
				
		self.progressinfo=BStatusBar(BRect(5,5,self.infobox.Bounds().right-5,35),'progress',"Progress:", None)#label,trailing_label
		self.potot=len(self.pofile.translated_entries())+len(self.pofile.untranslated_entries())+len(self.pofile.fuzzy_entries())
		self.progressinfo.SetMaxValue(self.potot)
		self.progressinfo.Update(len(self.pofile.translated_entries()),None,str(self.pofile.percent_translated())+"%")
		self.infobox.AddChild(self.progressinfo,None)
	
	def Save(self, path):
		self.pofile.save(path)
		svdlns=[]  #moved to fix reference before assignment
		if path[-7:] != "temp.po":
			#TODO rileva architettura -> msgfmt-x86 o msgfmt
			execpath = find_executable("msgfmt")
			comtwo = execpath+" -c "+path
			checker = Popen( comtwo.split(' '), stdout=PIPE,stderr=PIPE)
			jessude,err= checker.communicate()
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
		try:
		#if True:
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
			elif src==None:
				#close the server
				tmsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				tmsocket.connect((tmxsrv,tmxprt))
				tmsocket.send(b'')
				tmsocket.close()
			else:
				#we are requesting either to add or remove a translation
				txt0=src[0]
				tmsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				tmsocket.connect((tmxsrv,tmxprt))
				pck=[]
				txt1=src[1]
				if txt0==None:
					#add to tm dictionary
					txt2=src[2]
					st2=txt2
					st2.replace('<','&lt;')
					st2.replace('>','&gt;')
					st1=txt1
					st1.replace('<','&lt;')
					st1.replace('>','&gt;')
					pck.append((txt0,st1,st2))
				else:
					#remove from tm dictionary
					txt2=src[2]
					txt2.replace('<','&lt;')
					txt2.replace('>','&gt;')
					st1=txt1
					st1.replace('<','&lt;')
					st1.replace('>','&gt;')
					pck.append((txt0,st1,txt2))
				send_pck=pickle.dumps(pck)
				tmsocket.send(send_pck)
				tmsocket.close()
		except:
			hidemsg=BMessage(104501)
			be_app.WindowAt(0).PostMessage(hidemsg)
		self.netlock.release()
	
	def MessageReceived(self, msg):
		if msg.what == B_MODIFIERS_CHANGED:
			value=msg.FindInt32("modifiers")
			self.sem.acquire()
			if value==self.modifiervalue or value==self.modifiervalue+8 or value ==self.modifiervalue+32 or value ==self.modifiervalue+40:
				#"modificatore"
				self.modifier=True
				self.shortcut = False
			elif value == self.modifiervalue+4357 or value==self.modifiervalue+265 or value==self.modifiervalue+289 or value == self.modifiervalue+297:
				#"scorciatoia"
				self.shortcut = True
				self.modifier = False
			else:
				#"altro"
				self.modifier=False
				self.shortcut=False
			self.sem.release()
			return
		elif msg.what == B_KEY_DOWN:	#on tab key pressed, focus on translation or translation of first item list of translations
			key=msg.FindInt32('key')
			if key==38: #tab key
				if self.sourcestrings.lv.CurrentSelection()>-1:
					self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus() ########### LOOK HERE 
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
			return
		elif msg.what == 2:
			#Save from menu
			if True:     ###### FIX HERE check condition if file is loaded
				if self.listemsgstr[self.transtabview.Selection()].trnsl.tosave:
					#print("eventtextvie è cambiato, si esegue save interno")
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
				if tabs == 0:   #->      if not thisBlistitem.hasplural:                         <-------------------------- or this?
					thisBlistitem.txttosave=thisBlistitem.text
					thisBlistitem.msgstrs=thisBlistitem.txttosave
					bckpmsg.AddString('translation',thisBlistitem.txttosave)
				else:
					thisBlistitem.txttosavepl=[]
					thisBlistitem.txttosave=self.listemsgid[0].src.Text()
					thisBlistitem.msgstrs=[]
					thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
					bckpmsg.AddString('translation',thisBlistitem.txttosave)
					cox=1
					while cox < tabs+1:
						thisBlistitem.msgstrs.append(self.listemsgid[1].src.Text())
						thisBlistitem.txttosavepl.append(self.listemsgid[1].src.Text())
						bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())
						cox+=1
				bckpmsg.AddString('bckppath',self.backupfile)
				be_app.WindowAt(0).PostMessage(bckpmsg)

				kmesg=BMessage(130550)
				kmesg.AddInt8('movekind',0)
				be_app.WindowAt(0).PostMessage(kmesg)
			return
		elif msg.what == 5:
			if self.sourcestrings.lv.CountItems()>0:
				self.fp.Show()
		elif msg.what == 735157:
			color=rgb_color()
			color.green=150
			self.font.SetSize(28)
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,color)
			self.checkres.SetText("☑",None)
		elif msg.what == 982757:
			color=rgb_color()
			color.red=150
			self.font.SetSize(28)
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,color)
			self.checkres.SetText("☒",None)
		elif msg.what == 431110173:
			#delete a suggestion on remote tmserver
			txtdel=msg.FindString("sugj")
			srcdel=self.listemsgid[self.srctabview.Selection()].src.Text()
			cmd=("d","e","l")
			mx=[cmd,srcdel,txtdel]
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
				thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
				thisBlistitem.tosave=True
				tabs=len(self.listemsgstr)-1
				bckpmsg=BMessage(16893)
				bckpmsg.AddInt8('savetype',1)
				bckpmsg.AddInt32('tvindex',self.sourcestrings.lv.CurrentSelection())
				bckpmsg.AddInt8('plurals',tabs)
				if tabs == 0:   #-> if not thisBlistitem.hasplural:  <-- or this?
					thisBlistitem.txttosave=thisBlistitem.text#.decode(self.cod)#(self.encoding)
					thisBlistitem.msgstrs=thisBlistitem.txttosave
					bckpmsg.AddString('translation',thisBlistitem.txttosave)
				else:
					thisBlistitem.txttosavepl=[]
					thisBlistitem.txttosave=self.listemsgid[0].src.Text()
					thisBlistitem.msgstrs=[]
					thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
					bckpmsg.AddString('translation',thisBlistitem.txttosave)
					cox=1
					while cox < tabs+1:
						thisBlistitem.msgstrs.append(self.listemsgid[1].src.Text())
						thisBlistitem.txttosavepl.append(self.listemsgid[1].src.Text())
						bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())
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
					if self.listemsgstr[self.transtabview.Selection()].trnsl.CheckSpell():
						be_app.WindowAt(0).PostMessage(735157)
					else:
						be_app.WindowAt(0).PostMessage(982757)
				#except:
				#	pass
				self.Looper().Unlock()
			return
		elif msg.what == 6:
			# Find source
			if self.sourcestrings.lv.CountItems()>0:
				self.Findsrc = Findsource()
				self.Findsrc.Show()
			return
		elif msg.what == 7:
			# Find/Replace translation
			if self.sourcestrings.lv.CountItems()>0:
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
			self.bckgnd.Hide()
			self.overbox.Show()
			self.overbox.BtnCancel.Hide()
			pass #TODO
		elif msg.what == 53:#32:
			#Double clic = translator comment
			if self.sourcestrings.lv.CountItems()>0:
				listsel=self.sourcestrings.lv.CurrentSelection()
				if listsel>-1:
					thisBlistitem=self.sourcestrings.lv.ItemAt(listsel)
					self.tcommentdialog=TranslatorComment(listsel,thisBlistitem,self.backupfile)
					self.tcommentdialog.Show()
			return
		elif msg.what == 42:
			# PO metadata
			if self.sourcestrings.lv.CountItems()>0:
				self.POMetadata = POmetadata(self.pofile,self.orderedmetadata)
				self.POMetadata.Show()
			return
		elif msg.what == 43:
			#Po header
			if self.sourcestrings.lv.CountItems()>0:
				self.HeaderWindow = HeaderWindow(self.pofile,self.backupfile,self.oldsize)
				self.HeaderWindow.Show()
			return
		elif msg.what == 44:
			#spelcheck settings
			self.splchset = SpellcheckSettings(showspell,self.oldsize)
			self.splchset.Show()
		elif msg.what == 45:
			#Translation Memory settings
			self.tmset = TMSettings()
			self.tmset.Show()
		elif msg.what == 66:
			self.speloc.acquire()
			tbef = self.intime
			self.speloc.release()
			mux=BMessage(7484)
			mux.AddString('graph',str(self.steps[self.indsteps]))
			be_app.WindowAt(0).PostMessage(mux)
			self.speloc.acquire()
			taft = self.intime
			self.speloc.release()
			if tbef == taft:
				if taft > self.t1:
					if len(self.listemsgstr)>0:
						traduzion=self.listemsgstr[self.transtabview.Selection()].trnsl.Text()
						if traduzion != "":
							be_app.WindowAt(0).PostMessage(12343)# TODO EVALUATE: usare 333111 sempre in modo da richiamare questo?
				self.t1 = time.time()
			self.indsteps+=1
			if self.indsteps == len(self.steps):
				self.indsteps=0
			return
		elif msg.what == 70:
			# Done and next
			if self.sourcestrings.lv.CountItems()>0:
				if self.sourcestrings.lv.CurrentSelection()>-1:
					lung=len(self.listemsgstr)
					pick=0
					gonogo=False
					while pick<lung:
						thistranslEdit=self.listemsgstr[pick].trnsl
						if thistranslEdit.tosave:
							gonogo=True
						pick+=1
					thistranslEdit=self.listemsgstr[self.transtabview.Selection()].trnsl
					if gonogo:
						
						thisBlistitem=self.sourcestrings.lv.ItemAt(cursel.list.lv.CurrentSelection())
						thisBlistitem.tosave=True
						tabs=len(self.listemsgstr)-1
						bckpmsg=BMessage(16893)
						bckpmsg.AddInt8('savetype',1)
						bckpmsg.AddInt32('tvindex',self.sourcestrings.lv.CurrentSelection())
						bckpmsg.AddInt8('plurals',tabs)
						if tabs == 0:#->if not thisBlistitem.hasplural:<- or this?
							thisBlistitem.txttosave=thistranslEdit.Text()
							bckpmsg.AddString('translation',thisBlistitem.txttosave)
						else:
							thisBlistitem.txttosavepl=[]
							thisBlistitem.txttosave=self.listemsgstr[0].trnsl.Text()
							bckpmsg.AddString('translation',thisBlistitem.txttosave)
							cox=1
							while cox < tabs+1:
								thisBlistitem.txttosavepl.append(self.listemsgstr[1].trnsl.Text())
								bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgstr[cox].trnsl.Text())
								cox+=1
						bckpmsg.AddString('bckppath',self.backupfile)
						be_app.WindowAt(0).PostMessage(bckpmsg)
					kmesg=BMessage(130550)
					kmesg.AddInt8('movekind',4)
					be_app.WindowAt(0).PostMessage(kmesg)
			return
		elif msg.what == 72:
			# previous without saving
			if self.sourcestrings.lv.CountItems()>0:
				if self.sourcestrings.lv.CurrentSelection()>-1:
					thistranslEdit=self.listemsgstr[self.transtabview.Selection()].trnsl
					if thistranslEdit.tosave:
						thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
						thisBlistitem.tosave=False
						thisBlistitem.txttosave=""
					kmesg=BMessage(130550)
					kmesg.AddInt8('movekind',1)
					be_app.WindowAt(0).PostMessage(kmesg)
		elif msg.what == 73:
			# next without saving
			if self.sourcestrings.lv.CountItems()>0:
				if self.sourcestrings.lv.CurrentSelection()>-1:
					thistranslEdit=self.listemsgstr[self.transtabview.Selection()].trnsl
					if thistranslEdit.tosave:
						thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
						thisBlistitem.tosave=False
						thisBlistitem.txttosave=""
					kmesg=BMessage(130550)
					kmesg.AddInt8('movekind',0)
					be_app.WindowAt(0).PostMessage(kmesg)
		elif msg.what == 16893:
			try:
				Config.read(confile)
				defname=ConfigSectionMap("Translator")['name']
			except:
				defname=self.pofile.metadata['Last-Translator']
			now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
			# save to backup and update the blistitem
			bckppath = msg.FindString('bckppath')
			savetype = msg.FindInt8('savetype')
			if savetype == 0: #simple save, used for fuzzy state and metadata change
				self.writter.acquire()
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#self.pofile.save(bckppath)
				return
			elif savetype == 2:
				#save of metadata #TODO: verificare se usato, visto che non abbiamo più multipli file po aperti
				indexroot=msg.FindInt8('indexroot')
				self.writter.acquire()
				self.pofile.metadata['Last-Translator']=defname # metadata saved from po settings
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#self.pofile.save(bckppath)
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


				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('translation')
				tabbi=msg.FindInt8('plurals')
				self.writter.acquire()
				entry = self.sourcestrings.lv.ItemAt(tvindex).entry
				if entry and entry.msgid_plural:
						y=0
						textsavepl=[]
						entry.msgstr_plural[0] = textsave
						while y < tabbi:
							varname='translationpl'+str(y)                            ########################### give me one more eye?
							intended=msg.FindString(varname)
							textsavepl.append(intended) #useless???
							y+=1
							entry.msgstr_plural[y]=intended
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						if entry.previous_msgid:
							entry.previous_msgid=None
						if entry.previous_msgid_plural:
							entry.previous_msgid_plural=None
						if entry.previous_msgctxt:
							entry.previous_msgctxt=None
				elif entry and not entry.msgid_plural:
						entry.msgstr = textsave
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
				#self.pofile.save(bckppath)
				self.sourcestrings.lv.ItemAt(tvindex).state=1
				self.sourcestrings.lv.ItemAt(tvindex).tosave=False
				self.sourcestrings.lv.ItemAt(tvindex).txttosave=""
				self.sourcestrings.lv.ItemAt(tvindex).txttosavepl=[]
				return
			elif savetype == 3:
				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('tcomment')
				self.writter.acquire()
				entry = self.sourcestrings.lv.ItemAt(tvindex).entry
				entry.tcomment=textsave
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#self.pofile.save(bckppath)
				self.sourcestrings.lv.DeselectAll()
				self.sourcestrings.lv.Select(tvindex)
				return
			elif savetype == 4:
				textsave=msg.FindString('header')
				self.writter.acquire()
				self.pofile.header=textsave
				self.pofile.metadata['Last-Translator']=defname
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#self.pofile.save(bckppath)
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
					self.listemsgid[0].src.SetText(item.msgids[0],None)
					self.listemsgid[1].src.SetText(item.msgids[1],None)
					ww=0
					while ww<beta:
						self.transtablabels.append(BTab(None))
						if ww == 0:
							self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs[0])
							self.transtabview.SetFocusTab(x,True)
							self.transtabview.Select(x)
							self.transtabview.Select(0)
						else:
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr['+str(ww)+']',altece2,self))
							self.listemsgstr[ww].trnsl.SetPOReadText(item.msgstrs[ww])
							self.transtabview.AddTab(self.listemsgstr[ww],self.transtablabels[ww])
						ww=ww+1
				else:
					self.Nichilize()
					self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece2,self))
					self.transtablabels.append(BTab(None))
					self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
#######################################################################
					self.listemsgid[0].src.SetText(item.msgids,None)
					self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs)
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
			be_app.WindowAt(0).PostMessage(12343)
			return
		elif msg.what == 7484:
			self.spellabel.SetText(msg.FindString('graph'))
			return
		elif msg.what == 7485:
			b=msg.FindBool("First_step")
			if b:
				self.sourcestrings.lv.DeselectAll()
			else:
				tv=msg.FindInt32("tvindex")
				self.sourcestrings.lv.Select(tv)
			return
		elif msg.what == 1712:
			where=msg.FindInt32("where")
			self.sourcestrings.lv.Select(where)
			self.sourcestrings.lv.ScrollToSelection()
		elif msg.what == 71:
			# mark unmark as fuzzy
			if self.sourcestrings.lv.CountItems()>0:
				if self.sourcestrings.lv.CurrentSelection()>-1:
					self.writter.acquire()
					self.workonthisentry = self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection()).entry
					if 'fuzzy' in self.workonthisentry.flags:
						self.workonthisentry.flags.remove('fuzzy')
						if self.workonthisentry.previous_msgid:
							self.workonthisentry.previous_msgid=None
						if self.workonthisentry.previous_msgid_plural:
							self.workonthisentry.previous_msgid_plural=None
						if self.workonthisentry.previous_msgctxt:
							self.workonthisentry.previous_msgctxt=None
						self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection()).state=1
					else:
						self.workonthisentry.flags.append('fuzzy')
						self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection()).state=2
					self.sourcestrings.sv.Hide()
					self.sourcestrings.sv.Show() #Updates the MsgStrItem
					self.writter.release()
					bckpmsg=BMessage(16893)
					bckpmsg.AddInt8('savetype',0)
					bckpmsg.AddString('bckppath',self.backupfile)
					be_app.WindowAt(0).PostMessage(bckpmsg)
			return
		elif msg.what == 74:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			out=say.Go()
			if out == 0:
				#save first
				be_app.WindowAt(0).PostMessage(2)
				self.setMark(0)
			return
		elif msg.what == 75:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			out=say.Go()
			if out == 0:
				#save first
				be_app.WindowAt(0).PostMessage(2)
				self.setMark(1)
			return
		elif msg.what == 76:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			out=say.Go()
			if out == 0:
				#save first
				be_app.WindowAt(0).PostMessage(2)
				self.setMark(2)
			return
		elif msg.what == 77:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			out=say.Go()
			if out == 0:
				#save first
				be_app.WindowAt(0).PostMessage(2)
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
		elif msg.what == 54173:
			#Save as 
			txt=entry_ref()
			self.fp.GetPanelDirectory(txt)
			perc=BPath()
			BEntry(txt,True).GetPath(perc)
			savepath=perc.Path()
			e = msg.FindString("name")
			completepath = savepath +"/"+ e
			self.pofile.save(completepath)
			self.name=e
			self.percors=completepath
			self.pofile= polib.pofile(completepath,encoding=self.encoding)#wrongo
			self.filen, self.file_ext = os.path.splitext(completepath)
			self.backupfile= self.filen+".temp"+self.file_ext
			return
		elif msg.what == 112118:
			#launch a delayed check
			oldtext=msg.FindString('oldtext')
			indexBlistitem=msg.FindInt32('indexBlistitem')
			tabs=len(self.listemsgstr)-1
			
			if indexBlistitem == self.sourcestrings.lv.CurrentSelection():
				if self.listemsgstr[self.transtabview.Selection()].trnsl.oldtext != self.listemsgstr[self.transtabview.Selection()].trnsl.Text():  ### o è meglio controllare nel caso di plurale tutti gli eventtextview?
					self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			self.speloc.acquire()
			self.intime=time.time()
			self.speloc.release()
			return
		elif msg.what == 130550: # change listview selection
			#"changing selection"
			movetype=msg.FindInt8('movekind')
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
				hitem=rectangular.Height()
				rectangular=self.sourcestrings.lv.Bounds()
				hwhole=rectangular.Height()
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
				hitem=rectangular.Height()
				rectangular=self.sourcestrings.lv.Bounds()
				hwhole=rectangular.Height()
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
		elif msg.what == 10241:
			ei=msg.FindInt16("ei")
			ef=msg.FindInt16("ef")
			test=msg.FindString("subs")
			self.listemsgstr[self.transtabview.Selection()].trnsl.Delete(ei,ef)
			self.listemsgstr[self.transtabview.Selection()].trnsl.Insert(ei,test,byte_count(test)[0],None)
			self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			be_app.WindowAt(0).PostMessage(12343)
			return
		elif msg.what == 9631:
			sugg=msg.FindString('sugg')
			sorig=msg.FindString('sorig')
			indi=msg.FindInt32('indi')
			indf=msg.FindInt32('indf')
			bct,bca=byte_count(sugg)
			self.listemsgstr[self.transtabview.Selection()].trnsl.Delete(indi,indf)
			self.listemsgstr[self.transtabview.Selection()].trnsl.Insert(indi,sugg,bct,None)
			self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			selmex=BMessage(888222)
			selmex.AddInt32('indi',indi+bct)
			selmex.AddInt32('indf',indi+bct)
			be_app.WindowAt(0).PostMessage(12343)#(333111)
			be_app.WindowAt(0).PostMessage(selmex)
			return
		elif msg.what == 333111:
			#set checktime for delayed checkspell
			self.speloc.acquire()
			self.intime=time.time()
			self.speloc.release()
			return
		elif msg.what == 888222:
			indi=msg.FindInt32('indi')
			indf=msg.FindInt32('indf')
			self.listemsgstr[self.transtabview.Selection()].trnsl.Select(indi,indf)
			self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToOffset(indf)
		elif msg.what == 738033:
			#look for translations
			if tm:
				self.NichilizeTM()
			Thread(target=self.tmcommunicate,args=(msg.FindString('s'),)).start()
			return
		elif msg.what == 140:
			if self.tmscrollsugj.lv.CurrentSelection()>-1:
				self.expander.SetText(self.tmscrollsugj.lv.ItemAt(self.tmscrollsugj.lv.CurrentSelection()).Text(),None)
		elif msg.what == 141:
			#paste sugg to trnsl EventTextView
			try:
				self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.tmscrollsugj.lv.ItemAt(self.tmscrollsugj.lv.CurrentSelection()).Text(),None)
				self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus()
				lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
				self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
				self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
				self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			except:
			#	#"Not a SugjItem, but an ErrorItem as not having .Text() function"
				pass
			return
		elif msg.what == 5391359:
			r=msg.FindInt16('totsugj')
			act=0
			while act<r:
				self.sugjs.append(SugjItem(msg.FindString('sugj_'+str(act)),msg.FindInt8('lev_'+str(act))))
				self.tmscrollsugj.lv.AddItem(self.sugjs[-1])
				act+=1
			#se tra gli elementi non c'è 100% ma il BListItem è segnato come tradotto, è il caso di inviarlo al file tmx
			if self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection()).state == 1:	
				if self.tmscrollsugj.lv.CountItems()>0:
					if self.tmscrollsugj.lv.ItemAt(0).percent < 100:
						#mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text().decode(self.encoding),self.listemsgstr[self.transtabview.Selection()].trnsl.Text()).decode(self.encoding))
						mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text(),self.listemsgstr[self.transtabview.Selection()].trnsl.Text())
						Thread(target=self.tmcommunicate,args=(mx,)).start()
						#thread.start_new_thread( self.tmcommunicate, (mx,) )
						#print "beh, questo è corretto ma ha suggerimenti sbagliati, salvare in tmx!"
				else:
					#mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text().decode(self.encoding),self.listemsgstr[self.transtabview.Selection()].trnsl.Text().decode(self.encoding))
					mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text(),self.listemsgstr[self.transtabview.Selection()].trnsl.Text())
					#print "eseguo riga: 5083"
					Thread(target=self.tmcommunicate,args=(mx,)).start()
					#thread.start_new_thread( self.tmcommunicate, (mx,) )
					#print "mah, questo è corretto ma non ha suggerimenti, da salvare in tmx!"
			return
		elif msg.what == 963741:
			schplur = msg.FindInt8('plural')
			#schsrcplur = msg.FindInt8('srcplur')
			self.sourcestrings.lv.ScrollToSelection()
			self.transtabview.Select(schplur)
			if schplur>0:
				self.srctabview.Select(1)
			inizi=msg.FindInt32('inizi')
			fin=msg.FindInt32('fin')
			srctrnsl=msg.FindInt8('srctrnsl')
			#indolor=msg.FindInt8('index')
			#name=time.time()
			Thread(target=self.highlightlater,args=(inizi,fin,schplur,srctrnsl,)).start()#str(name),
			return
		elif msg.what == 852630:
			#highlight source text
			inizi = msg.FindInt32("inizi")
			fin = msg.FindInt32("fin")
			schede =  msg.FindInt8("schede")
			self.listemsgid[schede].src.MakeFocus(True)
			self.listemsgid[schede].src.Highlight(inizi,fin)
			return
		elif msg.what == 852631:
			#highlight translation text
			inizi = msg.FindInt32("inizi")
			fin = msg.FindInt32("fin")
			schede =  msg.FindInt8("schede")
			self.listemsgstr[schede].trnsl.MakeFocus(True)
			self.listemsgstr[schede].trnsl.Highlight(inizi,fin)
			return
		elif msg.what == 104501:
			self.tmscrollsugj.lv.AddItem(ErrorItem("┌─────────────────────┐"))
			self.tmscrollsugj.lv.AddItem(ErrorItem("| Error connecting to |"))
			self.tmscrollsugj.lv.AddItem(ErrorItem("| Translation Memory  |"))
			self.tmscrollsugj.lv.AddItem(ErrorItem("|       server        |"))
			self.tmscrollsugj.lv.AddItem(ErrorItem("└─────────────────────┘"))
			return
		#445380 huge check on older version look at that code
		BWindow.MessageReceived(self, msg)
		
	def highlightlater(self,inizi,fin,schede,srctrnsl):
		self.event.wait(0.1)
		if srctrnsl==0:
			mexacio = BMessage(852630)
		else:
			mexacio = BMessage(852631)
		mexacio.AddInt32("inizi",inizi)
		mexacio.AddInt32("fin",fin)
		mexacio.AddInt8("schede",schede)
#		mexacio.AddInt8("srctrnsl",srctrnsl)
		be_app.WindowAt(0).PostMessage(mexacio)
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
		ent,confile=Ent_config()
		Config.read(confile)
		sezioni=Config.sections()
		cfgfile = open(confile,'w')
		dict={0:'fuzzy',1:'untranslated',2:'translated',3:'obsolete'}
		if not "Listing" in sezioni:
			Config.add_section('Listing')
		if self.poview[index]:
			men=self.savemenu.FindItem(index+74)
			men.SetMarked(0)
			Config.set('Listing',dict[index],"False")
			self.poview[index]=False
		else:
			men=self.savemenu.FindItem(index+74)
			men.SetMarked(1)
			Config.set('Listing',dict[index],"True")
			self.poview[0]=True
		Config.write(cfgfile)
		cfgfile.close()
		#self.sourcestrings.reload(self.poview,self.pofile,self.encoding)
	#	x=0
	#	while x!=len(self.viewarr):
	#		if x==index:
	#			self.viewarr[x].SetMarked(1)
	#		else:
	#			self.viewarr[x].SetMarked(0)
	#		x+=1
	#	self.sort=index
	#	ent,confile=Ent_config()
	#	Config.read(confile)
	#	cfgfile = open(confile,'w')
	#	if not ("General" in Config.sections()):
	#		Config.add_section("General")
	#	Config.set('General','sort', str(self.sort))
	#	Config.write(cfgfile)
	#	cfgfile.close()
	#	Config.read(confile)
	#	self.sourcestrings.reload(self.poview,self.pofile,self.encoding)
	def server(self,addr,PORT=2022,HEADER=4096,log=False):#addr if local addr = 127.0.0.1 elif remote: passed by variable
		if log:
			with open(flog, 'a') as des:
				des.write("launching server...\n")
		perc=BPath()
		find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
		datapath=BDirectory(perc.Path()+"/HaiPO2")
		ent=BEntry(datapath,perc.Path()+"/HaiPO2")
		if not ent.Exists():
			datapath.CreateDirectory(perc.Path()+"/HaiPO2", datapath)
		ent.GetPath(perc)
		ftmx=perc.Path()+'/outtmx.db'
		flog=perc.Path()+'/log.txt'
		tmp_ftmx=perc.Path()+'/tmp_outtmx.db'
		old_ftmx=perc.Path()+'/old_outtmx.db'
		#HEADER = 4096 #TODO pass variable from config
		IP = socket.gethostbyname(addr)
		#PORT = 2022 #TODO pass variable from config
		self.keeperoftheloop=True
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
			server_socket.bind((IP,PORT))
			server_socket.listen()
			try:
				while self.keeperoftheloop:
					if log:
						with open(flog, 'a') as des:
							des.write("I\'m in the loop...\n")
					client_socket, client_address = server_socket.accept()
					with client_socket:
						if log:
							#print(f"Connected by {client_address}")
							with open(flog, 'a') as des:
								des.write(f"Connected by {client_address}\n")
						while True:
							try:
								instr = client_socket.recv(HEADER)
								if not instr:
									break
								if log:
									with open(flog, 'a') as des:
										des.write(f"Richiesto: {instr}\n")
								message = pickle.loads(instr)
								if log:
									with open(flog, 'a') as des:
										des.write(f"Message: {message}\n")
										des.write(f"Message type: {type(message)}\n")
								suggerimenti=[]
								if message==[None]:
									suggerimenti.append(None)
									packsug=pickle.dumps(suggerimenti,protocol=2)
									client_socket.sendall(packsug)
									self.keeperoftheloop=False
									break
								elif message[0][0]==None:
									if log:
										with open(flog, 'a') as des:
											des.write(f"trying to add source:  {message[0][1]}\nand translation: {message[0][2]}\n")
									if message[0][1]!="" and message[0][2]!="":
										with open(ftmx, 'rb') as fin:
											with open(tmp_ftmx, 'a') as des:
												whole=fin.read()
												liniis=whole.decode("utf-8").split('\n')
												for linie in liniis:
													if "</body>" not in str(linie):
													#if str(linie).find("</body>")==-1:
														des.write(str(linie)+"\n")
													else:
														msgid=html.escape(message[0][1])
														msgstr=html.escape(message[0][2])
														des.write("    <tu>\n      <tuv xml:lang=\"en\">\n        <seg>"+msgid+"</seg>\n      </tuv>\n")
														des.write("      <tuv xml:lang=\"fur\">\n        <seg>"+msgstr+"</seg>\n      </tuv>\n    </tu>\n")
														des.write("  </body>\n</tmx>\n")
														des.close()
														save_db(old_ftmx,tmp_ftmx,ftmx)
														#if os.path.exists(old_ftmx):
														#	os.remove(old_ftmx)
														#os.rename(ftmx,old_ftmx)
														#os.rename(tmp_ftmx,ftmx)
														break
										break
								elif message[0][0]==('d','e','l'):
										with open(ftmx, 'r', encoding='utf-8') as fin, open(tmp_ftmx, 'a', encoding='utf-8') as des:
												whole=fin.read()
												liniis=whole.split('\n')
												nl=len(liniis)
												i=0
												while i<nl:
													if '<tu>' not in str(liniis[i]):
														des.write(str(liniis[i])+"\n")
													else:
														k=1
														nextclose=False
														txt=str(liniis[i])+"\n"
														if 'tuv xml:lang="en"' in  str(liniis[i + k]):
														#if str(liniis[i+k]).find("tuv xml:lang=\"en\"")>-1:
															txt+=str(liniis[i+k])+"\n"
															while True:
																k+=1
																txt+=str(liniis[i+k])+"\n"
																if '<tuv xml:lang="fur">' in str(liniis[i+k]):
																#if str(liniis[i+k]).find("<tuv xml:lang=\"fur\">")>-1:
																	nextclose=True
																if nextclose:
																	if '</seg>' in str(liniis[i+k]):
																	#if str(liniis[i+k]).find("</seg>")>-1:
																		k+=1
																		txt+=str(liniis[i+k])+"\n" #this adds /tuv
																		txt+=str(liniis[i+k+1])+"\n" #this adds /tu
																		break
															#if (txt.find("<seg>"+message[0][1]+"</seg>")>-1) and (txt.find("<seg>"+message[0][2]+"</seg>")>-1):
															msgid=html.escape(message[0][1])
															msgstr=html.escape(message[0][2])
															if "<seg>"+msgid+"</seg>" in txt and "<seg>"+msgstr+"</seg>" in txt:
																i+=k+1
															else:
																des.write(txt)
																#for rie in txt:
																#    des.write(rie)
																i+=k+1
													i+=1
											#des.close()
										save_db(old_ftmx,tmp_ftmx,ftmx)
										#if os.path.exists(old_ftmx):
										#	 os.remove(old_ftmx)
										#os.rename(ftmx,old_ftmx)
										#os.rename(tmp_ftmx,ftmx)
										break
								else:
									lung1=len(message[0])
									lung2=round(lung1*0.75,0)
									delta=lung1-lung2+1
									with open(ftmx, 'rb') as fin:
										tmx_file = tmxfile(fin, "en", "fur")
										for node in tmx_file.unit_iter():
											dist=lev(message[0],node.source)
											if dist<delta:#2
												suggerimenti.append((node.target,dist))
									suggerimenti.sort(key=lambda element:element[1])
									client_socket.send(pickle.dumps(suggerimenti,protocol=2))
							except FileNotFoundError as e:
								with open(ftmx, 'a') as des:
									des.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tmx SYSTEM \"tmx14.dtd\">\n<tmx version=\"1.4\">\n  <header creationtool=\"Translate Toolkit\" creationtoolversion=\"3.8.0\" segtype=\"sentence\" o-tmf=\"UTF-8\" adminlang=\"en\" srclang=\"en\" datatype=\"PlainText\"/>\n  <body>\n")
									des.write("  </body>\n</tmx>\n")
			except KeyboardInterrupt:
				server_socket.close()
				print("interrotto dall'utente")
		#server_socket.close()
		print("Server closed")
		
	def QuitRequested(self):
		self.keeperoftheloop = False
		Thread(target=self.tmcommunicate,args=(None,)).start()
		be_app.PostMessage(B_QUIT_REQUESTED)
		return BWindow.QuitRequested(self)

def save_db(old_ftmx,tmp_ftmx,ftmx):
	e=BEntry(old_ftmx)
	if e.Exists():
		e.Remove()
	del e
	BEntry(ftmx).Rename(old_ftmx)
	BEntry(tmp_ftmx).Rename(ftmx)

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
	def MessageReceived(self, msg):
		if msg.what == B_SAVE_REQUESTED:
			e = msg.FindString("name")
			messaggio = BMessage(54173)
			messaggio.AddString("name",e)
			be_app.WindowAt(0).PostMessage(messaggio)
			return
		BApplication.MessageReceived(self,msg)
	def Pulse(self):
		be_app.WindowAt(0).PostMessage(BMessage(66))

def main():
	global be_app
	be_app = App()
	be_app.Run()	
 
if __name__ == "__main__":
    main()
