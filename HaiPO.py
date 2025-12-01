#!/boot/system/bin/python3
from Be import BApplication, BWindow, BView, BMenu,BMenuBar, BMenuItem, BSeparatorItem, BMessage, window_type, B_NOT_RESIZABLE, B_CLOSE_ON_ESCAPE, B_QUIT_ON_WINDOW_CLOSE, BButton, BTextView, BTextControl, BAlert, BListItem,BMenuField, BListView, BScrollView,BRect, BBox, BFont, InterfaceDefs, BPath, BDirectory, BEntry, BStringItem, BStringView,BCheckBox,BTranslationUtils, BBitmap, AppDefs, BTab, BTabView, BNodeInfo, BMimeType, BScrollBar,BPopUpMenu,BScreen,BStatusBar,BPoint,BNode,BUrl# BFile,

from Be.View import B_FOLLOW_NONE,set_font_mask,B_WILL_DRAW,B_NAVIGABLE,B_FULL_UPDATE_ON_RESIZE,B_FRAME_EVENTS,B_PULSE_NEEDED,B_FOLLOW_ALL_SIDES,B_FOLLOW_TOP,B_FOLLOW_LEFT_RIGHT,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT,B_FOLLOW_RIGHT,B_FOLLOW_TOP_BOTTOM
from Be.Menu import menu_info,get_menu_info
from Be.FindDirectory import *
from Be.Alert import alert_type
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
from Be.Architecture import get_architecture

import configparser,struct,threading,os,re,datetime,time,codecs,encodings,gettext
#from gettext import compile_domain
import enchant
try:
	from polib import polib
except:
	import polib
import pickle,socket,os,sys,html,subprocess,tempfile

from translate.storage.tmx import tmxfile
from translate.tools import junitmsgfmt
from Levenshtein import distance as lev

from distutils.spawn import find_executable
import socket,pickle,unicodedata
from threading import Thread
from babel import Locale
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo
from itertools import combinations


Config=configparser.ConfigParser()

def openlink(link):
	osd=BUrl(link)
	if osd.HasPreferredApplication():
		retu=osd.OpenWithPreferredApplication()
	else:
		#not an URL maybe a local file
		cmd = "open "+link
		t = Thread(target=os.system,args=(cmd,))
		t.run()

def cstep(n,r,h):
	s=5*(n+1)+(6+h)*n
	sh=5*n+(6+h)*(n+1)		
	return BRect(5,s,r-5,sh)

def lookfdata(name):
	perc=BPath()
	find_directory(directory_which.B_SYSTEM_DATA_DIRECTORY,perc,False,None)
	ent=BEntry(perc.Path()+"/HaiPO2/"+name)
	if ent.Exists():
		#use mascot installed in system data folder
		ent.GetPath(perc)
		return (True,perc.Path())
	else:
		find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
		ent=BEntry(perc.Path()+"/HaiPO2/"+name)
		if ent.Exists():
			#use mascot installed in user data folder
			ent.GetPath(perc)
			return (True,perc.Path())
		else:
			nopages=True
			cwd = os.getcwd()
			ent=BEntry(cwd+"/data/"+name)
			if ent.Exists():
				#use mascot downloaded with git by cmdline
				ent.GetPath(perc)
				return (True,perc.Path())
				nopages=False
			else:
				alt="".join(sys.argv)
				mydir=os.path.dirname(alt)
				link=mydir+"/data/"+name
				ent=BEntry(link)
				if ent.Exists():
					#use mascot downloaded with git by graphical launch
					ent.GetPath(perc)
					return (True,perc.Path())
					nopages=False
			if nopages:
				return (False,None)
				

class LocalizItem(BMenuItem):
	def __init__(self,name):
		self.name=name
		msg=BMessage(600)
		msg.AddString("name",self.name)
		BMenuItem.__init__(self,self.name,msg,'\x00',0)

locale_dir=None
b,p=lookfdata("locale")
if b:
	if BEntry(p).IsDirectory():
		locale_dir=p
		dir=BDirectory(p)
		ent=BEntry()
		dir.Rewind()
		lista_traduzioni=[]
		ret = False
		while not ret:
			ret=dir.GetNextEntry(ent,True)
			if not ret:
				perc=BPath()
				ent.GetPath(perc)
				lista_traduzioni.append(perc.Leaf())
	else:
		locale_dir=None
		t = gettext.NullTranslations()
		#but it was a file


def Ent_config():
	perc=BPath()
	find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
	datapath=BDirectory(perc.Path()+"/HaiPO2")
	ent=BEntry(datapath,perc.Path()+"/HaiPO2")
	if not ent.Exists():
		datapath.CreateDirectory(perc.Path()+"/HaiPO2", None)#datapath)
	ent.GetPath(perc)
	confile=BPath(perc.Path()+'/config.ini',None,False)
	ent=BEntry(confile.Path())
	return(ent,confile.Path())

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

#look for General in config.ini wether localization has been set
ent,confile=Ent_config()
Config.read(confile)
try:
	localization=ConfigSectionMap("General")['localization']
except:
	localization = "en"
	t = gettext.NullTranslations()
	
if locale_dir!=None:
	try:
		t = gettext.translation(
			domain="haipo",  # project name
			localedir=locale_dir,
			languages=[localization],
			fallback=True  # use english if the language does not exist
		)
	except Exception as e:
		print(f"Error loading translations: {e}")
		t = gettext.NullTranslations()

global _
_ = t.gettext
# Translators: The name of this app
appname=_("HaiPO")
ver="2.5"
# Translators: do not translate, just transliterate
state=_("beta")
version=" ".join((appname,ver,state))#'HaiPO x.x beta'

	
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

class PView(BView):
	def __init__(self,frame,name,immagine):
		self.immagine=immagine
		self.frame=frame
		BView.__init__(self,self.frame,name,B_FOLLOW_ALL_SIDES,B_WILL_DRAW)
		
	def UpdateImg(self,immagine):
		self.immagine=immagine
		a,b,c,d=self.frame
		rect=BRect(0,0,self.immagine.Width(),self.immagine.Height())
		self.DrawBitmap(self.immagine,rect)

	def Draw(self,rect):
		BView.Draw(self,rect)
		#a,b,c,d=self.frame
		rect=BRect(0,0,self.frame.Width(),self.frame.Height())
		self.DrawBitmap(self.immagine,rect)



class MyListView(BListView):
	def __init__(self, frame, name, type):
		BListView.__init__(self, frame, name, type)
	
	def MouseDown(self,point):
		if self.CurrentSelection() >-1:
			item=self.ItemAt(self.CurrentSelection())
			if type(item)!=LangListItem:
				if item.hasplural:
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
						thistranslEdit.Save() #it's not importat which EventTextView launches Save(), it will save both anyway
				else:
					itemtext=be_app.WindowAt(0).listemsgstr[0].trnsl
					if itemtext.tosave:
						if itemtext.Text()!= itemtext.oldtext:
							itemtext.Save()
				if showspell:
					be_app.WindowAt(0).PostMessage(333111)
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
		return BListView.KeyDown(self,char,bytes)

class ScrollSugj:
	HiWhat = 141# Doubleclick --> paste to trnsl TextView
	SectionSelection = 140
	def __init__(self, rect, name):
		self.lv = KListView(rect, name, list_view_type.B_SINGLE_SELECTION_LIST)
		self.lv.SetInvocationMessage(BMessage(self.HiWhat))
		self.lv.SetSelectionMessage(BMessage(self.SectionSelection))
		self.sv = BScrollView('ScrollSugj', self.lv, B_FOLLOW_RIGHT|B_FOLLOW_TOP|B_FOLLOW_RIGHT, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, True,True, border_style.B_FANCY_BORDER)
		
	def SelectedText(self):
		return self.lv.ItemAt(self.lv.CurrentSelection()).Text()

	def Clear(self):
		self.lv.DeselectAll()
		self.lv.MakeEmpty()

class TranslatorComment(BWindow):
	kWindowFrame = BRect(150, 150, 450, 300)
	# Translators: Window title
	kWindowName = _("Translator comment")

	def __init__(self,listindex,item,backupfile):
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
		# Translators: Button label/action
		kButtonName = _("Save comment")
		self.savebtn = BButton(kButtonFrame, kButtonName, kButtonName, BMessage(5252))
		self.underframe.AddChild(self.savebtn,None)
		self.item=item
		self.listindex=listindex
		if self.item.tcomment!="":
			self.tcommentview.SetText(self.item.tcomment,None)
		
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
	def __init__(self,superself,playground1,name,altece):
		self.name = name
		BBox.__init__(self,BRect(0,0,playground1[2]-playground1[0],playground1[3]-playground1[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.hsrc = playground1[3] - playground1[1] - altece
		self.src = srcTextView(superself,BRect(playground1[0],playground1[1],playground1[2]-playground1[0]-18,playground1[3]-playground1[1]),name+'_source_BTextView',BRect(5.0,5.0,playground1[2]-30,playground1[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.src.MakeEditable(False)
		self.AddChild(self.src,None)
		bi,bu,bo,ba = playground1
		self.scrollbsrc=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.src,0.0,0.0,B_VERTICAL)
		self.AddChild(self.scrollbsrc,None)

class trnsltabbox(BBox):
	def __init__(self,playground2,name,superself):
		self.name = name
		BBox.__init__(self,BRect(0,0,playground2[2]-playground2[0],playground2[3]-playground2[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.trnsl = EventTextView(superself,BRect(playground2[0],playground2[1],playground2[2]-playground2[0]-18,playground2[3]-playground2[1]),name+'_translation_BTextView',BRect(5.0,5.0,playground2[2]-30,playground2[3]-5),B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.trnsl.MakeEditable(True)
		self.AddChild(self.trnsl,None)
		bi,bu,bo,ba = playground2
		self.scrollbtrans=BScrollBar(BRect(bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.trnsl,0.0,0.0,orientation.B_VERTICAL)
		self.AddChild(self.scrollbtrans,None)

class contexttabbox(BBox):
	def __init__(self,frame,superself):
		name="context"
		self.name = name
		extrect=BRect(frame[0],frame[1],frame[2]-frame[0]-20,frame[3]-frame[1]-37)
		inrect=extrect
		inrect.InsetBy(2,2)
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.context = BTextView(extrect,name+'_context_BTextView',inrect,B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.context.MakeEditable(False)
		self.AddChild(self.context,None)
		scrrect=BRect(extrect.right,4,extrect.right+20,extrect.bottom+1)
		self.scrollbcont=BScrollBar(scrrect,name+'_ScrollBar',self.context,0.0,0.0,orientation.B_VERTICAL)
		self.AddChild(self.scrollbcont,None)
		
class commenttabbox(BBox):
	def __init__(self,frame,superself):
		name="comment"
		self.name = name
		extrect=BRect(frame[0],frame[1],frame[2]-frame[0]-20,frame[3]-frame[1]-37)
		inrect=extrect
		inrect.InsetBy(2,2)
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.comment = BTextView(extrect,name+'_comment_BTextView',inrect,B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.comment.MakeEditable(False)
		self.AddChild(self.comment,None)
		scrrect=BRect(extrect.right,4,extrect.right+20,extrect.bottom+1)
		self.scrollbcom=BScrollBar(scrrect,name+'_ScrollBar',self.comment,0.0,0.0,orientation.B_VERTICAL)
		self.AddChild(self.scrollbcom,None)

class tcommenttabbox(BBox):
	def __init__(self,frame,superself):
		name="tcomment"
		self.name = name
		extrect=BRect(frame[0],frame[1],frame[2]-frame[0]-20,frame[3]-frame[1]-37)
		inrect=extrect
		inrect.InsetBy(2,2)
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.tcomment = BTextView(extrect,name+'_comment_BTextView',inrect,B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.tcomment.MakeEditable(False)
		self.AddChild(self.tcomment,None)
		scrrect=BRect(extrect.right,4,extrect.right+20,extrect.bottom+1)
		self.scrollbtcom=BScrollBar(scrrect,name+'_ScrollBar',self.tcomment,0.0,0.0,orientation.B_VERTICAL)
		self.AddChild(self.scrollbtcom,None)

class previoustabbox(BBox):
	def __init__(self,frame,superself):
		name="prev_msgid"
		self.name = name
		extrect=BRect(frame[0],frame[1],frame[2]-frame[0]-20,frame[3]-frame[1]-37)
		inrect=extrect
		inrect.InsetBy(2,2)
		BBox.__init__(self,BRect(0,0,frame[2]-frame[0],frame[3]-frame[1]),name,B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.prev = BTextView(extrect,name+'_comment_BTextView',inrect,B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		self.prev.MakeEditable(False)
		self.AddChild(self.prev,None)
		scrrect=BRect(extrect.right,4,extrect.right+20,extrect.bottom+1)
		self.scrollbprev=BScrollBar(scrrect,name+'_ScrollBar',self.prev,0.0,0.0,orientation.B_VERTICAL)
		self.AddChild(self.scrollbprev,None)

class MsgStrItem(BListItem):
	nocolor = (0, 0, 0, 0)
	####  states table
	untranslated = 0
	translated = 1
	fuzzy = 2
	obsolete = 3
	hasplural = False
	tosave=False
	txttosave=""
	txttosavepl=[]
	#dragcheck=False 
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
			tempcolor.red=210
			tempcolor.green=200
			tempcolor.blue=255
			owner.SetHighColor(tempcolor)
			#owner.SetFont(self.font)
			#xtxt='Pl >>'
			#owner.DrawString(xtxt,None)
			#ww=self.font.StringWidth(xtxt)
			owner.FillTriangle(BPoint(frame.left+5.0,frame.top+5.0),BPoint(frame.left+5.0,frame.top+14.0),BPoint(frame.left+12.8,frame.top+9.5))
			owner.SetHighColor(self.color)
			self.font = be_plain_font
			owner.SetFont(self.font)
			#owner.MovePenTo(frame.left+ww+10,frame.bottom-5)
			owner.MovePenTo(frame.left+15,frame.bottom-5)
			owner.DrawString(self.text,None)
		else:
			owner.SetHighColor(self.color)
			owner.MovePenTo(frame.left+5,frame.bottom-5)
			owner.DrawString(self.text,None)
			owner.SetLowColor(self.mycolors["clear"])
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
		self.paste=False
		color=rgb_color()
		BTextView.__init__(self,frame,name,textRect,be_plain_font,color,resizingMode,flags)
		self.mousemsg=struct.unpack('!l', b'_MMV')[0]#mouse move
		self.middlemsgup=struct.unpack('!l', b'_MUP')[0]#middle mouse up
		self.middlemsgdn=struct.unpack('!l', b'_MDN')[0]
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
		bckpmsg.AddBool('tmx',True)
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
				thisBlistitem.msgstrs=[]
				thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text())
				thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
				bckpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgstr[cox].trnsl.Text())
				cox+=1
		bckpmsg.AddString('bckppath',self.superself.backupfile)
		be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
		#self.superself.infoprogress.SetText(str(self.superself.pofile.percent_translated())) #reinsert if something doesn't work properly but it should write in 16892/3
		self.superself.progressinfo.Update(1,None,str(self.superself.pofile.percent_translated())+"%")
	def SaveToOrig(self):
		thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
		thisBlistitem.tosave=True
		tabs=len(self.superself.listemsgstr)-1
		savpmsg=BMessage(16893)
		savpmsg.AddInt8('savetype',1)
		savpmsg.AddBool('tmx',True)
		savpmsg.AddInt32('tvindex',self.superself.sourcestrings.lv.CurrentSelection())
		savpmsg.AddInt8('plurals',tabs)
		if tabs == 0:
			thisBlistitem.txttosave=self.Text()
			thisBlistitem.msgstrs=self.Text()
			savpmsg.AddString('translation',thisBlistitem.txttosave)
		else:
			thisBlistitem.txttosavepl=[]
			thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
			thisBlistitem.msgstrs=[]
			thisBlistitem.msgstrs.append(self.superself.listemsgstr[0].trnsl.Text())
			savpmsg.AddString('translation',thisBlistitem.txttosave)
			cox=1
			while cox < tabs+1:
				thisBlistitem.msgstrs=[]
				thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text())
				thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
				savpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgstr[cox].trnsl.Text())
				cox+=1
		savpmsg.AddString('bckppath',self.superself.filen+self.superself.file_ext)
		be_app.WindowAt(0).PostMessage(savpmsg)
		self.superself.progressinfo.Update(1,None,str(self.superself.pofile.percent_translated())+"%")
	def checklater(self,name,oldtext,indexBlistitem):
		mes=BMessage(112118)
		mes.AddInt32('indexBlistitem',indexBlistitem)
		mes.AddString('oldtext',oldtext)
		self.event.wait(0.1)
		be_app.WindowAt(0).PostMessage(mes)
	def undropper(self):
		self.event.wait(0.1)
		be_app.WindowAt(0).PostMessage(BMessage(113119))

	def MouseUp(self,point):
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
						self.pop.AddItem(BMenuItem(aelem[1], msz,'\x00',0))
					pointo=self.PointAt(ubi2)
					self.ConvertToScreen(pointo[0])#overwrites pointo[0] with screen BPoint values
					x = self.pop.Go(pointo[0], True,False,False)
					if x:
						self.superself.Looper().PostMessage(x.Message())
		return BTextView.MouseUp(self,point)

	def MessageReceived(self, msg):
		if msg.what in [B_CUT,B_PASTE]:
			thisBlistitem=self.superself.sourcestrings.lv.ItemAt(self.superself.sourcestrings.lv.CurrentSelection())
			thisBlistitem.tosave=True
			self.tosave=True
			be_app.WindowAt(0).PostMessage(333111)
		elif msg.what == self.dragmsg:
			#print("c\'è un drag&drop")
			Thread(target=self.undropper).start()
			
			indexBlistitem=self.superself.sourcestrings.lv.CurrentSelection()
			name=time.time()
			self.checklater(str(name), self.Text(),indexBlistitem)
		elif msg.what == self.middlemsgdn:
			button=msg.FindInt32('buttons')
			if button == 4: #4=middle button
				self.paste=True
			else:
				self.paste=False
		elif msg.what == self.middlemsgup:
			if self.paste:
				position=BPoint()
				where=msg.FindPoint('be:view_where',position)
				pos1,pos2 = self.superself.listemsgid[self.superself.srctabview.Selection()].src.GetSelection()
				if pos1==pos2:
					pos1,pos2 = self.superself.expander.GetSelection()
					if pos1==pos2:
						return BTextView.MessageReceived(self,msg)
					else:
						bytext=self.superself.expander.GetText(pos1,pos2-pos1)
						self.superself.expander.Select(0,0)
						pos1=0
						pos2=0
				else:
					bytext=self.superself.listemsgid[self.superself.srctabview.Selection()].src.GetText(pos1,pos2-pos1)
					self.superself.listemsgid[self.superself.srctabview.Selection()].src.Select(0,0)
					pos1=0
					pos2=0
				self.Insert(self.OffsetAt(position),bytext,byte_count(bytext)[0],None)
				self.paste=False
				indexBlistitem=self.superself.sourcestrings.lv.CurrentSelection()
				name=time.time()
				self.checklater(str(name), self.Text(),indexBlistitem)

		return BTextView.MessageReceived(self,msg)

	def KeyDown(self,char,bytes):
		try:
			arrow=False
			ochar=ord(char)
			#print(ochar)
			if ochar in (B_DOWN_ARROW,B_UP_ARROW,B_PAGE_UP,B_PAGE_DOWN,10,48,49,50,51,52,53,54,55,56,57): #B_ENTER =10?
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
				elif ochar == 48:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",9)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 49:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",0)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 50:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",1)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 51:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",2)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 52:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",3)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 53:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",4)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 54:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",5)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 55:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",6)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 56:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",7)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 57:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",8)
						be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						if not value:
							self.tosave=True
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
					elif ochar in [B_LEFT_ARROW,B_RIGHT_ARROW,B_DOWN_ARROW,B_UP_ARROW]:
						arrow=True
					elif ochar == 116:
						self.superself.sem.acquire()
						value=self.superself.shortcut #CTRL SHIFT pressed
						self.superself.sem.release()
						if value:
							self.superself.switcher()
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
						if not arrow:
							be_app.WindowAt(0).PostMessage(333111)
					elif self.Text()=="":
						be_app.WindowAt(0).PostMessage(826066)
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
		if self.superself.skipcheck:
			self.superself.speloc.acquire()
			self.superself.intime=time.time()
			self.superself.speloc.release()
		else:
		#try:
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
					splitti=parola.split()
					for parola in splitti:
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
							break

			self.SetText(txt,TXT_ARR)			
			self.Select(indi,indf)
			return ret
		#except:
		#	return None
def find_byte(lookf,looka,offset=0):
	#note offset is not byte-offset but char-offset
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
		newarr.append((False,t,bc[0],byte_offset))#False = do not spellcheck
		text=text[text.find(words[0]):]
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

class CategoryTextView(BTextView):
	def __init__(self,frame,name,textRect,resizingMode,flags):
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)
		self.MakeSelectable(0)
		self.SetAlignment(alignment.B_ALIGN_CENTER)
		self.SetStylable(1)
		big_font = BFont()#be_plain_font
		oldsize=be_plain_font.Size()
		big_font.SetSize(32)
		self.first_run=text_run()
		self.first_run.font=big_font
		self.small_font=big_font
		self.small_font.SetSize(11)
		self.bc_color=rgb_color()
		self.bc_color.green=150
		self.mousemsg=struct.unpack('!l', b'_MMV')[0]
		self.dragmsg=struct.unpack('!l', b'MIME')[0]
		
	def SetSingleChar(self,char,bytes):
		# Translators: Bytes used by the indicated character
		# Translators: by pressing a key after this string it shows the bytes used by the character itself
		myTXT=char+" ⇨ "+unicodedata.category(char)+"\n"+_("char bytes:")+" "+str(bytes)#→
		txt_run2=text_run()
		txt_run2.offset=find_byte("char",myTXT)
		txt_run2.font=self.small_font
		txt_run2.color=self.bc_color
		myruns=[self.first_run,txt_run2]
		self.SetText(myTXT,myruns)
	def KeyDown(self,char,bytes):
		self.SetSingleChar(char,bytes)

	def MessageReceived(self, msg):
		if msg.what == B_PASTE:
			BTextView.MessageReceived(self,msg)
			nt=self.Text()[0]
			self.SetSingleChar(nt,byte_count(nt)[0])
			return
		elif msg.what == B_CUT:
			return
		elif msg.what == self.dragmsg:
			#mexico=msg.FindMessage('be:drag_message')
			#self.SelectAll()
			#self.Clear()
			return

		return BTextView.MessageReceived(self,msg)

class TranslatorTextView(BTextView):
	def __init__(self,superself,frame,name,textRect,resizingMode,flags):
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)
		self.superself=superself
	def KeyDown(self,char,bytes):
		ochar=ord(char)
		if self.superself.shortcut:
			if ochar == 116: #ctrl+shift+t
				self.superself.switcher()
				return
			elif ochar == 99:
				self.superself.es_src.SelectAll()
				self.superself.es_src.Clear()
				self.superself.es_trans.SelectAll()
				self.superself.es_trans.Clear()
				return
			else:
				return BTextView.KeyDown(self,char,bytes)
		else:
			return BTextView.KeyDown(self,char,bytes)
			
class srcTextView(BTextView):
	def __init__(self,superself,frame,name,textRect,resizingMode,flags):
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)
		self.superself=superself
		self.SetStylable(1)
		self.spaces=["\\x20","\\xc2\\xa0","\\xe1\x9a\\x80","\\xe2\\x80\\x80","\\xe2\\x80\\x81","\\xe2\\x80\\x82","\\xe2\\x80\\x83","\\xe2\\x80\\x84","\\xe2\\x80\\x85","\\xe2\\x80\\x86","\\xe2\\x80\\x87","\\xe2\\x80\\x88","\\xe2\\x80\\x89","\\xe2\\x80\\x8a","\\xe2\\x80\\x8b","\\xe2\\x80\\xaf","\\xe2\\x81\\x9f","\\xe3\\x80\\x80"]
	def Draw(self,suaze):
		BTextView.Draw(self,suaze)
		self.font = be_plain_font
		tst=self.Text()
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
					foundo=find_byte(ci,self.Text(),index)
					asd=self.PointAt(foundo)
					foundo+=1
					self.SetHighColor(0,0,200,0)
					self.MovePenTo(BPoinu(asd[0].x+(self.font.StringWidth(ci)/2),asd[0].y+asd[1]-3))
					self.DrawString('͜',None)#'̳')#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
					self.SetHighColor(0,0,0,0)
			else:
				mum="\\"+a_hex[0][1:]
				if mum in self.spaces:
					foundo=find_byte(ci,self.Text(),index)
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
						self.DrawString('̳',None)#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
						self.SetHighColor(0,0,0,0)
				elif mum=="\\xa":
					foundo=find_byte(ci,self.Text(),index)
					asd=self.PointAt(foundo)
					foundo+=1
					self.SetHighColor(200,0,0,0)
					fon=BFont()
					self.GetFont(fon)
					self.MovePenTo(BPoint(asd[0].x,asd[0].y+asd[1]-3))
					self.DrawString('⏎',None)
					self.SetHighColor(0,0,0,0)
				elif mum=="\\x9":
					self.SetHighColor(200,0,0,0)
					foundo=find_byte(ci,self.Text(),index)
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
		return
	def KeyDown(self,char,bytes):
		ochar=ord(char)
		if self.superself.shortcut:
			if ochar == 116: #ctrl+shift+t
				self.superself.switcher()
				return
			else:
				return BTextView.KeyDown(self,char,bytes)
		
def checklang(orderedata):
	ent,confile=Ent_config()
	Config.read(confile)
	confexists=False #user section exists
	samelang=-1 #1=not the same language; -1=Language metadata not detected(B_ERROR); 0=Same language(B_OK)
	try:
		#check language in config
		llangs=ConfigSectionMap("Translator")['langs'].split(",")
		confexists=True
		#check Language metadata presence
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
		# Translators: user full name
		self.name=BTextControl(BRect(box[0],box[1],box[2],box[1]+fon.Size()),"fullname",_("Full Name"),None,BMessage(152))
		# Translators: user e-mail
		self.mail=BTextControl(BRect(box[0],box[1]+fon.Size()+step,box[2],box[1]+fon.Size()*2+step),"mail",_("E-mail"),None,BMessage(153))
		# Translators: team language name, for example Friulian
		self.lt=BTextControl(BRect(box[0],box[1]+fon.Size()*2+step*2,box[2],box[1]+fon.Size()*3+step*2),"lang_team",_("Language team"),None,BMessage(154))
		# Translators: e-mail for the language team
		self.ltmail=BTextControl(BRect(box[0],box[1]+fon.Size()*3+step*3,box[2],box[1]+fon.Size()*4+step*3),"team_mail",_("Language-team e-mail"),None,BMessage(155))
		# Translators: list of accepted languages
		self.lang=BStringView(BRect(box[0],box[1]+fon.Size()*5+step*4,box[2],box[1]+fon.Size()*6+step*4),"lang_string",_("Accepted languages:"))
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
		locale=Locale.default()
		#for i in locale.territories:
		#	territori.append(locale.territories[i])
		#
		#per ottenere gli stati in lingua locale
		for i in locale.languages:
			suggested=False
			try:
				l=Locale.parse(i)
				dn=l.get_display_name()
			except:
				dn=locale.languages[i]
			if str(Locale.default()) in i:
				suggested=True
			try:
				self.lli.append(LangListItem(dn,i,suggested))
				self.langlist.lv.AddItem(self.lli[-1])
			except:
				#sometimes dn results in NoneType (because, in the current system localization,
				#babel doesn't know the name of the iso code, this does not mean that it's 
				#unknown in other localizations).
				#Here we can choose to support the language through its iso code
				#without knowing its name, or avoid supporting this language.
				#For now we are ignoring these languages, but we are open to change our mind
				pass
		# Translators: Used to add a language iso code not present in available languages
		self.lli.append(LangListItem(_("Add custom iso code"),None,False))
		self.langlist.lv.AddItem(self.lli[-1])
		# Translators: Button
		self.BtnSave=BButton(BRect(box[2]/2+100,box[3]-50,box[2]-5,box[3]-5),'SaveUserSettingsBtn',_('Save'),BMessage(612))
		# Translators: Button
		self.BtnCancel=BButton(BRect(box[0]+5,box[3]-50,box[2]/2-100,box[3]-5), 'CancelUserSettingsBtn',_('Cancel'),BMessage(B_QUIT_REQUESTED))
		self.AddChild(self.BtnSave,None)
		self.AddChild(self.BtnCancel,None)
		# import data from config.ini
		ent,confile=Ent_config()
		Config.read(confile)
		try:
			#check language in config
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
			myf=be_bold_font
			myf.SetSize(be_plain_font.Size())
			owner.SetFont(myf)
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
		oldsize=fon.Size()
		fon.SetSize(10)
		owner.SetFont(fon)
		BTab.DrawLabel(self,owner,frame)
		fon.SetSize(oldsize)

class FindRepTrans(BWindow):
	kWindowFrame = BRect(250, 150, 755, 317)
	# Translators: Window title
	kWindowName = _("Find/Replace translation")
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
		# Translators: Button label/action
		kButtonName1 = _("Search")
		self.SearchButton = BButton(kButtonFrame1, "Search", kButtonName1, BMessage(5348))
		self.underframe.AddChild(self.SearchButton,None)
		kButtonFrame2 = BRect(r/3+5,69,r*2/3-5,104)
		# Translators: Button label/action
		kButtonName2 = _("Replace")
		self.ReplaceButton = BButton(kButtonFrame2, "Replace", kButtonName2, BMessage(10240))#7047))
		self.underframe.AddChild(self.ReplaceButton,None)
		# Translators: Checkbox, allows/avoids case sensitive searches
		self.casesens = BCheckBox(BRect(5,79,r/2-15,104),'casesens', _('Case sensistive'), BMessage(222))
		self.casesens.SetValue(1)
		self.underframe.AddChild(self.casesens,None)
		# Translators: Field in which the user indicates the text to search for
		self.looktv=BTextControl(BRect(5,5,r-5,32),'txttosearch',_('Search:'),'',BMessage(8046))
		self.looktv.SetDivider(60.0)
		self.underframe.AddChild(self.looktv,None)
		self.looktv.MakeFocus()
		# Translators: Field to provide subtitutions
		self.reptv=BTextControl(BRect(5,37,r-5,64),'replacetxt',_('Replace:'),'',BMessage(8046))
		self.reptv.SetDivider(60.0)
		self.underframe.AddChild(self.reptv,None)
		self.pb=BStatusBar(BRect(5,b-63,r-5,b-5),"searchpb",None,None)
		self.underframe.AddChild(self.pb,None)
		lista=be_app.WindowAt(0).sourcestrings.lv
		total=lista.CountItems()
		self.pb.SetMaxValue(float(total))
		indaco=lista.CurrentSelection()
		self.pb.Update(float(indaco),None,None)
		self.ei=0
		self.ef=0
		i = 1

	def MessageReceived(self, msg):
		if msg.what == 5348:
			self.pb.Hide()
			self.pb.Show()
			if self.looktv.Text() != "":
				be_app.WindowAt(0).Lock()
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
								for ident,items in enumerate(blister.msgstrs):
									ret=find_byte(self.looktv.Text(),items)
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
								ret=find_byte(self.looktv.Text(),blister.msgstrs)
								if ret >-1:
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
									ret=find_byte(self.looktv.Text().lower(),items.lower())
									if ret >-1:
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
								ret=find_byte(self.looktv.Text().lower(),blister.msgstrs.lower())
								if ret >-1:
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
							# Translators: Search result
							say = BAlert('not_found', _('No matches found on listed entries'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
							self.alerts.append(say)
							say.Go()
				be_app.WindowAt(0).Unlock()
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
		elif msg.what == 1010:
			self.looktv.SetText(msg.FindString('txt'))
			return
		return BWindow.MessageReceived(self, msg)

class Findsource(BWindow):
	kWindowFrame = BRect(250, 150, 655, 226)
	# Translators: Window title
	kWindowName = _("Find source")
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
		be_plain_font.SetSize(14)
		h=be_plain_font.Size()
		kButtonFrame1 = BRect(r/2+15,b-40,r-5,b-5)
		# Translators: Button label/action
		kButtonName1 = _("Search")
		self.SearchButton = BButton(kButtonFrame1, "Search", kButtonName1, BMessage(5348))
		self.underframe.AddChild(self.SearchButton,None)
		# Translators: Checkbox, whether to take capitalization into account
		self.casesens = BCheckBox(BRect(5,b-30,r/2-15,b-5),'casesens', _('Case sensistive'), BMessage(222))
		self.casesens.SetValue(1)
		self.underframe.AddChild(self.casesens,None)
		# Translators: Field to provide search terms
		self.looktv=BTextControl(BRect(5,5,r-5,32),'txttosearch',_('Search:'),'',BMessage(8046))
		self.looktv.SetDivider(60.0)
		self.underframe.AddChild(self.looktv,None)
		self.looktv.MakeFocus()
		self.encoding=be_app.WindowAt(0).encoding


	def MessageReceived(self, msg):
		if msg.what == 5348:
			if self.looktv.Text() != "":
				be_app.WindowAt(0).Lock()
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
								ret=find_byte(self.looktv.Text(),item.msgids[0])
								if ret >-1:
									#highlight-fix
									scrollmsg.AddInt32("where",now)
									be_app.WindowAt(0).PostMessage(scrollmsg)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									be_app.WindowAt(0).PostMessage(messace)
									break
								ret=find_byte(self.looktv.Text(),item.msgids[1])
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
						# Translators: search result
						say = BAlert('not_found', _('No matches found on other entries'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
						self.alerts.append(say)
						say.Go()
				be_app.WindowAt(0).Unlock()
			return
		elif msg.what == 1010:
			self.looktv.SetText(msg.FindString('txt'))
			return
		return BWindow.MessageReceived(self, msg)

class POmetadata(BWindow):
	kWindowFrame = BRect(150, 150, 585, 480)
	# Translators: Window title
	kWindowName = _("PO properties")
	
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
		if msg.what == 51973:
			# save metadata to self.pofile
			ind=msg.FindString('itemstring')
			indi=msg.FindInt8('itemindex')
			self.pofile.metadata[ind]=self.listBTextControl[indi].Text()
			# ask update ordered metadata
			# save self.pofile to backup file
			smesg=BMessage(16893)
			smesg.AddInt8('savetype',2)
			smesg.AddString('bckppath',be_app.WindowAt(0).backupfile)
			be_app.WindowAt(0).PostMessage(smesg)

class MyListItem(BListItem):
	def __init__(self, txt):
		self.text = txt
		BListItem.__init__(self)
	
	def DrawItem(self, owner, frame,complete):
		self.frame = frame
		l=frame.left
		b=frame.bottom
		if self.IsSelected() or complete: 
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
		b=frame.bottom
		if self.IsSelected() or complete:
			owner.SetHighColor(200,200,200,255)
			owner.SetLowColor(200,200,200,255)
			owner.FillRect(frame)
		self.color = rgb_color()
		owner.MovePenTo(l+5,b-font_height_value.descent)
		tempcolor = rgb_color()
		if self.percent == 100:
			self.font = be_bold_font
			self.font.SetSize(be_plain_font.Size())
			tempcolor.green=200
		else:
			self.font = be_plain_font
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
		owner.MovePenTo(l+ww+10,b-2)
		owner.DrawString(self.text,None)

	def Text(self):
		return self.text

class ErrorItem(BListItem):
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
		owner.SetHighColor(20,20,20,0)
		owner.SetFont(self.font)
		owner.DrawString(self.text,None)

class GeneralSettings(BWindow):
	kWindowFrame = BRect(250, 150, 755, 297)
	# Translators: Window title
	kWindowName = _("General Settings")
	alerts=[]
	myItems=[]
	def __init__(self,oldsize):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		be_plain_font.SetSize(oldsize)
		#del self.superself
		bounds=self.Bounds()
		l=bounds.left
		t=bounds.top
		r=bounds.right
		b=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe,None)
		# Translators: Checkbox, option to check if po file matches to the user supported language
		self.langcheck = BCheckBox(BRect(5,79,r-15,104),'langcheck', _('Check language compliance between pofile and user'), BMessage(242))
		# Translators: Checkbox, option to check if file's mimetype matches the x-gettext-translation MimeType
		self.mimecheck = BCheckBox(BRect(5,109,r-15,134),'mimecheck', _("Check file's mimetype"), BMessage(262))
		# Translators: Localizations menu, list of available translations
		self.menulocaliz=BMenu(_("Localizations"))
		self.menulocaliz.SetLabelFromMarked(True)
		for y in lista_traduzioni:
			self.myItems.append(LocalizItem(y))#<fix doublefree
			self.menulocaliz.AddItem(self.myItems[-1])
		self.menuloc = BMenuField(BRect(5,5,r-5,40), 'pop0', '', self.menulocaliz,B_FOLLOW_TOP)
		self.savemocheck = BCheckBox(BRect(5,49,r-15,74),'savemocheck', _('Compile MO file on saving'), BMessage(282))
		self.underframe.AddChild(self.langcheck,None)
		self.underframe.AddChild(self.mimecheck,None)
		self.underframe.AddChild(self.menuloc,None)
		self.underframe.AddChild(self.savemocheck,None)
		ent,confile=Ent_config()
		Config.read(confile)
		try:
			#langcheck
			checklanguage = Config.getboolean('General','checklang')
			if checklanguage:
				self.langcheck.SetValue(1)
			else:
				self.langcheck.SetValue(0)
		except:
			# "gonna create checklang in config.ini"
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
			#"gonna create mimecheck in config.ini"
			cfgfile = open(confile,'w')
			Config.set('General','mimecheck', "True")
			Config.write(cfgfile)
			self.mimecheck.SetValue(1)
			cfgfile.close()
		

	def MessageReceived(self, msg):
		if msg.what == 242:
			#langcheck
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
				say = BAlert('error', _('Error enabling language compliance check, missing config section?'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 262:
			#mimecheck
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
				say = BAlert('error', _('Error enabling mimechecking, missing config section?'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 282:
			#compile mo
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.mimecheck.Value():
					Config.set('General','compilemo', "True")
					Config.write(cfgfile)
				else:
					Config.set('General','compilemo', "False")
					Config.write(cfgfile)
			except:
				say = BAlert('error', _('Error enabling mo-file compilation, missing config section?'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 600:
			value=msg.FindString("name")
			if value!="" and value!=None:
				ent,confile=Ent_config()
				cfgfile = open(confile,'w')
				try:
					Config.set('General','localization', value)
					Config.write(cfgfile)
					say = BAlert('restart', _('Restart required to apply changes.'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_INFO_ALERT)
					self.alerts.append(say)
					say.Go()
				except:
					say = BAlert('error', _('Error setting the localization, missing config section?'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
					self.alerts.append(say)
					say.Go()
				cfgfile.close()
			return
		BWindow.MessageReceived(self, msg)
class TMSettings(BWindow):
	kWindowFrame = BRect(250, 150, 755, 240)
	# Translators: Window title
	kWindowName = _("Translation Memory Settings")
	alerts=[]
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l=bounds.left
		t=bounds.top
		r=bounds.right
		b=bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		h=be_plain_font.Size()
		self.AddChild(self.underframe,None)
		self.enablecheck = BCheckBox(cstep(0,r,h),'enabcheck', _('Enable/Disable translation memory'), BMessage(222))
		if tm:
			self.enablecheck.SetValue(1)
		else:
			self.enablecheck.SetValue(0)
		ent,confile=Ent_config()
		Config.read(confile)
		
		self.builtinsrv = BCheckBox(cstep(1,r,h),'builtin_srv', _('Enable/Disable TM local server'), BMessage(333))
		try:
			bret = Config.getboolean('TMSettings','builtinsrv')
		except:
			cfgfile = open(confile,'w')
			try:
				Config.add_section('TMSettings')
			except:
				pass
			Config.set('TMSettings','builtinsrv',"False")
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			bret = False
		if bret:
			self.builtinsrv.SetValue(1)
		else:
			self.builtinsrv.SetValue(0)
			
		try:
			bret = ConfigSectionMap("TMSettings")['tmxsrv']
		except:
			cfgfile = open(confile,'w')
			Config.set('TMSettings','tmxsrv',"127.0.0.1")
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			bret = "127.0.0.1"
		self.tmxsrvBTC = BTextControl(cstep(2,r,h),'tmxsrv',_('Server address:'),bret,BMessage(8080))	
		try:
			bret = ConfigSectionMap("TMSettings")['tmxprt']
		except:
			cfgfile = open(confile,'w')
			Config.set('TMSettings','tmxprt',"2022")
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			bret = "2022"
		self.tmxprtBTC = BTextControl(cstep(3,r,h),'tmxprt',_('Server port:'),bret,BMessage(8086))
		try:
			bret = ConfigSectionMap("TMSettings")['header']
		except:
			cfgfile = open(confile,'w')
			Config.set('TMSettings','header',"4096")
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			bret = "2022"
		self.headerBTC = BTextControl(cstep(4,r,h),'header_btc',_('Header size:'),bret,BMessage(8088))
		self.logsrv = BCheckBox(cstep(5,r,h),'log_srv', _('Enable/Disable local server log'), BMessage(444))
		try:
			bret = Config.getboolean('TMSettings','logsrv')
		except:
			cfgfile = open(confile,'w')
			Config.set('TMSettings','logsrv',"False")
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			bret = False
		if bret:
			self.logsrv.SetValue(1)
		else:
			self.logsrv.SetValue(0)
		lastr=cstep(6,r,h)
		self.underframe.ResizeTo(r,lastr.bottom)
		self.ResizeTo(r,lastr.bottom)
		self.underframe.AddChild(self.enablecheck,None)
		self.underframe.AddChild(self.builtinsrv,None)
		self.underframe.AddChild(self.tmxsrvBTC,None)
		self.underframe.AddChild(self.tmxprtBTC,None)
		self.underframe.AddChild(self.headerBTC,None)
		self.underframe.AddChild(self.logsrv,None)
		
	
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
				say = BAlert('error', _('Error writing tm setting in config.ini, missing config section?'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 333:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.builtinsrv.Value():
					Config.set('TMSettings','builtinsrv', "True")
					Config.write(cfgfile)
					#restart app
				else:
					Config.set('TMSettings','builtinsrv', "False")
					Config.write(cfgfile)
					#restart app
			except:
				say = BAlert('error', _('Error writing builtinsrv setting in config.ini, missing config section?'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 444:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.logsrv.Value():
					Config.set('TMSettings','logsrv', "True")
					Config.write(cfgfile)
					#restart app
				else:
					Config.set('TMSettings','logsrv', "False")
					Config.write(cfgfile)
					#restart app
			except:
				say = BAlert('error', _('Error writing logsrv setting in config.ini, missing config section?'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 8080:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				Config.set("TMSettings",'tmxsrv',self.tmxsrvBTC.Text())
				Config.write(cfgfile)
				tmxsrv=self.tmxsrvBTC.Text()
			except:
				say = BAlert('error', _('Cannot save TM server address'), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 8086:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				tmxprt=int(self.tmxprtBTC.Text())
				Config.set("TMSettings",'tmxprt',self.tmxprtBTC.Text())
				Config.write(cfgfile)
			except:
				str1=_("Cannot save TM server port. Port value:")
				str2=self.tmxprtBTC.Text()
				say = BAlert('error', " ".join((str1,str2)), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 8088:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				tmxprt=int(self.headerBTC.Text())
				Config.set("TMSettings",'header',self.headerBTC.Text())
				Config.write(cfgfile)
			except:
				str1=_("Cannot save header size. Header value:")
				str2=self.tmxprtBTC.Text()
				say = BAlert('error', " ".join((str1,str2)), _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		BWindow.MessageReceived(self, msg)

class TransEngine(BMenuItem):
	def __init__(self,name):
		self.name=name
		msg=BMessage(600)
		msg.AddString("name",self.name)
		BMenuItem.__init__(self,self.name,msg,self.name[0],0)
		if self.name != "GoogleTranslator":
			self.SetEnabled(False)

class TranslatorSourceLang(BMenuItem):
	def __init__(self,name,code):
		self.name=name
		self.code=code
		msg=BMessage(800)
		msg.AddString("name",self.name)
		msg.AddString("code",self.code)
		BMenuItem.__init__(self,self.name,msg,'\x00',0)
class TranslatorTargetLang(BMenuItem):
	def __init__(self,name,code):
		self.name=name
		self.code=code
		msg=BMessage(900)
		msg.AddString("name",self.name)
		msg.AddString("code",self.code)
		BMenuItem.__init__(self,self.name,msg,'\x00',0)

class SpellcheckSettings(BWindow):
	kWindowFrame = BRect(250, 150, 755, 297)
	# Translators: Window title
	kWindowName = _("Spellchecking Settings")
	alerts=[]
	motori=["GoogleTranslator",
			"ChatGptTranslator",
			"MicrosoftTranslator",
			"PonsTranslator",
			"LingueeTranslator",
			"MyMemoryTranslator",
			"YandexTranslator",
			"PapagoTranslator",
			"DeeplTranslator",
			"QcriTranslator"]
	def __init__(self,showspell,oldsize):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		bounds=self.Bounds()
		l = bounds.left
		t = bounds.top
		r = bounds.right
		b = bounds.bottom
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		h=be_plain_font.Size()
		self.AddChild(self.underframe,None)
		ent,confile=Ent_config()
		self.enablecheck = BCheckBox(cstep(0,r,h),'enabcheck', _('Enable/Disable spellcheck'), BMessage(222))
		
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
			self.diz = BTextControl(cstep(1,r,h),'dictionary',_('Dictionary path:'),bret,BMessage(8086))
			self.underframe.AddChild(self.diz,None)
			try:
				bret = ConfigSectionMap("Translator")['spell_inclusion']
			except:
				bret = ""
			# Translators: the spellchecker will include these special chars within words
			self.inclus = BTextControl(cstep(2,r,h),'inclusion',_('Chars included in words:'),bret,BMessage(8087))
			self.underframe.AddChild(self.inclus,None)
			try:
				bret = ConfigSectionMap("Translator")['spell_esclusion']
			except:
				bret = "Pc,Pd,Pe,Pi,Po,Ps,Cc,Pf"
			# Translators: Categories in unicode to exclude from spellceck. Look at https://en.wikipedia.org/wiki/Template:General_Category_(Unicode)
			self.esclus = BTextControl(cstep(3,r,h),'inclusion',_('Chars-categories excluded in words:'),bret,BMessage(8088))
			self.underframe.AddChild(self.esclus,None)
			self.es_enabler=BCheckBox(cstep(8,r,h),'es_enabler', _('Enable/Disable external translator'), BMessage(333))
			if ext_sup:
				self.es_enabler.SetValue(1)
			else:
				self.es_enabler.SetValue(0)
			self.underframe.AddChild(self.es_enabler,None)
			try:
				bret = ConfigSectionMap("Translator")['engine']
			except:
				bret = ""
			self.menu=BMenu("Translator Engine")
			self.menu.SetLabelFromMarked(True)
			for z in self.motori:
				itm=TransEngine(z)
				if itm.name==bret:
					itm.SetMarked(True)
				self.menu.AddItem(itm)
			labell= _('Translator engine:')
			self.te_bar = BMenuField(cstep(9,r,h), 'pop1',labell, self.menu,B_FOLLOW_TOP)
			self.te_bar.SetDivider(self.underframe.StringWidth(labell))
			self.underframe.AddChild(self.te_bar,None)
		topr=cstep(4,r,h)
		botr=cstep(7,r,h)
		fusionr=BRect(topr.left,topr.top+10,botr.right,botr.bottom+10)
		del topr
		del botr
		innerfusion=BRect(0,0,fusionr.Width(),fusionr.Height())
		innerfusion.InsetBy(5,5)
		
		self.getcat=CategoryTextView(fusionr,"Category_TextView",innerfusion,B_FOLLOW_ALL_SIDES,B_WILL_DRAW|B_FRAME_EVENTS)
		
		self.ResizeTo(r,cstep(10,r,h).bottom)
		self.underframe.AddChild(self.enablecheck,None)
		self.underframe.AddChild(self.getcat,None)

	def MessageReceived(self, msg):
		if msg.what == 222:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.enablecheck.Value():
					Config.set('General','spellchecking', "True")
					Config.write(cfgfile)
					ext_sup=True
				else:
					Config.set('General','spellchecking', "False")
					Config.write(cfgfile)
					ext_sup=False
			except:
				say = BAlert("error_enable_spellcheck", _("Error enabling spellcheck, check config.ini"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			return
		elif msg.what == 333:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				if self.es_enabler.Value():
					ext_sup=True
					if not Config.has_section('Translator'):
						Config.add_section('Translator')						
					Config.set('Translator','es_enabled', "True")
					Config.write(cfgfile)
				else:
					ext_sup=False
					if not Config.has_section('Translator'):
						Config.add_section('Translator')	
					Config.set('Translator','es_enabled', "False")
					Config.write(cfgfile)
			except:
				say = BAlert("error_enable_ext_support", _("Error enabling external translator, check config.ini"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			Config.read(confile)
			return
		elif msg.what == 600:
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			try:
				name=msg.FindString("name")
				if not Config.has_section('Translator'):
					Config.add_section('Translator')	
				engine=name
				Config.set('Translator','engine', name)
				Config.write(cfgfile)
			except:
				say = BAlert("error_engine_selection", _("Error selecting the translator engine, check config.ini"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			Config.read(confile)
			return
		elif msg.what == 8086:
			confent,confile=Ent_config()
			ent=BEntry(self.diz.Text()+".dic")
			if ent.Exists():
				Config.read(confile)
				cfgfile = open(confile,'w')
				try:
					if not Config.has_section('Translator'):
						Config.add_section('Translator')	
					Config.set("Translator",'spell_dictionary',self.diz.Text())
				except:
					say = BAlert("error_name_path", _("Cannot save dictionary name path"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
					self.alerts.append(say)
					say.Go()
				Config.write(cfgfile)
				cfgfile.close()
			else:
				# Translators: example: With /boot/system/data/hunspell/fur_IT, could not find /boot/system/data/hunspell/fur_IT.dic
				txtos1=_("With ")
				# Translators: example: With /boot/system/data/hunspell/fur_IT, could not find /boot/system/data/hunspell/fur_IT.dic
				txtos2=_(", could not find ")
				ttsf="".Join((txtos1,self.diz.Text(),txtos2,self.diz.Text(),".dic"))
				say = BAlert("error_dic_path", ttsf, 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
				self.alerts.append(say)
				say.Go()
				return
		elif msg.what == 8087:
			confent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				if not Config.has_section('Translator'):
					Config.add_section('Translator')	
				Config.set("Translator",'spell_inclusion',self.inclus.Text())
				Config.write(cfgfile)
			except:
				say = BAlert("error_saving_inclusion", _("Cannot save inclusion chars"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			Config.read(confile)
			inctxt=ConfigSectionMap("Translator")['spell_inclusion']
			inclusion = inctxt.split(",")
			return
		elif msg.what == 8088:
			confent,confile=Ent_config()
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				if not Config.has_section('Translator'):
					Config.add_section('Translator')	
				Config.set("Translator",'spell_esclusion',self.esclus.Text())
				Config.write(cfgfile)
			except:
				say = BAlert("error_saving_inclusion", _("Cannot save esclusion char categories"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
				self.alerts.append(say)
				say.Go()
			cfgfile.close()
			Config.read(confile)
			esctxt=ConfigSectionMap("Translator")['spell_esclusion']
			esclusion=esctxt.split(",")
			return
		BWindow.MessageReceived(self, msg)

class HeaderWindow(BWindow):
	kWindowFrame = BRect(150, 150, 500, 600)
	# Translators: Window title
	kWindowName = _("Po header")
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
		# Translators: Button label/action
		kButtonName = "Save header"
		self.savebtn = BButton(kButtonFrame, "Save header", kButtonName, BMessage(5252))
		self.underframe.AddChild(self.savebtn,None)
		self.pofile=pofile
		if self.pofile.header!="":
			self.headerview.SetText(self.pofile.header,None)

	def Save(self):
		bckpmsg=BMessage(16893)
		bckpmsg.AddInt8('savetype',4)
		bckpmsg.AddString('header',self.headerview.Text())
		bckpmsg.AddString('bckppath',self.backupfile)
		be_app.WindowAt(0).PostMessage(bckpmsg)

	def MessageReceived(self, msg):
		if msg.what == 5252:
			self.Save()
			self.Quit()
		else:
			return BWindow.MessageReceived(self, msg)
class RedrawingScrollBar(BScrollBar):
	def __init__(self,superself,rect,name,taget,min,max,orientation):
		self.superself=superself
		BScrollBar.__init__(self,rect,name,taget,min,max,orientation)
	def ValueChanged(self,newValue):
		if self.superself.photoframe:
			self.superself.photoframe.Invalidate()
		BScrollBar.ValueChanged(self,newValue)
class AboutWindow(BWindow):
	kWindowFrame = BRect(50, 50, 600, 730)
	kButtonFrame = BRect(kWindowFrame.right-205,kWindowFrame.bottom-89,kWindowFrame.right-54,kWindowFrame.bottom-54)
	kWindowName = "About"
	# Translators: Button label/action
	kButtonName = "Close"
	BUTTON_MSG = struct.unpack('!l', b'PRES')[0]
	alerts=[]
	def __init__(self):							
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, window_type.B_MODAL_WINDOW, B_NOT_RESIZABLE)
		brec=self.Bounds()
		bpf=be_plain_font
		bpf.SetSize(16)
		bbf=be_bold_font
		bbf.SetSize(16)
		self.bbox=BBox(brec, 'underbox', B_FOLLOW_ALL_SIDES, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.bbox,None)
		self.CloseButton = BButton(self.kButtonFrame, self.kButtonName, self.kButtonName, BMessage(self.BUTTON_MSG))
		cise=BRect(4,4,brec.right-18,brec.bottom-44)
		cjamput=BRect(4,0,brec.right-24,brec.bottom-48)
		self.messagjio= BTextView(cise, 'TxTView', cjamput, B_FOLLOW_ALL_SIDES, B_WILL_DRAW)
		self.messagjio.SetStylable(1)
		self.messagjio.MakeSelectable(0)
		self.messagjio.MakeEditable(0)
		self.scrollbr=RedrawingScrollBar(self,BRect(brec.right-18,0,brec.right,brec.bottom-44),'TxTView_ScrollBar',self.messagjio,0.0,0.0,B_VERTICAL)
		titul=_("Po editor for Haiku")
		txtver=_("version ")
		bytxt=_("by Fabio Tomat")
		imail=_("e-mail:")
		license1=_("MIT LICENSE")
		license2=_("\nCopyright © 2025 Fabio Tomat\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.")
		license3=_("\n\nTHE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")
		stuff = "".join(("\n\t\t\t\t\t\t\t\t\t",appname,"\n\n\t\t\t\t\t\t\t\t\t\t\t\t",titul,"\n\t\t\t\t\t\t\t\t\t\t\t\t",txtver,ver," ",state,"\n\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\t",bytxt,"\n\t\t\t\t\t\t\t\t\t\t\t\t",imail,"\n\t\t\t\t\t\t\t\t\t\t\t\tf.t.public@gmail.com\n\n\n\n\n\n",license1,license2,license3))
		#stuff = '\n\t\t\t\t\t\t\t\t\t'+appname+'\n\n\t\t\t\t\t\t\t\t\t\t\t\tPo editor for Haiku\n\t\t\t\t\t\t\t\t\t\t\t\tversion '+ver+' '+state+'\n\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\tby Fabio Tomat\n\t\t\t\t\t\t\t\t\t\t\t\te-mail:\n\t\t\t\t\t\t\t\t\t\t\t\tf.t.public@gmail.com\n\n\n\n\n\n\nMIT LICENSE\nCopyright © 2024 Fabio Tomat\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'
		n = stuff.find(appname)
		m = stuff.find(license1)
		i=0
		itr=text_run()
		itr.font=bpf
		command=[itr]
		for char in appname:
			btr=text_run()
			btr.offset=n+i
			btr.font=bbf
			tcol=rgb_color()
			tcol.red=230-i*40
			tcol.green=50+i*50
			tcol.blue=20+i*40
			btr.color=tcol
			command.append(btr)
			i+=1
		ndtr=text_run()
		ndtr.offset=find_byte(titul,stuff)#"Po editor for Haiku"
		ndtr.font=bbf
		gcol=rgb_color()
		gcol.red=170
		gcol.green=130
		gcol.blue=170
		ndtr.color=gcol
		command.append(ndtr)
		nbtr=text_run()
		nbtr.font=bbf
		nbtr.offset=m
		ngcol=rgb_color()
		ngcol.red=100
		ngcol.green=100
		ngcol.blue=100
		nbtr.color=ngcol
		command.append(nbtr)
		ntr2=text_run()
		ntr2.font=bpf
		ntr2.offset=m+11
		ntr2.color=ngcol
		command.append(ntr2)
		self.messagjio.SetText(stuff, command)
		self.bbox.AddChild(self.messagjio,None)
		self.bbox.AddChild(self.scrollbr,None)
		self.bbox.AddChild(self.CloseButton,None)
		self.CloseButton.MakeFocus(1)
		b,p=lookfdata("HaiPO.png")
		if b:
			if self.show_img(p):
				pass
			else:
				say = BAlert("error_logo", _("something went wrong loading the logo"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
				self.alerts.append(say)
				say.Go()
		else:
			say = BAlert("error_logo", _("no logo found"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
			self.alerts.append(say)
			say.Go()

	def show_img(self,link):
		perc=BPath()
		ent=BEntry(link)
		if ent.Exists():
			ent.GetPath(perc)
			self.img=BTranslationUtils.GetBitmap(perc.Path(),None)
			self.photoframe=PView(BRect(40,50,255,255),"photoframe",self.img)
			self.bbox.AddChild(self.photoframe,None)
			return True
		else:
			return False
	def MessageReceived(self, msg):
		if msg.what == self.BUTTON_MSG:
			self.Quit()
		else:
			BWindow.MessageReceived(self, msg)

class BaOButton(BButton):
	def __init__(self,frame,name,label,message):
		self.iso=""
		self.langname=""
		self.name=label
		BButton.__init__(self,frame,name,label,message,B_FOLLOW_LEFT | B_FOLLOW_BOTTOM,B_WILL_DRAW | B_NAVIGABLE)

class LangMenuItem(BMenuItem):
	def __init__(self,cubie):
		self.name=cubie[0]
		self.code=cubie[1]
		msg=BMessage(707)
		msg.AddString("code",self.code)
		msg.AddString("name",self.name)
		BMenuItem.__init__(self,self.name,msg,self.name[0],0)
class CharsetMenuItem(BMenuItem):
	def __init__(self,name):
		self.name=name
		msg=BMessage(777)
		msg.AddString("name",self.name)
		BMenuItem.__init__(self,self.name,msg,self.name[0],0)
class POTchooser(BWindow):
	charset="UTF-8"
	setchrset=False
	setlang=False
	alerts=[]
	def __init__(self,potfile,langlist,oldsize):
		a=display_mode()
		BScreen().GetMode(a)
		w=a.virtual_width
		h=a.virtual_height
		fon=BFont()
		BWindow.__init__(self, BRect(w/2-200, h/2-100, w/2+200, h/2+100),"Choose your destiny...",window_type.B_FLOATING_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		self.bckgnd = BView(self.Bounds(), "bckgnd_View", 8, 20000000)
		self.AddChild(self.bckgnd,None)
		bounds=self.Bounds()
		r = bounds.right
		h = fon.Size()
		self.langmenu=BMenu("Language")
		self.langmenu.SetLabelFromMarked(True)
		for y in langlist:
			self.langmenu.AddItem(LangMenuItem(y))
		# Translators: language selector menu label
		mnlab=_('Build PO with this language:')
		self.langmenufield = BMenuField(cstep(1,r,h), 'pop0', mnlab, self.langmenu,B_FOLLOW_TOP)
		self.langmenufield.SetDivider(fon.StringWidth(mnlab+" "))
		self.bckgnd.AddChild(self.langmenufield,None)
		# Translators: Button label/action
		self.baobtn=BaOButton(cstep(5,r,h),"build_and_open_btn", _("Build and open"), BMessage(5252))
		self.baobtn.SetEnabled(False)
		self.bckgnd.AddChild(self.baobtn,None)
		
		self.potfile=potfile
		self.new_dict = {}
		b,pth=lookfdata('plural_forms.txt')
		if b:
			with open(pth, 'r') as infile:
				for line in infile:
					spline=line.split('#')
					plural=spline[0]
					splingue=spline[1].split('/')
					for lingua in splingue:
						self.new_dict[lingua]=plural
		else:
			say = BAlert("error_plurals", _("no plurals file found"), 'Ok',None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
			self.alerts.append(say)
			say.Go()
		po_supported_charsets = [
    'utf-8',
    'iso-8859-1', 'iso-8859-2', 'iso-8859-3', 'iso-8859-4', 'iso-8859-5',
    'iso-8859-6', 'iso-8859-7', 'iso-8859-8', 'iso-8859-9', 'iso-8859-10',
    'iso-8859-13', 'iso-8859-14', 'iso-8859-15',
    'koi8-r', 'koi8-u',
    'windows-1250', 'windows-1251', 'windows-1252', 'windows-1253',
    'windows-1254', 'windows-1255', 'windows-1256', 'windows-1257',
    'ascii',
    'big5',
    'gb2312',
    'euc-jp', 'shift_jis',
    'euc-kr',
]
		text_codec_list = sorted(po_supported_charsets)
		self.charsetmenu=BMenu("Charset")
		self.charsetmenu.SetLabelFromMarked(True)
		for y in text_codec_list:
			self.charsetmenu.AddItem(CharsetMenuItem(y))
		mflab=_('Charset encoding:')
		self.charsetmenufield = BMenuField(cstep(3,r,h), 'pop0', mflab, self.charsetmenu,B_FOLLOW_BOTTOM)
		self.charsetmenufield.SetDivider(fon.StringWidth(mflab+" "))
		self.bckgnd.AddChild(self.charsetmenufield,None)
		self.ResizeTo(r,cstep(6,r,h).bottom)

	def MessageReceived(self, msg):
		if msg.what == 707:
			self.baobtn.iso=msg.FindString('code')
			self.baobtn.langname=msg.FindString('name')
			self.baobtn.SetLabel(self.baobtn.name+" for "+self.baobtn.langname)
			self.setlang=True
			if self.setchrset:
				self.baobtn.SetEnabled(True)
		elif msg.what == 777:
			self.charset = msg.FindString("name")
			self.setchrset=True
			if self.setlang:
				self.baobtn.SetEnabled(True)
		elif msg.what == 5252:
			#before starting retrieve Plural-Forms
			pot = polib.pofile(self.potfile)
			potname,potextension=os.path.splitext(self.potfile)
			target_language = self.baobtn.iso
			po = polib.POFile()
			po.metadata = pot.metadata.copy()
			po.metadata['Language'] = target_language
			nplurrule_txt = self.new_dict[self.baobtn.iso]#'nplurals=2; plural=(n != 1);' 
			po.metadata['Plural-Forms'] = nplurrule_txt
			nplur_txt=nplurrule_txt[:nplurrule_txt.find(';')]
			
			nplur=nplur_txt[nplur_txt.find('=')+1:]
			
			for entry in pot:
				new_entry_data = {
					'msgid': entry.msgid,
				}
				pl=False
				if entry.msgid_plural:
					pl=True
				for field in ['msgctxt', 'msgid_plural', 'flags', 'occurrences', 'comment', 'tcomment', 
							  'previous_msgctxt', 'previous_msgid', 'previous_msgid_plural', 'linenum']:
					if hasattr(entry, field):
						new_entry_data[field] = getattr(entry, field)
				#to create a plural msgstr you should pass msgstr_plural, but its value should not be a list ["",""...]
				#it should be a dict {int:str} as these comments indicates:
				#https://github.com/python/typeshed/pull/11273
				if pl:
					dic={}
					i=0
					while i<int(nplur):
						dic[i]=""
						i+=1
					new_entry_data["msgstr_plural"]=dic
				new_entry = polib.POEntry(**new_entry_data)
				po.append(new_entry)
			po.header=pot.header
			ent,confile=Ent_config()
			if ent.Exists():
				Config.read(confile)
				try:
					namo=ConfigSectionMap("Translator")['name']
					defname=namo+' <'+ConfigSectionMap("Translator")['mail']+'>'
					po.metadata['Last-Translator']=defname
					grp=ConfigSectionMap("Translator")['team']+' <'+ConfigSectionMap("Translator")['ltmail']+'>'
					po.metadata['Language-Team']=grp
				except:
					#keep those in pot file
					pass
			now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
			po.metadata['PO-Revision-Date']=now
			try:
				codecs.lookup(self.charset)
			except:
				self.charset="UTF-8"
			po.metadata['Content-Type']=f'text/plain; charset={self.charset}'
			po.metadata['X-Generator']=version
			filename=f'{potname}.{target_language}.po'
			po.save(filename)
			mxg=BMessage(45371)
			mxg.AddString('path',filename)
			be_app.WindowAt(0).PostMessage(mxg)
			self.Quit()
		BWindow.MessageReceived(self,msg)

class MainWindow(BWindow):
	alerts=[]
	sugjs=[]
	badItems=[]
	#winset=[]
	filen=""
	file_ext=""
	viewtxt=_('View')
	fuztxt=_('Fuzzy')
	unttxt=_('Untranslated')
	tratxt=_('Translated')
	obstxt=_('Obsolete')
	transmnu=_('Translation')
	cpfrsr= _('Copy from source (ctrl+shift+s)')
	Menus = (
		(_('File'), ((295485, _('Open')), (2, _('Save')), (1, _('Close')), (5, _('Save as...')),(None, None),(B_QUIT_REQUESTED, _('Quit')))),
		(transmnu, ((3, cpfrsr), (53,_('Edit comment')), (70,_('Done and next')), (71,_('Mark/Unmark fuzzy (ctrl+b)')), (72, _('Previous w/o saving')),(73,_('Next w/o saving')),(None, None),(42, _('Po properties')), (43, _('Po header')),(None, None),(14183, _('Compile mo file')),(None, None), (6, _('Find source')), (7, _('Find/Replace translation')))),
		(viewtxt, ((74,fuztxt), (75, unttxt),(76,tratxt),(77, obstxt))),
		(_('Settings'), ((40, _('General')),(41, _('User settings')), (44, _('Spellcheck')), (45,_('Translation Memory')))),
		(_('About'), ((8, _('Help')),(None, None),(9,_('About'))))
		)

	def __init__(self,arg):
		BWindow.__init__(self, BRect(6,64,1024,768), " ".join([appname,ver]), window_type.B_TITLED_WINDOW, B_QUIT_ON_WINDOW_CLOSE)
		okeys=[B_NUM_LOCK,B_SCROLL_LOCK,B_LEFT_COMMAND_KEY+B_COMMAND_KEY,B_OPTION_KEY+B_LEFT_OPTION_KEY,B_OPTION_KEY+B_RIGHT_OPTION_KEY,B_CAPS_LOCK]
		self.combination_ok=[]
		for r in range(1,len(okeys)+1):
			for combo in combinations(okeys,r):
				self.combination_ok.append(sum(combo,0))
		shiftil=[B_LEFT_SHIFT_KEY]
		for k in self.combination_ok:
			shiftil.append(B_LEFT_SHIFT_KEY|k)
		shiftir=[B_RIGHT_SHIFT_KEY]
		for k in self.combination_ok:
			shiftil.append(B_RIGHT_SHIFT_KEY|k)
		self.shifti = shiftil+shiftir
		self.skipcheck=False
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
		global tm,tmxsrv,tmxprt,tmsocket,showspell,comm,esclusion,inclusion,ext_sup,engine
		showspell = False
		if ent.Exists():
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
						log_srv = False
						Config.write(cfgfile)
						cfgfile.close()
					try:
						langs=ConfigSectionMap("Translator")['langs']
						self.tmxlang=langs.split(',')[0]
					except:
						builtin_srv=False
					if builtin_srv:
						self.builtin_srv=[True,tmxsrv,tmxprt,header,log_srv]
					else:
						self.builtin_srv=[False,tmxsrv,tmxprt,header,log_srv]
				else:
					self.builtin_srv=[False,tmxsrv,tmxprt,4096,False]
			except:
				cfgfile = open(confile,'w')
				try:
					Config.add_section("General")
				except:
					pass
				Config.set('General','tm', 'False')
				Config.write(cfgfile)
				cfgfile.close()
				tm=False
				tmxsrv = '127.0.0.1'
				tmxprt = 2022
				self.builtin_srv=[False,tmxsrv,tmxprt,4096,False]
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
			Config.set('General','tm', 'False')
			Config.set('General','modifierkey',"4100")
			Config.set('General','spellchecking', 'False')
			tm=False
			self.modifiervalue=4100
			setspellcheck=False
			Config.add_section('Listing')
			Config.set('Listing','Fuzzy',"True")
			Config.set('Listing','Untranslated',"True")
			Config.set('Listing','Translated',"True")
			Config.set('Listing','Obsolete',"False")
			Config.add_section("TMSettings")
			Config.set("TMSettings",'tmxsrv', '127.0.0.1')
			tmxsrv = '127.0.0.1'
			Config.set("TMSettings",'tmxprt', "2022")
			tmxprt = 2022
			Config.set("TMSettings",'builtinsrv', "False")
			builtin_srv = False
			Config.set("TMSettings",'header', "4096")
			header = 4096
			Config.set("TMSettings",'logSrv', "False")
			log_srv = False
			Config.write(cfgfile)
			cfgfile.close()
			Config.read(confile)
			self.poview[0]=Config.getboolean('Listing', 'Fuzzy')
			self.poview[1]=Config.getboolean('Listing', 'Untranslated')
			self.poview[2]=Config.getboolean('Listing', 'Translated')
			self.poview[3]=Config.getboolean('Listing', 'Obsolete')
			setspellcheck=False
			self.builtin_srv=[False,tmxsrv,tmxprt,4096,False]
		
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
				try:
					Config.read(confile)
					ext_sup=Config.getboolean('Translator', 'es_enabled')
				except:
					cfgfile = open(confile,'w')
					Config.set('Translator','es_enabled', 'False')
					Config.write(cfgfile)
					cfgfile.close()
					Config.read(confile)
					ext_sup=False
				try:
					engine=ConfigSectionMap("Translator")['engine']
					self.src_lang=ConfigSectionMap("Translator")['src_lang']
					self.trans_lang=ConfigSectionMap("Translator")['trans_lang']
				except:
					cfgfile = open(confile,'w')
					Config.set('Translator','engine', 'GoogleTranslator')
					Config.set('Translator','src_lang', 'en')
					Config.set('Translator','trans_lang', 'it')
					Config.write(cfgfile)
					cfgfile.close()
					Config.read(confile)
					engine='GoogleTranslator'
					self.src_lang="en"
					self.trans_lang="it"
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
				try:
					self.spellchecker = enchant.Dict(filename) # check initialization (correctly loading dictionary)
				except:
					showspell=False
					cfgfile = open(confile,'w')
					Config.set('General','spellchecking', 'False')
					Config.write(cfgfile)
					cfgfile.close()
					Config.read(confile)
			else:
				showspell=False
				say = BAlert('Warn', _('Your dictionary cannot be found, disabling spell check...'), _('Ooook'), None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				say.Go()
		else:
			showspell=False
			spelldict="/system/data/hunspell/en_US"
			inclusion = []
			esclusion = ["Pc","Pd","Pe","Pi","Po","Ps","Cc","Pf"]
			ext_sup=False
			engine='GoogleTranslator'
			self.src_lang="en"
			self.trans_lang="it"
		self.curtain=False
		

		self.steps=['˹','   ˺','   ˼','˻']
		self.indsteps=0
		self.ofp=BFilePanel(B_OPEN_PANEL,None,None,node_flavor.B_ANY_NODE,True, None, None, True, True)
		osdir="/boot/home"
		self.ofp.SetPanelDirectory(osdir)
		self.bar = BMenuBar(bckgnd_bounds, 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		self.viewarr = []		
		for menu, items in self.Menus:
			if menu == self.viewtxt:#"View":
				savemenu=True
			else:
				savemenu=False
			if menu == self.transmnu:
				menu = BMenu(menu)
				menu.SetEnabled(False)
			else:
				menu = BMenu(menu)
				
			for k, name in items:
				if k is None:
						menu.AddItem(BSeparatorItem())
				else:
						menuitem=BMenuItem(name, BMessage(k), '\x00',0)
						#in base a Settings
						if name == self.fuztxt:#"Fuzzy":
							menuitem.SetMarked(self.poview[0])
						elif name == self.unttxt:#"Untranslated":
							menuitem.SetMarked(self.poview[1])
						elif name == self.tratxt:#"Translated":
							menuitem.SetMarked(self.poview[2])
						elif name == self.obstxt:#"Obsolete":
							menuitem.SetMarked(self.poview[3])
						self.viewarr.append(menuitem)
						menu.AddItem(menuitem)
			if savemenu:
				self.savemenu = menu
				self.bar.AddItem(self.savemenu)
			else:
				self.bar.AddItem(menu)
		
		self.upperbox = BBox(BRect(0,barheight+2,bckgnd_bounds.Width(),bckgnd_bounds.Height()/2-1),"Under_upperbox",B_FOLLOW_TOP,border_style.B_FANCY_BORDER)
		self.lowerbox = BBox(BRect(0,bckgnd_bounds.Height()/2+1,bckgnd_bounds.Width()*2/3,bckgnd_bounds.Height()),"Under_lowerbox",B_FOLLOW_BOTTOM,border_style.B_FANCY_BORDER)
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
		self.sourcebox=srctabbox(self,tabrc,'msgid',altece)
		self.listemsgid.append(self.sourcebox)
		self.srctablabels.append(BTab(None))
		self.srctabview.AddTab(self.listemsgid[0], self.srctablabels[0])
		self.transbox=trnsltabbox(tabrc2,'msgstr',self)
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
		self.upperbox.AddChild(self.sourcestrings.sv,None)
		
		self.tmscrollsugj=ScrollSugj(BRect(self.upperbox.Bounds().right*2/3+4,4,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom/2), 'ScrollSugj')
		splchkstat=_("Spellchecker status:")
		statsplchkr=_(" disabled")
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
			self.spellabel= BStringView(rectspellab,"spellabel",splchkstat,B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM)
			self.spellabel.SetFont(self.font)
			self.upperbox.AddChild(self.spellabel,None)
			self.upperbox.AddChild(self.checkres,None)
		else:
			fo=BFont()
			self.upperbox.GetFont(fo)
			l=fo.StringWidth(splchkstat+statsplchkr)
			rectspellab=BRect(self.upperbox.Bounds().right-l-4,self.upperbox.Bounds().bottom-55,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom-4)
			self.spellabel= BStringView(rectspellab,"spellabel",splchkstat+statsplchkr,B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM)
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
		self.expander = srcTextView(self,rectcksp,"checkres",insetcksp,B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM,B_WILL_DRAW|B_FRAME_EVENTS)
		self.expander.MakeEditable(0)
		self.upperbox.AddChild(self.expander,None)
		myFont=BFont()
		myFont.SetSize(self.oldsize)
		if self.builtin_srv[0]:
			txt=_("TM server status: alive")
		else:
			txt=_("TM server status: not running")
		l=myFont.StringWidth(txt)
		self.TM_srv_status=BStringView(BRect(self.upperbox.Bounds().right*2/3+4,self.upperbox.Bounds().bottom-58,self.upperbox.Bounds().right*2/3+l+4,self.upperbox.Bounds().bottom-56+myFont.Size()),"tm_srv_status",txt,B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM)
		self.TM_srv_status.SetFont(myFont)
		self.upperbox.AddChild(self.TM_srv_status,None)
		
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
		self.valueln=BStringView(BRect(self.infobox.Bounds().right-x-5,self.infobox.Bounds().bottom-fon.Size()-10,self.infobox.Bounds().right-5,self.infobox.Bounds().bottom-5),"value_ln_num",None)
		lntxt=_("Line number:")
		w=fon.StringWidth(lntxt)
		self.infoln=BStringView(BRect(5,self.infobox.Bounds().bottom-fon.Size()-10,5+w,self.infobox.Bounds().bottom-5),"line_number",lntxt)
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
			self.msgstablabels.append(infoTab(None))
		i=0
		while i < len(self.listemsgs):
			self.msgstabview.AddTab(self.listemsgs[i], self.msgstablabels[i])
			i+=1
		
		self.msgstabview.SetTabSide(tab_side.kBottomSide)
		self.infobox.AddChild(self.msgstabview,None)
		self.msgstabview.Select(2)
		self.writter = threading.Semaphore()
		self.netlock=threading.Semaphore()
		self.badItems.append(ErrorItem("┌──────────────┐"))
		# Translators: max lenght 32 chars
		self.badItems.append(ErrorItem(_(" Error connecting to Translation")))
		# Translators: max lenght 32 chars
		self.badItems.append(ErrorItem(_("          Memory server  ")))
		self.badItems.append(ErrorItem("└──────────────┘"))
		#### Translators ####
		if showspell:
			nr=cstep(0,self.upperbox.Bounds().right-4-self.upperbox.Bounds().right*2/3,self.oldsize*2)
			self.esb_rect=BRect(self.upperbox.Bounds().right*2/3,4,self.upperbox.Bounds().right-4,self.upperbox.Bounds().bottom-4)
			self.esbox=BBox(self.esb_rect,"ext_support_box",B_FOLLOW_RIGHT,border_style.B_PLAIN_BORDER)
			txt_rect=BRect(4,4+nr.Height(),self.esb_rect.Width()-4,self.esb_rect.Height()/2-4-nr.Height()/2)
			inrect=BRect(4,4,txt_rect.Width()-8,txt_rect.Height()-8)
			self.es_src=TranslatorTextView(self,txt_rect,"es_source",inrect,B_FOLLOW_RIGHT,B_WILL_DRAW|B_FRAME_EVENTS)
			txt_rect1=BRect(4,self.esb_rect.Height()/2+4+nr.Height()/2,self.esb_rect.Width()-4,self.esb_rect.Height()-nr.Height()-4)
			inrect1=BRect(4,4,txt_rect1.Width()-8,txt_rect1.Height()-8)
			self.es_trans=TranslatorTextView(self,txt_rect1,"es_translation",inrect1,B_FOLLOW_RIGHT,B_WILL_DRAW|B_FRAME_EVENTS)
			self.es_trans.MakeEditable(False)
			import deep_translator
			self.Traduttore = getattr(deep_translator, engine)
			langs_dict = self.Traduttore().get_supported_languages(as_dict=True)
			# Translators: Menu field, menu with a list of languages
			srclangtxt=_("Source language")
			self.msl=BMenu(srclangtxt)
			# Translators: Menu field, menu with a list of languages
			trgtlangtxt=_("Target language")
			self.mtl=BMenu(trgtlangtxt)
			self.msl.SetLabelFromMarked(True)
			self.mtl.SetLabelFromMarked(True)
			for language, code in langs_dict.items():
				sitm=TranslatorSourceLang(language,code)
				if code == self.src_lang:
					sitm.SetMarked(True)
				self.msl.AddItem(sitm)
				titm=TranslatorTargetLang(language,code)
				if code == self.trans_lang:
					titm.SetMarked(True)
				self.mtl.AddItem(titm)
			self.src_langs=BMenuField(nr, 'src_pop', srclangtxt+':', self.msl,B_FOLLOW_RIGHT)
			self.trg_langs=BMenuField(BRect(4,self.esb_rect.Height()/2-nr.Height()/2,self.esb_rect.Width()-4,self.esb_rect.Height()/2+4+nr.Height()/2), 'target_pop', trgtlangtxt+':', self.mtl,B_FOLLOW_RIGHT)
			self.traduttore = self.Traduttore(source=self.src_lang, target=self.trans_lang)
			# Translators: Button label/action
			self.gotrans=BButton(BRect(4,self.esb_rect.Height()-nr.Height()-4,self.esb_rect.Width()-4,self.esb_rect.Height()-4),'TranslateBtn',_('Translate'),BMessage(909),B_FOLLOW_BOTTOM|B_FOLLOW_RIGHT)
			self.esbox.AddChild(self.gotrans,None)
			self.esbox.AddChild(self.src_langs,None)
			self.esbox.AddChild(self.trg_langs,None)
			self.esbox.AddChild(self.es_src,None)
			self.esbox.AddChild(self.es_trans,None)
			self.upperbox.AddChild(self.esbox,None)
			self.esbox.ResizeTo(self.esb_rect.Width(),0)
			self.ongoing=threading.Semaphore() # locker for curtain
		
		####### end Translator #######
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

	def NichilizeMsgs(self):
		for i in self.msgstablabels:
			i.notify = False
		self.msgstabview.DrawTabs()
		for i in self.listemsgs:
			c=i.CountChildren()
			v=0
			while v<c:
				myview=i.ChildAt(v)
				if type(myview)==BTextView:
					myview.SelectAll()
					myview.Clear()
				v+=1
		if showspell:
			self.font=be_bold_font
			self.font.SetSize(28.0)
			nocolor=rgb_color()
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,nocolor)
			self.checkres.SetText("☐",None)
		self.valueln.SetText("")
		old_progress=self.FindView('progress')
		if old_progress!=None:
			self.RemoveChild(old_progress)
		self.progressinfo=BStatusBar(BRect(5,5,self.infobox.Bounds().right-5,35),'progress',_("Progress:"), None)
		self.infobox.AddChild(self.progressinfo,None)

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
		srcrect=self.srctabview.Bounds()
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
		self.infobox.GetFont(fon)
		s="100000"
		x=fon.StringWidth(s)
		self.valueln.MoveTo(self.infobox.Bounds().right-x-5,self.infobox.Bounds().bottom-fon.Size()-10)
		self.infoln.MoveTo(5,self.infobox.Bounds().bottom-fon.Size()-10)
		self.msgstabview.ResizeTo(self.infobox.Bounds().right-10,self.infobox.Bounds().bottom-fon.Size()-self.msgstabview.TabHeight()-40)
		self.tmscrollsugj.sv.ResizeTo(self.tmscrollsugj.sv.Bounds().right,self.upperbox.Bounds().Height()/2)
		sbh=self.tmscrollsugj.sv.ScrollBar(orientation.B_HORIZONTAL).Frame().Height()
		self.tmscrollsugj.lv.ResizeTo(self.tmscrollsugj.lv.Bounds().right,self.upperbox.Bounds().Height()/2-sbh)
		self.esbox.MoveTo(self.upperbox.Bounds().right-4-self.esbox.Bounds().Width(),4)
		self.expander.MoveTo(self.upperbox.Bounds().right-4-self.expander.Bounds().Width(),4+self.tmscrollsugj.sv.Bounds().Height()+10)
		self.expander.ResizeTo(self.expander.Bounds().right,self.upperbox.Bounds().Height()/2-80)
		for view in self.listemsgs:
			view.ResizeTo(view.Frame().right,self.msgstabview.Bounds().Height())
			i=0
			while i < view.CountChildren():
				tx=view.ChildAt(i)
				if type(tx) == BTextView:
					tx.ResizeTo(view.Frame().right-28,self.msgstabview.Bounds().Height()-48)
				if type(tx) == BScrollBar:
					tx.ResizeTo(20,self.msgstabview.Bounds().Height()-46)
				i+=1
			
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
	
	def generate_mo_with_babel(self,path_to_po):
		mo_output = path_to_po.replace('.po', '.mo')
		try:
			with open(path_to_po, 'rb') as infile:
				# 1. Legge il file PO
				catalog = read_po(infile) 

			with open(mo_output, 'wb') as outfile:
				# 2. Scrive (compila) il file MO
				write_mo(outfile, catalog)
			return True
			
		except FileNotFoundError:
			alrt1=_("Error: .po file not found at:")
			alrt2=(f"{alrt1} {path_to_po}")
			say = BAlert("not_found", alrt2, _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
			self.alerts.append(say)
			say.Go()
			return False
		except Exception as e:
			alrt1=_("Error compiling with Babel:")
			alrt2=(f"{alrt1} {e}")
			say = BAlert("error", alrt2, _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
			self.alerts.append(say)
			say.Go()
			return False
		
	def OpenPOFile(self, f):		
		#1)clean all
		self.sourcestrings.Clear()
		self.NichilizeTM()
		self.NichilizeTabs()
		self.NichilizeMsgs()
		subtype="none"
		
		#2)check mimetype
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
				if supertype=="text" and (subtype=="x-gettext-translation" or subtype=="x-gettext-translation-template"):
					boolgo=True
				else:
					say = BAlert('Warn', _('This is a workaround, the file\'s mimetype is not a x-gettext-translation nor a x-gettext-translation-template. Do you want to open the file despite this?'), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
					self.alerts.append(say)
					ret=say.Go()
					if ret==0:
						# mimetype not detected, check file extension
						boolgo=False
						if not(file_extension in [".po", ".pot", ".mo"]):
							return
						else:
							boolgo=True
					else:
						return
			except:
				say = BAlert('Warn', _('This is a workaround, cannot detect correctly the file\'s mimetype. Do you want to open the file despite this?'), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				ret=say.Go()
				if ret==0:
					# mimetype not detected, check file extension
					boolgo=False
					if not(file_extension in [".po", ".pot", ".mo"]):
						return
					else:
						supertype = "text"
						if file_extension == ".pot":
							subtype = "x-gettext-translation-template"
						else:
							subtype = "x-gettext-translation"
						boolgo=True
				else:
					return
		else:
			if file_extension in [".po", ".pot", ".mo"]:
				boolgo=True
			else:
				return
		if boolgo:
			# file correctly detected ... 
			# check poerrors
			if (file_extension in [".po",".mo"]) or (subtype == "x-gettext-translation"):
				errors=False
				infos,warnings,fatals=self.CheckPO(f)
				if len(infos)>0:
					for info in infos:
						say = BAlert(info[1], info[0], _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_INFO_ALERT)
						self.alerts.append(say)
						say.Go()
				if len(warnings)>0:
					for warn in warnings:
						say = BAlert(warn[1], warn[0], _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
						self.alerts.append(say)
						say.Go()
				if len(fatals)>0:
					for fatal in fatals:
						if fatal[1]!=None:
							# Translators: follows position of the error
							trnphr=_("At position")
							txt=f"{trnphr} {fatal[1]}: {fatal[0]}"
						else:
							txt=fatal[0]
						say = BAlert(fatal[2], txt, _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_STOP_ALERT)
						self.alerts.append(say)
						say.Go()
					errors=True
				if errors:
					try:
						fileenc = polib.detect_encoding(f)
						self.pof = polib.pofile(f,encoding=fileenc)
					except:
						print("impossibile aprire il file po")
						return
					try:
						ordmdata=self.pof.ordered_metadata()
						for i in ordmdata:
							if i[0]=="Language":
								self.tmxlang=i[1]
						a,b = checklang(ordmdata)
					except:
						print("errore nella lettura dei metadati")
						return
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
							#po file has no language metadata
							say = BAlert('Warn', _("There's no language section in metadata! Continue?"), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
							self.alerts.append(say)
							ret=say.Go()
							if ret==0:
								self.loadPO(f,self.pof)
							else:
								return
						elif b==1:
							#user has not the po file language
							say = BAlert('Warn', _('This gettext portable object file is not for your language!'), _('OK'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
							self.alerts.append(say)
							ret=say.Go()
						else:
							if self.builtin_srv[0]:
								try:
									if self.serv.is_alive():
										be_app.WindowAt(0).PostMessage(376)
									else:
										self.serv.start()
								except:
									self.serv=Thread(target=self.server,args=(self.builtin_srv[1],self.builtin_srv[2],self.builtin_srv[3],self.builtin_srv[4],))
									self.serv.start()
							self.loadPO(f,self.pof)
							note = BAlert('Note', _("Now you'll be addressed to the last fatal error"), _('OK'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_INFO_ALERT)
							self.alerts.append(note)
							ret=note.Go()
							#guut=[]
							for fatal in fatals:
								if isinstance(fatal[1],int):
									elemento=0
									elemselez=self.sourcestrings.lv.ItemAt(0)
									for elementi in self.sourcestrings.lv.Items():
										if elementi.linenum <= fatal[1]:
											if elementi.linenum> elemento:
												elementoselez=elementi
												elemento=elementi.linenum
									self.sourcestrings.lv.Select(self.sourcestrings.lv.IndexOf(elementoselez))
								
								####################################################################
								# abilitare questo se viene usato btextview al posto di btextcontrol
								# in findsource
								#if isinstance(fatal[1],int):
								#	elemento=0
								#	elemselez=self.sourcestrings.lv.ItemAt(0)
								#	for elementi in self.sourcestrings.lv.Items():
								#		if elementi.linenum <= fatal[1]:
								#			if elementi.linenum> elemento:
								#				elementoselez=elementi
								#				elemento=elementi.linenum
								#		else:
								#			break
								#	s=elementoselez.Text()
								#	guut.append(Findsource())
								#	trant=_("Find position:")
								#	guut[-1].SetTitle(trant+" "+str(fatal[1]))
								#	guut[-1].Show()
								#	mxg=BMessage(1010)
								#	mxg.AddString('txt',s)
								#	guut[-1].PostMessage(mxg)
					else:
						#mostra BBox per la creazione dell'utente
						say = BAlert('Warn', _('Please, fill the fields below, these informations will be written to saved po files and in config.ini'), _('OK'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_IDEA_ALERT)
						self.alerts.append(say)
						ret=say.Go()
						self.bckgnd.Hide()
						self.overbox.Show()
					return
				else:
				#...so open...
					# check user accepted languages
					fileenc = polib.detect_encoding(f)
					self.pof = polib.pofile(f,encoding=fileenc)
					ordmdata=self.pof.ordered_metadata()
					for i in ordmdata:
						if i[0]=="Language":
							self.tmxlang=i[1]
					a,b = checklang(ordmdata)
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
							say = BAlert('Warn', _("There's no language section in metadata! Continue?"), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
							self.alerts.append(say)
							ret=say.Go()
							if ret==0:
								self.loadPO(f,self.pof)
							else:
								return
						elif b==1:
							say = BAlert('Warn', _('This gettext portable object file is not for your language!'), _('OK'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
							self.alerts.append(say)
							ret=say.Go()
						else:
							if self.builtin_srv[0]:
								try:
									if self.serv.is_alive():
										be_app.WindowAt(0).PostMessage(376)#cambia file/lingua
									else:
										self.serv.start()
								except:
									self.serv=Thread(target=self.server,args=(self.builtin_srv[1],self.builtin_srv[2],self.builtin_srv[3],self.builtin_srv[4],))
									self.serv.start()
							self.loadPO(f,self.pof)
					else:
						#show user creation BBox
						say = BAlert('Warn', _('Please, fill the fields below, these informations will be written to saved po files and in config.ini'), _('OK'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_IDEA_ALERT)
						self.alerts.append(say)
						ret=say.Go()
						self.bckgnd.Hide()
						self.overbox.Show()
			else:
				langlist=[]
				for i in self.overbox.acceptedlang.lv.Items():
					langlist.append((i.txt,i.iso))
				self.chooser=POTchooser(f,langlist,self.oldsize)
				self.chooser.Show()
	def loadPO(self, pth, pof):
		filen, file_ext = os.path.splitext(pth)
		self.wob=False
		backupfile = filen+".temp"+file_ext
		if os.path.exists(backupfile):
			if os.path.getmtime(backupfile)>os.path.getmtime(pth):
				say = BAlert('Backup exist', _("There's a recent temporary backup file, open it instead?"), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				out=say.Go()
				if out == 0:
					self.wob=True
					try:
						temppofile = polib.pofile(backupfile,encoding=polib.detect_encoding(backupfile))
						self.handlePO(temppofile,backupfile,self.wob)
					except:
						say = BAlert('Warn', _('It is possible that the backup file is corrupted or damaged and it cannot be loaded! The original file will be loaded instead.'), _('OK'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
						self.alerts.append(say)
						ret=say.Go()
						self.handlePO(pof,pth,self.wob)
				else:
					self.handlePO(pof,pth,self.wob)
			else:
				self.handlePO(pof,pth,self.wob)
		else:
			self.handlePO(pof,pth,self.wob)

		

	def handlePO(self,pof,percors,workonbackup):
		p=BPath(BEntry(percors)).Leaf()
		title=f"{appname} {ver}: {p}\n"
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
		#get nplurals
		plural_forms_header = self.pofile.metadata.get('Plural-Forms', '')
		match = re.search(r'nplurals\s*=\s*(\d+)', plural_forms_header)
		if match:
			self.nplurals = int(match.group(1))
		else:
			print("Plural-Forms not found or malformed.")
		self.fp=BFilePanel(B_SAVE_PANEL,None,None,0,False, None, None, True, True)
		pathorig,nameorig=os.path.split(percors)
		self.fp.SetPanelDirectory(pathorig)
		self.fp.SetSaveText(nameorig)
		#create items and load sourcestrings
		self.load_sourcestrings(encoding)
		#look for previous self.progressinfo and remove them
		
		self.potot=len(self.pofile.translated_entries())+len(self.pofile.untranslated_entries())+len(self.pofile.fuzzy_entries())
		self.progressinfo.SetMaxValue(self.potot)
		self.progressinfo.Update(len(self.pofile.translated_entries()),None,str(self.pofile.percent_translated())+"%")
		
		x=self.bar.CountItems()
		i=0
		while i<x:
			try:
				itm=self.bar.SubmenuAt(i)
				try:
					if isinstance(itm.FindItem(self.cpfrsr),BMenuItem):
						itm.SetEnabled(True)
						break
				except Exception as e:
					#print("errore nella ricerca del BMenuItem",e)
					pass
			except Exception as e:
				print(e)
				pass
			i+=1
		self.bar.Invalidate()

	
	def load_sourcestrings(self,encoding):
		self.sourcestrings.Clear()
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

	def CheckPO(self,path):
		pth=BPath()
		BEntry(path).GetPath(pth)
		leaf=pth.Leaf()
		infos=[]
		warnings=[]
		fatals=[]
		asc=junitmsgfmt.MsgfmtTester(path)._run_msgfmt(path)
		if len(asc[2])>0:
			for item in asc[2]:
				try:
					tottxt=item[0] #tutto il testo
					ltxt=tottxt.split("msgfmt: ")
					mytxts=ltxt[0].split("\n")
					infos.append((ltxt[1],item[1]))
					for txt in mytxts:
						if txt.find(leaf+":")>-1:
							sptxt=txt.split(leaf+":")#every time i find "filename:" there's an error
							for s in sptxt:
								if s.find("warning:")>-1:
									warnings.append((s,item[1]))
								else:
									t=s[s.find(":")+2:]
									try:
										pos=int(s[:s.find(":")])#if int I can try to reach it
									except:
										pos=None
									if t!="":
										fatals.append((t,pos,item[1]))
				except Exception as e:
					infos.append((_("unable to handle the error"),e))
		return (infos,warnings,fatals)
	def Save(self, path):
		self.pofile.save(path)
		if path[-8:] != ".temp.po":
			infos, warnings, fatals = self.CheckPO(path)
			removetmp=[True,True]
			if len(warnings)>0:
				removetmp[0]=False
				for warn,title in warnings:
					say = BAlert(warn, title, ':-(',None, None, button_width.B_WIDTH_AS_USUAL , alert_type.B_STOP_ALERT)
					self.alerts.append(say)
					say.Go()
			if len(fatals)>0:
				removetmp[1]=False
				polines = []
				guut=[]
				with open (path, 'rt') as pf:
					for rie in pf:
						polines.append(rie)
				for fatal in fatals:
					try:
						strtosrc = polines[fatal[1]-1]
					except:
						strtosrc=None
					if strtosrc!=None:
						s=strtosrc[strtosrc.find("\"")+1:]
						s=s[:s.find("\"")]
						if s!="":
							say = BAlert(fatal[0], fatal[2]+_("\n\nGo to this error?"), _('Yes'),_("Skip"), None, button_width.B_WIDTH_AS_USUAL , alert_type.B_STOP_ALERT)
							self.alerts.append(say)
							out=say.Go()
							if out==0:
								guut.append(FindRepTrans())
								# Translators: Important! Same as window title before
								trant=_("Find/Replace")
								guut[-1].SetTitle(trant+" "+str(len(guut)-1))
								guut[-1].Show()
								mxg=BMessage(1010)
								mxg.AddString('txt',s)
								guut[-1].PostMessage(mxg)
			if removetmp[0] and removetmp[1]:
				tmppth=path[:-3]+".temp.po"
				entro=BEntry(tmppth)
				if entro.Exists():
					entro.Remove()
		#################################################
		######### This should be done by the OS #########
		st=BMimeType("text/x-gettext-translation")
		nd=BNode(path)
		ni = BNodeInfo(nd)
		ni.SetType("text/x-gettext-translation")
		#################################################
		ent,confile=Ent_config()
		Config.read(confile)
		try:
			#langcheck
			savemo = Config.getboolean('General','compilemo')
		except:
			savemo = False
		if savemo:
			self.generate_mo_with_babel(path)
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
					pck.append(src)
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
							sugjmsg.AddString('sugj_'+str(x),answer[x][0])
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
		
	def curtain_roller(self,up_down):
		x=self.esb_rect.Height()
		while x>0:
			curt=BMessage(2363)
			curt.AddBool("dir",up_down)
			self.event.wait(0.005)
			be_app.WindowAt(0).PostMessage(curt)
			x-=1
		self.ongoing.release()
	
	def switcher(self):
		self.ongoing.acquire()
		if ext_sup:
			if self.shortcut:
				if self.curtain:
					#close curtain
					self.expander.Show()
					self.TM_srv_status.Show()
					self.tmscrollsugj.sv.Show()
					self.spellabel.Show()
					self.checkres.Show()
					self.curtain=False
				else:
					#show curtain
					p1,p2=self.listemsgid[self.srctabview.Selection()].src.GetSelection()
					if p1!=p2:
						self.es_src.SetText(self.listemsgid[self.srctabview.Selection()].src.GetText(p1,p2-p1),None)
					self.expander.Hide()
					self.TM_srv_status.Hide()
					self.tmscrollsugj.sv.Hide()
					self.spellabel.Hide()
					self.checkres.Hide()
					self.curtain=True
				Thread(target=self.curtain_roller,args=(self.curtain,)).start()

	def MessageReceived(self, msg):
		if msg.what == B_MODIFIERS_CHANGED:
			value=msg.FindInt32("modifiers")
			self.sem.acquire()
			vtc=value-1
			if vtc in self.shifti:
				self.skipcheck=True
			else:
				self.skipcheck=False
			if value==self.modifiervalue or value==self.modifiervalue+8 or value ==self.modifiervalue+32 or value ==self.modifiervalue+40:
				#"modifier"
				self.modifier=True
				self.shortcut = False
			elif value == self.modifiervalue+257 or value==self.modifiervalue+265 or value==self.modifiervalue+289 or value == self.modifiervalue+297:
				#"shortcut"
				self.shortcut = True
				self.modifier = False
			else:
				#"other"
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
			elif key== 43:
						self.switcher()
						#Thread(target=self.switcher).start()
			return
		elif msg.what == 2363:
			direction=msg.FindBool("dir")
			if direction:
				self.esbox.ResizeBy(0,1)
			else:
				self.esbox.ResizeBy(0,-1)
			
		elif msg.what == 1:
			# Close opened file
			if self.sourcestrings.lv.CountItems()>0:
				if self.builtin_srv[0]:
					Thread(target=self.tmcommunicate,args=(None,)).start()
				self.sourcestrings.lv.DeselectAll()
				self.sourcestrings.Clear()
				self.Nichilize()
				self.NichilizeTM()
				self.NichilizeMsgs()
				#self.NichilizeTabs()
				altece2 = self.transtabview.TabHeight()
				tabrc2 = (3.0, 3.0, self.transtabview.Bounds().Width() - 3, self.transtabview.Bounds().Height()-altece2)
				self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',self))
				self.transtablabels.append(BTab(None))
				self.transtabview.AddTab(self.listemsgstr[0], self.transtablabels[0])
				self.transtabview.Select(1)									###### bug fix
				self.transtabview.Select(0)
				self.listemsgid[0].src.SelectAll()
				self.listemsgid[0].src.Clear()
				self.srctabview.Draw(self.srctabview.Bounds())
				self.SetTitle(" ".join([appname,ver]))
				self.filen=""
				self.file_ext=""
				#self.srctabview.Draw(self.srctabview.Bounds()) <<< look this!! bug fix
				
				x=self.bar.CountItems()
				i=0
				while i<x:
					try:
						itm=self.bar.SubmenuAt(i)
						try:
							if isinstance(itm.FindItem(self.cpfrsr),BMenuItem):
								itm.SetEnabled(False)
								break
						except Exception as e:
							pass
							#print("errore nella ricerca del BMenuItem",e)

					except Exception as e:
						print(e)
						pass
					i+=1
				self.bar.Invalidate()
			
			return
		elif msg.what == 2:
			#Save from menu
			#savefrom=msg.FindString("savefrom")
			if self.sourcestrings.lv.CountItems()>0:     ###### FIX HERE check condition if file is loaded
				ent,confile=Ent_config()
				if self.listemsgstr[self.transtabview.Selection()].trnsl.tosave:
					self.listemsgstr[self.transtabview.Selection()].trnsl.SaveToOrig()
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
			if self.sourcestrings.lv.CurrentSelection()>-1:
				thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
				thisBlistitem.tosave=True
				tabs=len(self.listemsgstr)-1
				bckpmsg=BMessage(16893)
				bckpmsg.AddBool('tmx',True)
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
						thisBlistitem.msgstrs.append(self.listemsgid[cox].src.Text())
						thisBlistitem.txttosavepl.append(self.listemsgid[cox].src.Text())
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
		elif msg.what == 800:
			self.src_lang = msg.FindString("code")
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			Config.set('Translator','src_lang', self.src_lang)
			Config.write(cfgfile)
			cfgfile.close()
			self.traduttore = self.Traduttore(source=self.src_lang, target=self.trans_lang)
		elif msg.what == 900:
			self.trans_lang = msg.FindString("code")
			ent,confile=Ent_config()
			cfgfile = open(confile,'w')
			Config.set('Translator','trans_lang', self.trans_lang)
			Config.write(cfgfile)
			cfgfile.close()
			self.traduttore = self.Traduttore(source=self.src_lang, target=self.trans_lang)
		elif msg.what == 909:
			self.es_trans.SetText(self.traduttore.translate(text=self.es_src.Text()),None)
		elif msg.what == 735157:
			color=rgb_color()
			color.green=150
			self.font.SetSize(28)
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,color)
			self.checkres.SetText("☑",None)
		elif msg.what == 826066:
			color=rgb_color()
			self.font.SetSize(28)
			self.checkres.SetFontAndColor(self.font,set_font_mask.B_FONT_ALL,color)
			self.checkres.SetText("☐",None)
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
					indexBlistitem=self.sourcestrings.lv.CurrentSelection()
					name=time.time()
					self.listemsgstr[self.transtabview.Selection()].trnsl.checklater(str(name), self.listemsgstr[self.transtabview.Selection()].trnsl.Text(),indexBlistitem)
#						print self.tmscrollsugj.lv.ItemAt(askfor).text #settext con tutte i vari controlli ortografici mettere tosave = True a eventtextview interessato
		elif msg.what == 33:
			#copy from source from keyboard
			# commented out all saving rows to the backup
			# if you want to save use copy from menu
			if self.sourcestrings.lv.CurrentSelection()>-1:
				thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
				thisBlistitem.tosave=True
				tabs=len(self.listemsgstr)-1
				#bckpmsg=BMessage(16893)
				#bckpmsg.AddInt8('savetype',1)
				#bckpmsg.AddBool('tmx',False)
				#bckpmsg.AddInt32('tvindex',self.sourcestrings.lv.CurrentSelection())
				#bckpmsg.AddInt8('plurals',tabs)
				if tabs == 0:   #-> if not thisBlistitem.hasplural:  <-- or this?
					thisBlistitem.txttosave=thisBlistitem.text#.decode(self.cod)#(self.encoding)
					thisBlistitem.msgstrs=thisBlistitem.txttosave
					#bckpmsg.AddString('translation',thisBlistitem.txttosave)
				else:
					thisBlistitem.txttosavepl=[]
					thisBlistitem.txttosave=self.listemsgid[0].src.Text()
					thisBlistitem.msgstrs=[]
					thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
					#bckpmsg.AddString('translation',thisBlistitem.txttosave)
					cox=1
					while cox < tabs+1:
						thisBlistitem.msgstrs.append(self.listemsgid[cox].src.Text())
						thisBlistitem.txttosavepl.append(self.listemsgid[cox].src.Text())
						#bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())
						cox+=1
				#bckpmsg.AddString('bckppath',self.backupfile)
				#be_app.WindowAt(0).PostMessage(bckpmsg)
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
			#run checkspell
			if self.sourcestrings.lv.CurrentSelection()>-1 and showspell:
				##self.Looper().Lock()
				#try:
					if self.listemsgstr[self.transtabview.Selection()].trnsl.Text()=="":
						be_app.WindowAt(0).PostMessage(826066)#set empty square for checkspell result
					else:
						if self.listemsgstr[self.transtabview.Selection()].trnsl.CheckSpell():
							be_app.WindowAt(0).PostMessage(735157)#set ok square for checkspell result
						else:
							be_app.WindowAt(0).PostMessage(982757)#set X square for checkspell result
				#except:
				#	pass
				##self.Looper().Unlock()
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
		elif msg.what == 8:
			# launch help url
			perc=BPath()
			find_directory(directory_which.B_SYSTEM_DOCUMENTATION_DIRECTORY,perc,False,None)
			link=perc.Path()+"/packages/haipo/HaiPO2/index.html"
			ent=BEntry(link)
			if ent.Exists():
				# open system documentation help
				t = Thread(target=openlink,args=(link,))
				t.run()
			else:
				find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
				link=perc.Path()+"/HaiPO2/Data/help/index.html"
				ent=BEntry(link)
				if ent.Exists():
					# open user data dir help
					t = Thread(target=openlink,args=(link,))
					t.run()
				else:
					# look for local help
					nopages=True
					cwd = os.getcwd()
					link=cwd+"/data/help/index.html"
					ent=BEntry(link)
					if ent.Exists():
						# open local help
						t = Thread(target=openlink,args=(link,))
						t.run()
						nopages=False
					#else:
					#	alt="".join(sys.argv)
					#	mydir=os.path.dirname(alt)
					#	print(mydir)
					#	link=mydir+"/Data/help/index.html"
					#	ent=BEntry(link)
					#	if ent.Exists():
					#		t = Thread(target=openlink,args=(link,))
					#		t.run()
					#		nopages=False
					if nopages:
						wa=BAlert('noo', _('No help pages installed'), _('Poor me'), None,None,InterfaceDefs.B_WIDTH_AS_USUAL,alert_type.B_WARNING_ALERT)
						self.alerts.append(wa)
						wa.Go()
		elif msg.what == 9:
			#ABOUT
			self.About = AboutWindow()
			self.About.Show()
			return
		elif msg.what == 40:
			#self.winset.append(GeneralSettings(self))
			#self.winset[-1].Show()
			self.gensettings=GeneralSettings(self.oldsize)
			self.gensettings.Show()
			return
		elif msg.what == 41:
			#USER SETTINGS
			self.bckgnd.Hide()
			self.overbox.Show()
			self.overbox.BtnCancel.Hide()
			return
		elif msg.what == 53:
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
			# pulse procedure
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
				self.check_tm_status()
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
						thisBlistitem=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
						thisBlistitem.tosave=True
						tabs=len(self.listemsgstr)-1
						bckpmsg=BMessage(16893)
						bckpmsg.AddInt8('savetype',1)
						bckpmsg.AddBool('tmx',True)
						bckpmsg.AddInt32('tvindex',self.sourcestrings.lv.CurrentSelection())
						bckpmsg.AddInt8('plurals',tabs)
						if tabs == 0:#->if not thisBlistitem.hasplural:<- or this?

							thisBlistitem.txttosave=thistranslEdit.Text()
							bckpmsg.AddString('translation',thisBlistitem.txttosave)
							thisBlistitem.msgstrs=thistranslEdit.Text()
						else:
							thisBlistitem.txttosavepl=[]
							thisBlistitem.txttosave=self.listemsgstr[0].trnsl.Text()
							thisBlistitem.msgstrs=[]
							thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
							# TODO : betatesters: need to check plural changes
							print(thisBlistitem.msgstrs)
							bckpmsg.AddString('translation',thisBlistitem.txttosave)
							cox=1
							while cox < tabs+1:
								thisBlistitem.txttosavepl.append(self.listemsgstr[cox].trnsl.Text())
								bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgstr[cox].trnsl.Text())
								thisBlistitem.msgstrs.append(self.listemsgstr[cox].trnsl.Text())
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
			return
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
			return
		elif msg.what == 14183:
			try:
				Config.read(confile)
				compile=Config.getboolean('General', 'compilemo')
			except:
				compile=False
			if compile:
				#compila il file mo
				print("origine",self.filen+self.file_ext)
				print("mo diventa",self.filen+".mo")
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
				#save of metadata
				self.writter.acquire()
				#update self.orderedmetadata
				self.orderedmetadata = self.pofile.ordered_metadata()
				self.pofile.metadata['Last-Translator']=defname # metadata saved from po settings
				self.pofile.metadata['PO-Revision-Date']=now
				self.pofile.metadata['X-Editor']=version
				Thread(target=self.Save,args=(bckppath,)).start()
				#self.pofile.save(bckppath)
				return
			elif savetype == 1:
				#save
				if tm:
					needtopush=msg.FindBool('tmx') # valutare se spostare in if (tm and needtopush):
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
						#"serve aggiungere a tmx"
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
			self.NichilizeTM()
			if self.sourcestrings.lv.CurrentSelection()>-1:
				item=self.sourcestrings.lv.ItemAt(self.sourcestrings.lv.CurrentSelection())
				if item.hasplural:
					beta=len(item.msgstrs)
					if beta!=self.nplurals:
						say=BAlert(_('Different number of plurals'), _('This entry presents plural source entry, but the number of translation entries do not respect the language number of plurals. Saving this entry will introduce some differences from original file or errors. Do you want to manually fix this error or let this app attempt a fix?'), _('Manual'),_('Auto Fix'), None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
						self.alerts.append(say)
						ret = say.Go()
						if ret == 0:
							be_app.WindowAt(0).PostMessage(B_QUIT_REQUESTED)
							return
						else:
							self.FixItemMsgstrs(item)
							return
					self.Nichilize()
					self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr[0]',self))
					self.transtablabels.append(BTab(None))
					self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
					self.listemsgid.append(srctabbox(self,(3,3,self.listemsgid[0].Bounds().right+3,self.listemsgid[0].Bounds().bottom+3),'msgid_plural',altece2))
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
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr['+str(ww)+']',self))
							self.listemsgstr[ww].trnsl.SetPOReadText(item.msgstrs[ww])
							self.transtabview.AddTab(self.listemsgstr[ww],self.transtablabels[ww])
						ww=ww+1
					#TODO: inserire check len(self.transtablabels) != nplurs specificato da metadatapo nell'header
				else:
					self.Nichilize()
					self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',self))
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
				self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
				if tm:
					self.tmscrollsugj.Clear()
					riga=self.listemsgid[self.srctabview.Selection()].src.Text()
					cirmsg=BMessage(738033)
					cirmsg.AddString('s',riga)
					be_app.WindowAt(0).PostMessage(cirmsg)
					#Thread(target=self.tmcommunicate,args=(riga,)).start()
			else:
				if tm:
					self.NichilizeTM()
				self.Nichilize()				
				self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',self))
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
			if showspell:
				be_app.WindowAt(0).PostMessage(12343)
			return
		elif msg.what == 7484:
			# status active - rotation 
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
			return
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
			say = BAlert('Save unsaved work', _('To proceed you need to save this file first, proceed?'), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			out=say.Go()
			if out == 0:
				#save first
				be_app.WindowAt(0).PostMessage(2)
				self.setMark(0)
			return
		elif msg.what == 75:
			#this is slow due to reload
			say = BAlert('Save unsaved work', _('To proceed you need to save this file first, proceed?'),_('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			out=say.Go()
			if out == 0:
				#save first
				be_app.WindowAt(0).PostMessage(2)
				self.setMark(1)
			return
		elif msg.what == 76:
			#this is slow due to reload
			say = BAlert('Save unsaved work', _('To proceed you need to save this file first, proceed?'), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
			self.alerts.append(say)
			out=say.Go()
			if out == 0:
				#save first
				be_app.WindowAt(0).PostMessage(2)
				self.setMark(2)
			return
		elif msg.what == 77:
			#this is slow due to reload
			say = BAlert('Save unsaved work', _('To proceed you need to save this file first, proceed?'), _('Yes'),_('No'), None, button_width.B_WIDTH_AS_USUAL , alert_type.B_WARNING_ALERT)
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
			# Translators: as in phrase "Custom iso"
			newitem=LangListItem(_("Custom"),iso,False)
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
				say = BAlert('Warn', _('Please, fill the fields below, these informations will be written to saved po files and in config.ini'), _('OK'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
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
			#self.pofile.save(completepath) <--- moved inside self.Save
			ent,confile=Ent_config()
			try:
				Config.read(confile)
				defname=ConfigSectionMap("Translator")['name']+' <'+ConfigSectionMap("Translator")['mail']+'>'
				grp=ConfigSectionMap("Translator")['team']+' <'+ConfigSectionMap("Translator")['ltmail']+'>'
			except:
				defname=self.pofile.metadata['Last-Translator']
				grp=self.pofile.metadata['Language-Team']
			now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
			self.writter.acquire()
			self.pofile.metadata['Last-Translator']=defname
			self.pofile.metadata['Language-Team']=grp
			self.pofile.metadata['PO-Revision-Date']=now
			self.pofile.metadata['X-Editor']=version
			self.Save(completepath)
			self.name=e
			self.percors=completepath
			self.pofile= polib.pofile(completepath,encoding=self.encoding)
			self.filen, self.file_ext = os.path.splitext(completepath)
			self.backupfile= self.filen+".temp"+self.file_ext
			return
		elif msg.what == 376:
			if self.builtin_srv[0]:
				cmd=("c","h","g")
				mx=[cmd,"",""]
				Thread(target=self.tmcommunicate,args=(mx,)).start()
			return
		elif msg.what == 386:
			f=self.filen+self.file_ext
			self.OpenPOFile(f)
			#self.sourcestrings.reload(self.poview,self.pofile,self.encoding)
			return
		elif msg.what == 112118:
			#launch a delayed check
			oldtext=msg.FindString('oldtext')
			indexBlistitem=msg.FindInt32('indexBlistitem')
			tabs=len(self.listemsgstr)-1
			
			if indexBlistitem == self.sourcestrings.lv.CurrentSelection():
				if self.listemsgstr[self.transtabview.Selection()].trnsl.oldtext != self.listemsgstr[self.transtabview.Selection()].trnsl.Text():
					self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			self.speloc.acquire()
			self.intime=time.time()
			self.speloc.release()
			return
		elif msg.what == 113119:
			ubi1,ubi2=self.listemsgstr[self.transtabview.Selection()].trnsl.GetSelection()
			if ubi1!=ubi2:
				self.listemsgstr[self.transtabview.Selection()].trnsl.Select(ubi2,ubi2)
			self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
			self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus()
			return
		elif msg.what == 130550: # change listview selection
			movetype=msg.FindInt8('movekind')
			if tm:
				self.NichilizeTM()
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
					print("text to save (this shouldn\'t happen)",thisBlistitem.txttosave)
			except:
				pass
			if self.listemsgstr[self.transtabview.Selection()].trnsl.Text()!="":
				be_app.WindowAt(0).PostMessage(333111)
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
			return
		elif msg.what == 738033:
			#look for translations
			if tm:
				self.NichilizeTM()
				Thread(target=self.tmcommunicate,args=(msg.FindString('s'),)).start()
			return
		elif msg.what == 140:
			if self.tmscrollsugj.lv.CurrentSelection()>-1:
				try:
					self.expander.SetText(self.tmscrollsugj.lv.ItemAt(self.tmscrollsugj.lv.CurrentSelection()).Text(),None)
				except:
					pass #non è un suggerimento forse un ErrorItem
			return
		elif msg.what == 141:
			#paste sugg to trnsl EventTextView
			try:
				self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.tmscrollsugj.lv.ItemAt(self.tmscrollsugj.lv.CurrentSelection()).Text(),None)
				self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus()
				lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
				self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
				self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
				self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
				self.listemsgstr[self.transtabview.Selection()].trnsl.CheckSpell()
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
						mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text(),self.listemsgstr[self.transtabview.Selection()].trnsl.Text())
						Thread(target=self.tmcommunicate,args=(mx,)).start()
						#print "beh, questo è corretto ma ha suggerimenti sbagliati, salvare in tmx!"
				else:
					mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text(),self.listemsgstr[self.transtabview.Selection()].trnsl.Text())
					Thread(target=self.tmcommunicate,args=(mx,)).start()
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

			for item in self.badItems:
				self.tmscrollsugj.lv.AddItem(item)
			return
		#445380 huge check on older version look at that code
		BWindow.MessageReceived(self, msg)
	def check_tm_status(self):
		if self.builtin_srv[0]:
			try:
				if self.serv.is_alive():
					self.TM_srv_status.SetText(_("TM server status: alive"))
				else:
					self.TM_srv_status.SetText(_("TM server status: dead"))
			except:
				self.TM_srv_status.SetText(_("TM server status: died badly"))
		else:
			self.TM_srv_status.SetText(_("TM server status: not running"))
	def FixItemMsgstrs(self,item):
		mtxt1=_("A reconstructed file (")
		mtxt2=_(") has been created, Please check for compliance.")
		beta=len(item.msgstrs)
		polines = []
		path=self.backupfile
		delta=0
		path=path.replace(".temp.po",".po")
		with open (path, 'rt') as pf:
			for rie in pf:
				polines.append(rie)
		if beta<self.nplurals:
			#aggiungi righe
			while True:
				#salta le righe con commenti vari
				if polines[item.linenum][:5]!="msgid":
					delta+=1
				else:
					break
			row_sing=polines[item.linenum+delta]
			row_plur=polines[item.linenum+delta+1]
			rs=row_sing[row_sing.find("\"")+1:]
			rs=rs[:rs.find("\"")]
			rp=row_plur[row_plur.find("\"")+1:]
			rp=rp[:rp.find("\"")]
			if rs == item.msgids[0] and rp == item.msgids[1]:
				i=1
				inti=i
				rowst=[]
				while i<self.nplurals+1:
					row_trans=polines[item.linenum+delta+1+inti]
					if row_trans=="\n":
						newstr=f"msgstr[{str(i-1)}] \"\""
						polines.insert(item.linenum+delta+1+inti,newstr)
						polines.insert(item.linenum+delta+1+inti+1,"\n")
					elif row_trans[:6] == "msgstr":
						pass
					else:
						i-=1#potrebbe essere continuazione riga precedente
					i+=1
					inti+=1
				newpath=path[:-3]+".reconstructed.po"
				with open(newpath,'w') as f:
					f.writelines(polines)
				say = BAlert('Succeeded', f"{mtxt1}{newpath}{mtxt2}", _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_INFO_ALERT)
				self.alerts.append(say)
				say.Go()		
		elif beta>self.nplurals:
			#rimuovi righe
			while True:
				#salta le righe con commenti vari
				if polines[item.linenum][:5]!="msgid":
					delta+=1
				else:
					break
			row_sing=polines[item.linenum+delta]
			row_plur=polines[item.linenum+delta+1]
			rs=row_sing[row_sing.find("\"")+1:]
			rs=rs[:rs.find("\"")]
			rp=row_plur[row_plur.find("\"")+1:]
			rp=rp[:rp.find("\"")]
			if rs == item.msgids[0] and rp == item.msgids[1]:
				i=1
				inti=i
				rowst=[]
				while True:
					row_trans=polines[item.linenum+delta+1+inti]
					if row_trans=="\n":
						if i>self.nplurals:
							#salva
							break
						else:
							#c'è una riga vuota in mezzo
							kabuki=item.linenum+delta+1+inti
							#print(f"is {kabuki} an empty line in the middle?")
					elif row_trans[:6] == "msgstr":
						if i>self.nplurals:
							acti=item.linenum+delta+1+inti
							torem=[]
							while True:
								if polines[acti][:2]=="#:":#non dovrebbe succedere, ma se siamo sulla traduzione successiva...
									break
								if polines[acti+1]=="\n":
									torem.append(acti)
									break
								torem.append(acti)
								acti+=1
							uwu=len(torem)
							if uwu>0:
								while uwu>-1:
									polines.pop(uwu)
									uwu-=1
							else:
								print("I had to eliminate excess elements, but I did not detect them")
					else:
						i-=1#potrebbe essere continuazione riga precedente
					i+=1
					inti+=1
				newpath=path[:-3]+".reconstructed.po"
				with open(newpath,'w') as f:
					f.writelines(polines)
				say = BAlert('Succeeded', f"{mtxt1}{newpath}{mtxt2}", _('Ok'),None, None, button_width.B_WIDTH_AS_USUAL, alert_type.B_INFO_ALERT)
				self.alerts.append(say)
				say.Go()
		be_app.WindowAt(0).PostMessage(B_QUIT_REQUESTED)
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
			self.poview[index]=True
		Config.write(cfgfile)
		cfgfile.close()
		be_app.WindowAt(0).PostMessage(386)
		#self.sourcestrings.reload(self.poview,self.pofile,self.encoding)
	def server(self,addr,PORT=2022,HEADER=4096,log=False):
		perc=BPath()
		find_directory(directory_which.B_USER_NONPACKAGED_DATA_DIRECTORY,perc,False,None)
		datapath=BDirectory(perc.Path()+"/HaiPO2")
		ent=BEntry(datapath,perc.Path()+"/HaiPO2")
		if not ent.Exists():
			datapath.CreateDirectory(perc.Path()+"/HaiPO2", datapath)
		ent.GetPath(perc)
		ftmx=perc.Path()+'/outtmx'+self.tmxlang+'.db'
		e = BEntry(ftmx)
		if not e.Exists():
			with open(ftmx, 'a') as des:
				des.write(
				"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tmx SYSTEM \"tmx14.dtd\">\n"
				"<tmx version=\"1.4\">\n  <header creationtool=\"Translate Toolkit\" "
				"creationtoolversion=\"3.8.0\" segtype=\"sentence\" o-tmf=\"UTF-8\" adminlang=\"en\" "
				"srclang=\"en\" datatype=\"PlainText\"/>\n  <body>\n")
				des.write("  </body>\n</tmx>\n")
		flog=perc.Path()+'/log.txt'
		tmp_ftmx=perc.Path()+'/tmp_outtmx'+self.tmxlang+'.db'
		old_ftmx=perc.Path()+'/old_outtmx'+self.tmxlang+'.db'
		if log:
			with open(flog, 'a') as des:
				des.write("launching server...\n")
		IP = socket.gethostbyname(addr)
		self.keeperoftheloop=True
		try:
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
											with open(ftmx, 'rb') as fin, open(tmp_ftmx, 'a') as des:
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
														des.write("      <tuv xml:lang=\""+self.tmxlang+"\">\n        <seg>"+msgstr+"</seg>\n      </tuv>\n    </tu>\n")
														des.write("  </body>\n</tmx>\n")
														save_db(old_ftmx,tmp_ftmx,ftmx)
														break
											break
									elif message[0][0]==('c','h','g'):
										ftmx=perc.Path()+'/outtmx'+self.tmxlang+'.db'
										flog=perc.Path()+'/log.txt'
										tmp_ftmx=perc.Path()+'/tmp_outtmx'+self.tmxlang+'.db'
										old_ftmx=perc.Path()+'/old_outtmx'+self.tmxlang+'.db'
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
															if '<tuv xml:lang="'+self.tmxlang+'">' in str(liniis[i+k]):
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
										save_db(old_ftmx,tmp_ftmx,ftmx)
										break
									else:
										lung1=len(message[0])
										lung2=round(lung1*0.75,0)
										delta=lung1-lung2+1
										#print("file dizionario:",ftmx)
										with open(ftmx, 'rb') as fin:
											tmx_file = tmxfile(fin, "en", self.tmxlang)
											for node in tmx_file.unit_iter():
												dist=lev(message[0],node.source)
												if dist<delta:#2
													suggerimenti.append((node.target,dist))
										suggerimenti.sort(key=lambda element:element[1])
										client_socket.send(pickle.dumps(suggerimenti,protocol=2))
								except FileNotFoundError as e:
									with open(ftmx, 'a') as des:
										des.write(
										"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tmx SYSTEM \"tmx14.dtd\">\n"
										"<tmx version=\"1.4\">\n  <header creationtool=\"Translate Toolkit\" "
										"creationtoolversion=\"3.8.0\" segtype=\"sentence\" o-tmf=\"UTF-8\" adminlang=\"en\" "
										"srclang=\"en\" datatype=\"PlainText\"/>\n  <body>\n")
										des.write("  </body>\n</tmx>\n")
										#des.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tmx SYSTEM \"tmx14.dtd\">\n<tmx version=\"1.4\">\n  <header creationtool=\"Translate Toolkit\" creationtoolversion=\"3.8.0\" segtype=\"sentence\" o-tmf=\"UTF-8\" adminlang=\"en\" srclang=\"en\" datatype=\"PlainText\"/>\n  <body>\n")
										#des.write("  </body>\n</tmx>\n")
					#print("quit from keeper of the loop")
				except KeyboardInterrupt:
					server_socket.close()
					print("aborted by user")
		except OSError as e:
			if e.errno == -2147454954:
				print("Server instance not started\nprobably another one already running...")
		#server_socket.close()
		print("Server closed")
		
	def QuitRequested(self):
		#check if there's a .temp.po file and if it's newer than the original .po, if so ask if you want to Save changes, Delete temp file, Just quit
		pth="".join((self.filen,self.file_ext))
		backupfile="".join((self.filen,".temp",self.file_ext))
		if os.path.exists(backupfile):
			if os.path.getmtime(backupfile)>os.path.getmtime(pth):
				say = BAlert('Quit?', _("The temporary file is newer than the original po file, what do you want to do?"), _('Save it to po file'), _("Delete temp file"), _("Just quit"), button_width.B_WIDTH_AS_USUAL, alert_type.B_WARNING_ALERT)
				self.alerts.append(say)
				ret=say.Go()
				if ret == 0:
					# overwrite the original
					self.pofile= polib.pofile(backupfile,encoding=self.encoding)
					self.Save(pth)
				elif ret==1:
					# delete temp file
					entro=BEntry(backupfile)
					if entro.Exists():
						entro.Remove()
				elif ret==2:
					# quit without saving
					pass
		# Note: this strange kind of QuitRequest is the only one which does not request a double free
		# of this BWindow (don't know why). The actual Quit is done through be_app O_O'
		self.keeperoftheloop = False
		Thread(target=self.tmcommunicate,args=(None,)).start()
		self.event.wait(0.2)
		be_app.Quit()
		

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
		# Translators: window title
		BWindow.__init__(self, BRect(w/2-200, h/2-fon.Size(), w/2+200, h/2+fon.Size()),_("CustomISO"),window_type.B_BORDERED_WINDOW, B_NOT_RESIZABLE|B_CLOSE_ON_ESCAPE)
		self.bckgnd=BBox(self.Bounds(),"bckgnd_customiso",B_FOLLOW_NONE,B_WILL_DRAW,border_style.B_NO_BORDER)
		self.input=BTextControl(self.bckgnd.Bounds(),"isoinput",_("ISO code:"),"",BMessage(252))
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
			self.poeditor=MainWindow("")
		else:
			self.poeditor=MainWindow(self.realargs[0])
		self.poeditor.Show()
	def ArgvReceived(self,num,args):
		realargs=args
		if args[1][-8:]=="HaiPO.py" or args[1][-5:]=="HaiPO":
			#launched by terminal or by link in non-packaged/bin
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