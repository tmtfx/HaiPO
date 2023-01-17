#!/boot/system/bin/python
# -*- coding: utf-8 -*-

#   A Simple PO editor for Haiku.
#
# Copyright (c) 2021 Fabio Tomat

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os,sys,ConfigParser,struct,re,thread,datetime,time,threading,unicodedata
from distutils.spawn import find_executable
from subprocess import Popen,STDOUT,PIPE

version='HaiPO 1.4 beta'
(appname,ver,state)=version.split(' ')

jes = False

try:
	import polib
except:
	print "Your python environment has no polib module"
	jes=True

Config=ConfigParser.ConfigParser()
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

firstrun=False
global evstyle,deb
deb=False
evstyle=threading.Semaphore()
global confile,setencoding
confile=os.path.join(sys.path[0],'config.ini')
if os.path.isfile(confile):
	try:
		Config.read(confile)
		name=ConfigSectionMap("Users")['names']
		default=ConfigSectionMap("Users")['default']
		name=ConfigSectionMap(default)['name']
		lang=ConfigSectionMap(default)['lang']
		team=ConfigSectionMap(default)['team']
		pemail=ConfigSectionMap(default)['pe-mail']
		temail=ConfigSectionMap(default)['te-mail']

	except (ConfigParser.NoSectionError):
		os.rename(os.path.join(sys.path[0],'config.ini'),os.path.join(sys.path[0],'config_old.ini'))
		firstrun = True
else:
	firstrun = True

if not firstrun:
	global tm,tmxsrv,tmxprt,tmsocket
	try:
		Config.read(confile)
		try:
			if ConfigSectionMap("Settings")['tm'] == "True":
				tm = True
			else:
				tm = False
		except:
			cfgfile = open(confile,'w')
			Config.set('Settings','tm', 'False')
			Config.write(cfgfile)
			cfgfile.close()
			tm=False
		if tm:
			import socket,pickle
			#tmsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			usero=ConfigSectionMap("Users")['default']
			try:
				tmxsrv=ConfigSectionMap(usero)['tmxsrv']
				tmxprt=int(ConfigSectionMap(usero)['tmxprt'])
			except:
				cfgfile = open(confile,'w')
				Config.set(usero,'tmxsrv', '127.0.0.1')
				Config.set(usero,'tmxprt', 2022)
				Config.write(cfgfile)
				cfgfile.close()

	except:
		tm = False
		tmxsrv = '127.0.0.1'
		tmxprt = 2022
	#try:
	#	if tm:
	#		tmsocket.settimeout(3)
	#		#tmsocket.connect((tmxsrv,tmxprt))
	#except:
	#	print ("impossibile connettersi")
		
if not firstrun:
	global showspell
	showspell = False
	try:
#	if True:
		Config.read(confile)
		try:
			if ConfigSectionMap("Settings")['spellchecking'] == "True":
				setspellcheck=True
			else:
				setspellcheck=False
		except:
			cfgfile = open(confile,'w')
			Config.set('Settings','spellchecking', 'False')
			Config.write(cfgfile)
			cfgfile.close()
			setspellcheck=False
		try:
			setencoding=Config.getboolean('Settings', 'customenc')
			if setencoding:
					try:
						usero=ConfigSectionMap("Users")['default']
						try:
							encoding = ConfigSectionMap(usero)['encoding']
						except:
							print "setencoding true but no encoding property in user settings"
							encoding = "utf-8"
						pass
					except (ConfigParser.NoSectionError):
						encoding = "utf-8"
						setencoding = False
		except:
				setencoding = False

		if setspellcheck:
			showspell=True
			try:
				global inclusion,esclusion
				usero=ConfigSectionMap("Users")['default']
				try:
					inctxt=ConfigSectionMap(usero)['spell_inclusion']
					inclusion = inctxt.split(",")
				except:
					cfgfile = open(confile,'w')
					Config.set(usero,'spell_inclusion', '')
					Config.write(cfgfile)
					cfgfile.close()
					inclusion = []
				try:
					esctxt=ConfigSectionMap(usero)['spell_esclusion']
					esclusion=esctxt.split(",")
				except:
					cfgfile = open(confile,'w')
					Config.set(usero,'spell_esclusion', 'Pc,Pd,Pe,Pi,Po,Ps,Cc,Pf')
					Config.write(cfgfile)
					cfgfile.close()
					esclusion = ["Pc","Pd","Pe","Pi","Po","Ps","Cc","Pf"]
				try:
					spelldict=ConfigSectionMap(usero)['spell_dictionary']
				except:
					cfgfile = open(confile,'w')
					Config.set(usero,'spell_dictionary', '/system/data/hunspell/en_US')
					Config.write(cfgfile)
					cfgfile.close()
					spelldict="/system/data/hunspell/en_US"
			except:
				spelldict="/system/data/hunspell/en_US"
				inclusion = []
				esclusion = ["Pc","Pd","Pe","Pi","Po","Ps","Cc","Pf"]
			try:
				exe=ConfigSectionMap("Settings")['spell_path']
			except:
				exe = "hunspell-x86"
			if setencoding:
				comm = [exe,'-i',encoding,'-d',spelldict]
			else:
				comm = [exe,'-d',spelldict]
		else:
			showspell=False
	except:
		setspellcheck = False
		showspell = False

else:
	showspell = False
	setspellcheck = False
try:
	import BApplication
	from BStringItem import BStringItem
	from BListView import BListView
	from BScrollView import BScrollView
	from BWindow import BWindow
	from BMessage import BMessage
	from BMenuItem import BMenuItem
	from BMenu import BMenu
	from BBox import BBox
	from BButton import BButton
	from BMenuBar import BMenuBar
	from BPopUpMenu import BPopUpMenu
	from BSeparatorItem import BSeparatorItem
	from BStringView import BStringView
	from BTab import BTab
	from BTabView import BTabView
	from BTextView import BTextView
	from BFont import be_plain_font, be_bold_font
	from BTextControl import BTextControl
	from BStatusBar import BStatusBar
	from BAlert import BAlert
	from BListItem import BListItem
	from BStatusBar import BStatusBar
	from BTranslationUtils import *
	from BFile import BFile
	from BNode import BNode
	from BNodeInfo import BNodeInfo
	from BMimeType import BMimeType
	from BCheckBox import BCheckBox
	from BView import BView
	import BEntry
	from BFont import BFont
	from BFilePanel import BFilePanel
	from BEntry import BEntry
	from BScrollBar import BScrollBar
	from InterfaceKit import B_PAGE_UP,B_PAGE_DOWN,B_TAB,B_ESCAPE,B_DOWN_ARROW,B_UP_ARROW,B_V_SCROLL_BAR_WIDTH,B_FULL_UPDATE_ON_RESIZE,B_VERTICAL,B_FOLLOW_ALL,B_FOLLOW_TOP,B_FOLLOW_LEFT,B_FOLLOW_RIGHT,B_WIDTH_FROM_LABEL,B_TRIANGLE_THUMB,B_BLOCK_THUMB,B_FLOATING_WINDOW,B_DOCUMENT_WINDOW,B_TITLED_WINDOW,B_WILL_DRAW,B_NAVIGABLE,B_FRAME_EVENTS,B_ALIGN_CENTER,B_ALIGN_RIGHT,B_FOLLOW_ALL_SIDES,B_MODAL_WINDOW,B_FOLLOW_TOP_BOTTOM,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT_RIGHT,B_SINGLE_SELECTION_LIST,B_NOT_RESIZABLE,B_NOT_ZOOMABLE,B_PLAIN_BORDER,B_FANCY_BORDER,B_NO_BORDER,B_ITEMS_IN_COLUMN,B_AVOID_FOCUS,B_BOLD_FACE,B_ITALIC_FACE,B_UNDERSCORE_FACE,B_STRIKEOUT_FACE,B_FONT_ALL,B_NAVIGABLE,B_NAVIGABLE_JUMP
	from AppKit import B_QUIT_REQUESTED,B_KEY_UP,B_KEY_DOWN,B_MODIFIERS_CHANGED,B_UNMAPPED_KEY_DOWN,B_REFS_RECEIVED,B_SAVE_REQUESTED,B_CANCEL,B_WINDOW_RESIZED,B_CUT,B_PASTE
	from StorageKit import B_SAVE_PANEL,B_OPEN_PANEL,B_FILE_NODE,B_READ_ONLY
	from SupportKit import B_ERROR,B_ENTRY_NOT_FOUND,B_OK,B_ANY_TYPE
except:
	print "Your python environment has no Bethon modules"
	jes = True

if jes:
	sys.exit(1)
	
class PBoolView(BView):
	def __init__(self,frame,name,imagjinV,imagjinF,stato):
		self.imagjinV=imagjinV
		self.imagjinF=imagjinF
		self.stato=stato
		self.frame=frame
		BView.__init__(self,self.frame,name,B_FOLLOW_ALL_SIDES,B_WILL_DRAW)
		
	def UpdateState(self,stato):
		self.stato=stato
		a,b,c,d=self.frame
		rect=(0,0,c-a,d-b)
		if self.stato:
			self.DrawBitmap(self.imagjinV,rect)
		else:
			self.DrawBitmap(self.imagjinF,rect)
			
	def GetState(self):
		return self.stato

	def Draw(self,rect):
		BView.Draw(self,rect)
		a,b,c,d=self.frame
		rect=(0,0,c-a,d-b)
		if self.stato:
			self.DrawBitmap(self.imagjinV,rect)
		else:
			self.DrawBitmap(self.imagjinF,rect)
			
class PeopleBView(BBox):
	def __init__(self,frame,name,lang,team,pemail,temail,default,encod):
		self.frame=frame
		self.name=name
		BBox.__init__(self,self.frame,name,B_FOLLOW_LEFT | B_FOLLOW_TOP,B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		bounds=self.Bounds()
		l,t,r,b = bounds
		h=round(self.GetFontHeight()[0])
		self.username = BTextControl((20, 16, r - 50, h + 18 ), 'name', 'Profile name:', name, BMessage(6))#b - 16
		self.lang = BTextControl((20, 32 + h, r - 50, 2*h + 50), 'lang', 'Language:', lang, BMessage(7))
		self.team = BTextControl((20, 48 + 2*h, r - 50, 3*h + 66), 'team', 'Team name:', team, BMessage(8))
		self.pemail = BTextControl((20, 64 + 3*h, r - 50, 4*h + 82), 'pemail', 'Personal e-mail:', pemail, BMessage(9))
		self.temail = BTextControl((20, 80 + 4*h, r - 50, 5*h + 98), 'temail', 'Team e-mail:', temail, BMessage(10))
		self.default = BCheckBox((20, 5*h + 101, r - 150, 6*h + 119),'chkdef','Active user',BMessage(150380))
		self.encod = BTextControl((120, 96 + 5*h, r - 50, 6*h + 119), 'encod', 'User encoding:', encod, BMessage(11))
		if default:
			self.default.SetValue(1)
		else:
			self.default.SetValue(0)
		self.AddChild(self.username)
		self.AddChild(self.lang)
		self.AddChild(self.team)
		self.AddChild(self.pemail)
		self.AddChild(self.temail)
		self.AddChild(self.default)
		if setencoding:
			self.AddChild(self.encod)

class POmetadata(BWindow):
	kWindowFrame = (150, 150, 585, 480)
	kWindowName = "POSettings"
	
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		self.listBTextControl=[]
		self.indexroot=BApplication.be_app.WindowAt(0).postabview.Selection()
		
	def MessageReceived(self, msg):
		if msg.what == 99111: # elaborate pofile
			conta=self.underframe.CountChildren()
			while conta > 0:
				self.underframe.ChildAt(conta).RemoveSelf()
				conta=conta-1

			self.metadata = self.pofile.ordered_metadata()
			
			rect = [10,10,425,30]
			step = 34
			
			indexstring=0
			for item in self.metadata:
				modmsg=BMessage(51973)
				modmsg.AddString('itemstring',item[0])
				modmsg.AddInt8('itemindex',indexstring)
				self.listBTextControl.append(BTextControl((rect[0],rect[1]+step*indexstring,rect[2],rect[3]+step*indexstring),'txtctrl'+str(indexstring),item[0],item[1],modmsg))
				indexstring+=1

			if (self.kWindowFrame[3]-self.kWindowFrame[1])< rect[3]+step*(indexstring):
				self.ResizeTo(self.Bounds()[2],float(rect[3]+step*(indexstring)-20))
				
			for element in self.listBTextControl:
				self.underframe.AddChild(element)

		if msg.what == 51973:
			# save metadata to self.pofile
			ind=msg.FindString('itemstring')
			indi=msg.FindInt8('itemindex')
			self.pofile.metadata[ind]=self.listBTextControl[indi].Text().decode(BApplication.be_app.WindowAt(0).encoding)   ################### possible error? check encoding
			# save self.pofile to backup file
			smesg=BMessage(16893)
			smesg.AddInt8('savetype',2)
			smesg.AddInt8('indexroot',self.indexroot)
			smesg.AddString('bckppath',BApplication.be_app.WindowAt(0).editorslist[self.indexroot].backupfile)
			BApplication.be_app.WindowAt(0).PostMessage(smesg)


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
		
		
class ImpostazionsUtent(BWindow):
	kWindowFrame = (150, 150, 585, 480)
	kWindowName = "User Settings"
	global confile
	
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		h=round(self.underframe.GetFontHeight()[0])
		self.userstabview = BTabView((5.0, 5.0, r-5, t+6*h+190), 'tabview')
		altece = self.userstabview.TabHeight()
		tfr = (10.0, 10.0, r-25, t+6*h+170 - altece)
		trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])
		self.tabslabels=[]
		self.userviewlist=[]
		try:
			Config.read(confile)
			defaultuser = ConfigSectionMap("Users")['default']
			names=ConfigSectionMap("Users")['names']
			listu = names.split(';')
			listu.pop(len(listu)-1) #last item is ""
			x=0
			while x<len(listu):
				name=ConfigSectionMap(listu[x])['name']
				lang=ConfigSectionMap(listu[x])['lang']
				team=ConfigSectionMap(listu[x])['team']
				pemail=ConfigSectionMap(listu[x])['pe-mail']
				temail=ConfigSectionMap(listu[x])['te-mail']
				#print setencoding
				if setencoding:
					try:
						thisencoding=ConfigSectionMap(listu[x])['encoding']
					except:
						thisencoding = 'utf-8'
				else:
					thisencoding = 'utf-8'
				if name == defaultuser:
					self.userviewlist.append(PeopleBView(tfr,name,lang,team,pemail,temail,True,thisencoding))
				else:
					self.userviewlist.append(PeopleBView(tfr,name,lang,team,pemail,temail,False,thisencoding))
				self.tabslabels.append(BTab())
				self.userstabview.AddTab(self.userviewlist[x], self.tabslabels[x])
				x=x+1
			self.underframe.AddChild(self.userstabview)
			kButtonFrame1 = (r/4+5, t+6*h+200, r/2-5, b-5)
			kButtonName1 = "Remove user"
			kButtonFrame2 = (r*3/4+5, t+6*h+200, r-5, b-5)
			kButtonName2 = "Add user"
			kButtonFrame3 = (r/2+5, t+6*h+200, r*3/4-5, b-5)
			kButtonName3 = "Set default"
			self.gjaveBtn = BButton(kButtonFrame1, kButtonName1, kButtonName1, BMessage(50250))
			self.zonteBtn = BButton(kButtonFrame2, kButtonName2, kButtonName2, BMessage(550250))
			self.underframe.AddChild(self.gjaveBtn)
			self.underframe.AddChild(self.zonteBtn)
		except:
			say = BAlert('Oops', 'No/Wrong config file or users found', 'Ok',None, None, None, 3)
			say.Go()
			self.Quit()
			
		


	def MessageReceived(self, msg):
		if msg.what == 550250:    #Create new user
			self.maacutent = MaacUtent(False)
			self.maacutent.Show()
			self.Quit()
			return
		elif msg.what == 50250:   #Remove user
			index=self.userstabview.Selection()
			Config.read(confile)
			defaultuser = ConfigSectionMap("Users")['default']
			names=ConfigSectionMap("Users")['names']
			listu = names.split(';')
			listu.pop(len(listu)-1)
			if len(listu)>1:
				if defaultuser == self.tabslabels[index].Label():
					# change the default user and remove it
					cfgfile = open(confile,'w')
					Config.remove_section(self.tabslabels[index].Label())
					newnames=names.replace((self.tabslabels[index].Label()+";"),"")
					Config.set('Users','names', newnames)
					newdefault=newnames.split(';')[0]
					Config.set('Users','default', newdefault)
					Config.write(cfgfile)
					cfgfile.close()
					self.userstabview.RemoveTab(index)
					self.tabslabels.pop(index)
					self.userviewlist.pop(index)
					listu.pop(index)
					self.userviewlist[0].default.SetValue(1)
				else:
					# remove the selected user
					cfgfile = open(confile,'w')
					Config.remove_section(self.tabslabels[index].Label())
					newnames=names.replace((self.tabslabels[index].Label()+";"),"")
					Config.set('Users','names', newnames)
					Config.write(cfgfile)
					cfgfile.close()
					self.userstabview.RemoveTab(index)
					self.tabslabels.pop(index)
					self.userviewlist.pop(index)
					listu.pop(index)
			else:
				say = BAlert('oops', 'Add another user before removing this one!', 'Ok',None, None, None, 3)
				say.Go()
			return
		elif msg.what == 6:			# update username
			Config.read(confile)
			cfgfile = open(confile,'w')
			index=self.userstabview.Selection()
			oldname = self.userviewlist[index].name
			defname = ConfigSectionMap("Users")['default']
			newusername = self.userviewlist[index].username.Text()
			if defname == oldname:
				Config.set('Users','default', newusername)
			newnames = ConfigSectionMap("Users")['names']
			overwritnames=newnames.replace(oldname,newusername)
			Config.set('Users','names', overwritnames)
			Config.remove_section(oldname)
			Config.add_section(newusername)
			Config.set(newusername,'name',newusername)
			Config.set(newusername,'lang',self.userviewlist[index].lang.Text())
			Config.set(newusername,'team',self.userviewlist[index].team.Text())
			Config.set(newusername,'pe-mail',self.userviewlist[index].pemail.Text())
			Config.set(newusername,'te-mail',self.userviewlist[index].temail.Text())
			Config.write(cfgfile)
			cfgfile.close()
			say = BAlert('ok', 'Username saved to config file. Reopen user setting to update the view', 'Ok',None, None, None, 3)
			say.Go()
			self.Quit()
			return
		elif msg.what == 7:			# update lang
			Config.read(confile)
			cfgfile = open(confile,'w')
			index=self.userstabview.Selection()
			user = self.userviewlist[index].name
			newlang = self.userviewlist[index].lang.Text()
			Config.set(user,'lang',newlang)
			Config.write(cfgfile)
			cfgfile.close()
			return
		elif msg.what == 8:			# update team
			Config.read(confile)
			cfgfile = open(confile,'w')
			index=self.userstabview.Selection()
			user = self.userviewlist[index].name
			newteam = self.userviewlist[index].team.Text()
			Config.set(user,'team',newteam)
			Config.write(cfgfile)
			cfgfile.close()
			return
		elif msg.what == 9:			# update pe-mail
			Config.read(confile)
			cfgfile = open(confile,'w')
			index=self.userstabview.Selection()
			user = self.userviewlist[index].name
			newpemail = self.userviewlist[index].pemail.Text()
			Config.set(user,'pe-mail',newpemail)
			Config.write(cfgfile)
			cfgfile.close()
			return
		elif msg.what == 10:		# update te-mail
			Config.read(confile)
			cfgfile = open(confile,'w')
			index=self.userstabview.Selection()
			user = self.userviewlist[index].name
			newtemail = self.userviewlist[index].temail.Text()
			Config.set(user,'te-mail',newtemail)
			Config.write(cfgfile)
			cfgfile.close()
			return
		elif msg.what == 11:
			cfgfile = open(confile,'w')
			index=self.userstabview.Selection()
			user = self.userviewlist[index].name
			newenc = self.userviewlist[index].encod.Text()
			Config.set(user,'encoding',newenc)
			Config.write(cfgfile)
			cfgfile.close()
			return
		elif msg.what == 150380:    #Change default user
			Config.read(confile)
			defaultuser = ConfigSectionMap("Users")['default']
			names=ConfigSectionMap("Users")['names']
			listu = names.split(';')
			listu.pop(len(listu)-1)
			index=self.userstabview.Selection()
			if len(listu)>1:
				if listu[index] == defaultuser:
					say = BAlert('oops', 'There should be just one default user. Set as default another user!', 'Ok',None, None, None, 3)
					say.Go()
					self.userviewlist[index].default.SetValue(1)
				else:	
					x=0
					while x<len(listu):
						if x==index:
							self.userviewlist[x].default.SetValue(1)
							cfgfile = open(confile,'w')
							Config.set('Users','default', self.userviewlist[x].name)
							Config.write(cfgfile)
							cfgfile.close()
						else:
							self.userviewlist[x].default.SetValue(0)
						x=x+1			
			else:
				say = BAlert('oops', 'You have configured only one user which should be the default one. Create another one!', 'Ok',None, None, None, 3)
				say.Go()
				self.userviewlist[0].default.SetValue(1)

			return

	def QuitRequested(self):
		BApplication.be_app.WindowAt(0).PostMessage(777)
		self.Quit()
		return 0


class GeneralSettings(BWindow):
	global setencoding
	kWindowFrame = (250, 150, 755, 297)
	kWindowName = "General Settings"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		self.encustenc = BCheckBox((5,49,r-15,74),'customenc', 'Check for custom encoding', BMessage(222))
		self.langcheck = BCheckBox((5,79,r-15,104),'langcheck', 'Check language compliance between pofile and user', BMessage(242))
		self.mimecheck = BCheckBox((5,109,r-15,134),'mimecheck', 'Check mimetype of file', BMessage(262))
		self.underframe.AddChild(self.encustenc)
		self.underframe.AddChild(self.langcheck)
		self.underframe.AddChild(self.mimecheck)
		Config.read(confile)
		try:
			custenccheck = Config.getboolean('Settings','customenc')
			if custenccheck:
				self.encustenc.SetValue(1)
			else:
				self.encustenc.SetValue(0)
		except:
			print "eccezione creo customenc in config.ini"
			cfgfile = open(confile,'w')
			if setencoding:
				Config.set('Settings','customenc', "True")
			else:
				Config.set('Settings','customenc', "False")
			Config.write(cfgfile)
			self.encustenc.SetValue(setencoding)
			cfgfile.close()
		try:
			#langcheck
			checklang = Config.getboolean('Settings','checklang')
			if checklang:
				self.langcheck.SetValue(1)
			else:
				self.langcheck.SetValue(0)
		except:
			print "eccezione creo checklang in config.ini"
			cfgfile = open(confile,'w')
			Config.set('Settings','checklang', "True")
			Config.write(cfgfile)
			self.langcheck.SetValue(1)
			cfgfile.close()
		try:
			mimecheck = Config.getboolean('Settings','mimecheck')
			if mimecheck:
				self.mimecheck.SetValue(1)
			else:
				self.mimecheck.SetValue(0)
		except:
			print "eccezione creo mimecheck in config.ini"
			cfgfile = open(confile,'w')
			Config.set('Settings','mimecheck', "True")
			Config.write(cfgfile)
			self.mimecheck.SetValue(1)
			cfgfile.close()

	def MessageReceived(self, msg):
		if msg.what == 222:
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				if self.encustenc.Value():
					Config.set('Settings','customenc', "True")
					Config.write(cfgfile)
					setencoding = True
				else:
					Config.set('Settings','customenc', "False")
					Config.write(cfgfile)
					setencoding = False
			except:
				print "Error setting up custom encoding, missing config section?"
			cfgfile.close()
		elif msg.what == 242:
			Config.read(confile)
			cfgfile = open(confile,'w')
			try:
				if self.langcheck.Value():
					Config.set('Settings','checklang', "True")
					Config.write(cfgfile)
				else:
					Config.set('Settings','checklang', "False")
					Config.write(cfgfile)
			except:
				print "Error enabling language compliance check, missing config section?"
			cfgfile.close()
		elif msg.what == 262:
			cfgfile = open(confile,'w')
			try:
				if self.mimecheck.Value():
					Config.set('Settings','mimecheck', "True")
					Config.write(cfgfile)
				else:
					Config.set('Settings','mimecheck', "False")
					Config.write(cfgfile)
			except:
				print "Error enabling mimechecking, missing config section?"
			cfgfile.close()

class TMSettings(BWindow):
	kWindowFrame = (250, 150, 755, 240)
	kWindowName = "Translation Memory Settings"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		Config.read(confile)
		self.enablecheck = BCheckBox((5,5,r-5,18),'enabcheck', 'Enable/Disable translation memory', BMessage(222))
		if tm:
			self.enablecheck.SetValue(1)
		else:
			self.enablecheck.SetValue(0)
		try:
			usero = ConfigSectionMap("Users")['default']
			bret = ConfigSectionMap(usero)['tmxsrv']
		except:
			bret = "127.0.0.1"
		self.tmxsrvBTC = BTextControl((5,27,r-5,49),'tmxsrv','Server address:',bret,BMessage(8080))
		try:
			usero = ConfigSectionMap("Users")['default']
			bret = ConfigSectionMap(usero)['tmxprt']
		except:
			bret = "2022"
		self.tmxprtBTC = BTextControl((5,51,r-5,73),'tmxprt','Server port:',bret,BMessage(8086))
		self.underframe.AddChild(self.enablecheck)
		self.underframe.AddChild(self.tmxsrvBTC)
		self.underframe.AddChild(self.tmxprtBTC)

	def MessageReceived(self, msg):
		if msg.what == 222:
			cfgfile = open(confile,'w')
			try:
				if self.enablecheck.Value():
					Config.set('Settings','tm', "True")
					Config.write(cfgfile)
				else:
					Config.set('Settings','tm', "False")
					Config.write(cfgfile)
			except:
				print "Error writing tm setting in config.ini, missing config section?"
			cfgfile.close()
		elif msg.what == 8080:
			try:
				usero = ConfigSectionMap("Users")['default']
				cfgfile = open(confile,'w')
				try:
					Config.set(usero,'tmxsrv',self.tmxsrvBTC.Text())
					Config.write(cfgfile)
				except:
					print "Cannot save TM server address"
				cfgfile.close()
			except:
				print "Error reading default user"
		elif msg.what == 8086:
			try:
				usero = ConfigSectionMap("Users")['default']
				cfgfile = open(confile,'w')
				try:
					Config.set(usero,'tmxprt',int(self.tmxprtBTC.Text()))
					Config.write(cfgfile)
				except:
					print "Cannot save TM server port"
				cfgfile.close()
			except:
				print "Error reading default user"
		
class SpellcheckSettings(BWindow):
	kWindowFrame = (250, 150, 755, 297)
	kWindowName = "Spellchecking Settings"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		Config.read(confile)
		self.enablecheck = BCheckBox((5,5,r-5,18),'enabcheck', 'Enable/Disable spellcheck', BMessage(222))
		if showspell:
			self.enablecheck.SetValue(1)
		else:
			self.enablecheck.SetValue(0)
		try:
			bret = ConfigSectionMap("Settings")['spell_path'] #it's ascii
		except:
			bret = "hunspell-x86"
		self.splchker = BTextControl((5,27,r-5,49),'spellchecker','Spellchecker command:',bret,BMessage(8080))
		try:
			usero = ConfigSectionMap("Users")['default']
			bret = ConfigSectionMap(usero)['spell_dictionary'] #it's ascii
		except:
			bret = "/boot/system/data/hunspell/en_US"
			
		self.diz = BTextControl((5,51,r-5,73),'dictionary','Dictionary path:',bret,BMessage(8086))
		try:
			usero = ConfigSectionMap("Users")['default']
			bret = ConfigSectionMap(usero)['spell_inclusion']
		except:
			bret = ""
		self.inclus = BTextControl((5,75,r-5,97),'inclusion','Chars included in words:',bret,BMessage(8087))
		try:
			usero = ConfigSectionMap("Users")['default']
			bret = ConfigSectionMap(usero)['spell_esclusion']
		except:
			bret = ""
		self.esclus = BTextControl((5,99,r-5,121),'inclusion','Chars-categories escluded in words:',bret,BMessage(8088))
		self.esclus.SetText("Pc,Pd,Pe,Pi,Po,Ps,Cc,Pf")
		self.underframe.AddChild(self.splchker)
		self.underframe.AddChild(self.enablecheck)
		self.underframe.AddChild(self.diz)
		self.underframe.AddChild(self.inclus)
		self.underframe.AddChild(self.esclus)
		
	def MessageReceived(self, msg):
		if msg.what == 222:
			cfgfile = open(confile,'w')
			try:
				if self.enablecheck.Value():
					Config.set('Settings','spellchecking', "True")
					Config.write(cfgfile)
				else:
					Config.set('Settings','spellchecking', "False")
					Config.write(cfgfile)
			except:
				print "Error enabling spellcheck, missing config section?"
			cfgfile.close()
		elif msg.what == 8080:
			if find_executable(self.splchker.Text()):
				cfgfile = open(confile,'w')
				try:
					Config.set('Settings','spell_path',self.splchker.Text())
					Config.write(cfgfile)
				except:
					print "Cannot save spellchecker path"
				cfgfile.close()
		elif msg.what == 8086:
			if os.path.exists(self.diz.Text()+".dic"):
				Config.read(confile)
				try:
					usero = ConfigSectionMap("Users")['default']
					cfgfile = open(confile,'w')
					try:
						Config.set(usero,'spell_dictionary',self.diz.Text())
						Config.write(cfgfile)
					except:
						print "Cannot save dictionary path"
					cfgfile.close()
				except:
					print "there's no users saved"
			else:
				print "wrong path"
		elif msg.what == 8087:
				Config.read(confile)
				usero = ConfigSectionMap("Users")['default']
				cfgfile = open(confile,'w')
				try:
					Config.set(usero,'spell_inclusion',self.inclus.Text())
					Config.write(cfgfile)
				except:
					print "Cannot save inclusion chars"
				cfgfile.close()
				Config.read(confile)
				inctxt=ConfigSectionMap(usero)['spell_inclusion']
				inclusion = inctxt.split(",")
		elif msg.what == 8088:
				Config.read(confile)
				usero = ConfigSectionMap("Users")['default']
				cfgfile = open(confile,'w')
				try:
					Config.set(usero,'spell_esclusion',self.esclus.Text())
					Config.write(cfgfile)
				except:
					print "Cannot save esclusion chars"
				cfgfile.close()
				Config.read(confile)
				esctxt=ConfigSectionMap(usero)['spell_esclusion']
				esclusion=esctxt.split(",")

class Findsource(BWindow):
	kWindowFrame = (250, 150, 655, 226)
	kWindowName = "Find source"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		h=round(self.underframe.GetFontHeight()[0])
		kButtonFrame1 = (r/2+15,b-40,r-5,b-5)
		kButtonName1 = "Search"
		self.SearchButton = BButton(kButtonFrame1, kButtonName1, kButtonName1, BMessage(5348))
		self.underframe.AddChild(self.SearchButton)
		self.casesens = BCheckBox((5,b-30,r/2-15,b-5),'casesens', 'Case sensistive', BMessage(222))
		self.casesens.SetValue(1)
		self.underframe.AddChild(self.casesens)
		self.looktv=BTextControl((5,5,r-5,32),'txttosearch','Search:','',BMessage(8046))
		self.looktv.SetDivider(60.0)
		self.underframe.AddChild(self.looktv)
		self.looktv.MakeFocus()
		self.encoding=BApplication.be_app.WindowAt(0).editorslist[BApplication.be_app.WindowAt(0).postabview.Selection()].encodo#encoding
		#self.encoding = BApplication.be_app.WindowAt(0).encoding


	def MessageReceived(self, msg):
	
		if msg.what == 5348:
			if self.looktv.Text() != "":
				lista=BApplication.be_app.WindowAt(0).editorslist[BApplication.be_app.WindowAt(0).postabview.Selection()].list.lv
				total=lista.CountItems()
				indaco=lista.CurrentSelection()
				if indaco>-1:
					savin=False
					object=lista.ItemAt(indaco)
					if object.hasplural:
						if object.tosave:
							savin = True
						if not savin:
							listar=BApplication.be_app.WindowAt(0).listemsgstr
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
						if BApplication.be_app.WindowAt(0).listemsgstr[0].trnsl.tosave:
							savin = True
					if savin:
						BApplication.be_app.WindowAt(0).listemsgstr[0].trnsl.Save()
				tl = len(self.looktv.Text())
				max = total
				now = indaco
				partial = False
				partiali = False
				loopa =True
				while loopa:
					now+=1
					if now < total:
						if self.casesens.Value():
							item = lista.ItemAt(now)
							if item.hasplural:
								ret = item.msgids[0].encode(self.encoding).find(self.looktv.Text())
								if ret >-1:
									lista.Select(now) #evidenziare-correggere
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									#messace.AddInt8('index',0)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									break
								ret = item.msgids[1].encode(self.encoding).find(self.looktv.Text())
								if ret >-1:
									lista.Select(now)
									messace=BMessage(963741)
									messace.AddInt8('plural',1)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									#messace.AddInt8('index',1)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									break
							else:
								ret = item.msgids.encode(self.encoding).find(self.looktv.Text())
								if ret >-1:
									lista.Select(now)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									#messace.AddInt8('index',0)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									break
					
						else:
							item = lista.ItemAt(now)
							if item.hasplural:
								ret = item.msgids[0].encode(self.encoding).lower().find(self.looktv.Text().lower())
								if ret >-1:
									lista.Select(now)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									break
								ret = item.msgids[1].encode(self.encoding).lower().find(self.looktv.Text().lower())
								if ret >-1:
									lista.Select(now)
									messace=BMessage(963741)
									messace.AddInt8('plural',1)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									break
							else:
								ret = item.msgids.encode(self.encoding).lower().find(self.looktv.Text().lower())
								if ret >-1:
									lista.Select(now)
									messace=BMessage(963741)
									messace.AddInt8('plural',0)
									messace.AddInt32('inizi',ret)
									messace.AddInt32('fin',ret+tl)
									messace.AddInt8('srctrnsl',0)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									break
					if now == total:
						now = -1
						total = indaco+1
						partial = True
					if now == indaco:
						partiali = True
					if partial and partiali:
						loopa=False
						say = BAlert('not_found', 'No matches found on other entries', 'Ok',None, None, None, 3)
						say.Go()

class FindRepTrans(BWindow):
	kWindowFrame = (250, 150, 755, 297)
	kWindowName = "Find/Replace translation"
	def __init__(self):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
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
		self.ReplaceButton = BButton(kButtonFrame2, kButtonName2, kButtonName2, BMessage(7047))
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
		lista=BApplication.be_app.WindowAt(0).editorslist[BApplication.be_app.WindowAt(0).postabview.Selection()].list.lv
		total=lista.CountItems()
		self.pb.SetMaxValue(float(total))
		indaco=lista.CurrentSelection()
		self.pb.Update(float(indaco))
		#self.encoding=BApplication.be_app.WindowAt(0).encoding
		self.encoding = BApplication.be_app.WindowAt(0).editorslist[BApplication.be_app.WindowAt(0).postabview.Selection()].encodo
		i = 1
		w = BApplication.be_app.CountWindows()
		while w > i:
			if BApplication.be_app.WindowAt(i).Title()==self.kWindowName:
				self.thiswindow=i
			i=i+1

	def MessageReceived(self, msg):
		if msg.what == 5348:
		  if self.looktv.Text() != "":
			self.pof=BApplication.be_app.WindowAt(0).editorslist[BApplication.be_app.WindowAt(0).postabview.Selection()].pofile
			lista=BApplication.be_app.WindowAt(0).editorslist[BApplication.be_app.WindowAt(0).postabview.Selection()].list.lv
			indaco=lista.CurrentSelection()
			if indaco>-1:
					savin=False
					object=lista.ItemAt(indaco)
					if object.hasplural:
						if object.tosave:
							savin = True
						if not savin:
							listar=BApplication.be_app.WindowAt(0).listemsgstr
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
						if BApplication.be_app.WindowAt(0).listemsgstr[0].trnsl.tosave:
							savin = True
					if savin:
						BApplication.be_app.WindowAt(0).listemsgstr[0].trnsl.Save()
			self.arrayview=BApplication.be_app.WindowAt(0).poview
			total=lista.CountItems()
			applydelta=float(indaco-self.pb.CurrentValue())
			deltamsg=BMessage(7047)
			deltamsg.AddFloat('delta',applydelta)
			BApplication.be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
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
						BApplication.be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
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
										BApplication.be_app.WindowAt(0).PostMessage(epistola)
										loopa = False
										break
							else:
								ret = blister.msgstrs.encode(self.encoding).find(self.looktv.Text())
								if ret >-1:
									lista.Select(now)
									epistola.AddInt8('plural',0)
									epistola.AddInt32('inizi',ret)
									epistola.AddInt32('fin',ret+tl)
									epistola.AddInt8('srctrnsl',1)
									BApplication.be_app.WindowAt(0).PostMessage(epistola)
									loopa = False
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
										BApplication.be_app.WindowAt(0).PostMessage(epistola)
										loopa = False
										break
							else:
								ret = blister.msgstrs.encode(self.encoding).lower().find(self.looktv.Text().lower())
								if ret >-1:
									lista.Select(now)
									epistola.AddInt8('plural',0)
									epistola.AddInt32('inizi',ret)
									epistola.AddInt32('fin',ret+tl)
									epistola.AddInt8('srctrnsl',1)
									BApplication.be_app.WindowAt(0).PostMessage(epistola)
									loopa = False
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
		elif msg.what == 1010:
#			lftxt=
			self.looktv.SetText(msg.FindString('txt'))
			return
		return
		
class MaacUtent(BWindow):
	kWindowFrame = (250, 150, 555, 290)
	kWindowName = "User Wizard"
	BUTTON_MSG = struct.unpack('!l', 'PRES')[0]
	global confile
	email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

	def __init__(self,firstime):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		self.firstime=firstime
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		h=round(self.underframe.GetFontHeight()[0])
		kButtonFrame1 = (2, t+2*h+12, r/2-2, b-2)
		kButtonName1 = "Dismiss"
		kButtonFrame2 = (r/2+2, t+2*h+12, r-2, b-2)
		kButtonName2 = "Proceed"
		kButtonFrame3 = (r/2+4,t+184,r-9,t+216)
		kButtonName3 = "Create"
		self.AddChild(self.underframe)
		if self.firstime:
			self.introtxt=BStringView((l+2,t+2,r-2,t+h+4),"introtxt","No users defined, insert your user profile", B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT)
		else:
			self.introtxt=BStringView((l+2,t+2,r-2,t+h+4),"introtxt","Add a new user profile?", B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT)
		self.introtxt2=BStringView((l+2,t+h+4,r-2,t+2*h+6),"introtxt","Data will be saved on a plain text file in your disc", B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT)
		self.underframe.AddChild(self.introtxt)
		self.underframe.AddChild(self.introtxt2)
		self.CloseButton = BButton(kButtonFrame1, kButtonName1, kButtonName1, BMessage(self.BUTTON_MSG))
		self.ProceedButton = BButton(kButtonFrame2, kButtonName2, kButtonName2, BMessage(295050))
		self.CreatePButton = BButton(kButtonFrame3, kButtonName3, kButtonName3, BMessage(380220))
		self.underframe.AddChild(self.CloseButton)
		self.underframe.AddChild(self.ProceedButton)

	def MessageReceived(self, msg):
		if msg.what == self.BUTTON_MSG:
			if self.firstime:
				say = BAlert('Ask again?', 'Do you wish be prompted again?', 'Yes','No', None, None , 3)
				out=say.Go()
				if out == 1:
					if not self.firstime:
						cfgfile = open(confile,'w')
						Config.set('Settings','wizardprompt',False)
						Config.write(cfgfile)
						cfgfile.close()
					else:
						cfgfile = open(confile,'w')
						try:
							Config.add_section('Settings')
						except:
							pass
						Config.set('Settings','wizardprompt',False)
						Config.write(cfgfile)
						cfgfile.close()
			BApplication.be_app.WindowAt(0).PostMessage(777)
			self.Quit()
			return
		elif msg.what == 295050:
			l,t,r,b = self.Bounds()
			self.introtxt2.Hide()
			self.ProceedButton.Hide()
			self.CloseButton.Hide()
			self.ResizeBy(0.0,100.0)
			h=round(self.underframe.GetFontHeight()[0])
			self.introtxt.SetText('Fill the fields below')
			self.name = BTextControl((l + 20, t + 16, r - 50, t + h + 18 ), 'name', 'Profile name:', '', BMessage(1))#b - 16
			self.lang = BTextControl((l + 20, t + 32 + h, r - 50, t + 2*h + 50), 'lang', 'Language:', '', BMessage(2))
			self.team = BTextControl((l + 20, t + 48 + 2*h, r - 50, t + 3*h + 66), 'team', 'Team name:', '', BMessage(3))
			self.pemail = BTextControl((l + 20, t + 64 + 3*h, r - 50, t + 4*h + 82), 'pemail', 'Personal e-mail:', '', BMessage(4))
			self.temail = BTextControl((l + 20, t + 80 + 4*h, r - 50, t + 5*h + 98), 'temail', 'Team e-mail:', '', BMessage(5))
			
			self.underframe.AddChild(self.name)
			self.underframe.AddChild(self.lang)
			self.underframe.AddChild(self.team)
			self.underframe.AddChild(self.pemail)
			self.underframe.AddChild(self.temail)
			link1=sys.path[0]+'/data/dialog-ok-apply.bmp'
			link2=sys.path[0]+'/data/window-close.bmp'
			self.img1=BTranslationUtils.GetBitmap(link1)
			self.img2=BTranslationUtils.GetBitmap(link2)
			self.namecheck=PBoolView((r-41,t+16,r-9,t+44),"namecheck",self.img1,self.img2,False)
			self.langcheck=PBoolView((r-41,t+47,r-9,t+75),"langcheck",self.img1,self.img2,False)
			self.teamcheck=PBoolView((r-41,t+78,r-9,t+106),"teamcheck",self.img1,self.img2,False)
			self.pemailcheck=PBoolView((r-41,t+109,r-9,t+137),"pemailcheck",self.img1,self.img2,False)
			self.temailcheck=PBoolView((r-41,t+140,r-9,t+168),"temailcheck",self.img1,self.img2,False)
			self.underframe.AddChild(self.namecheck)
			self.underframe.AddChild(self.langcheck)
			self.underframe.AddChild(self.teamcheck)
			self.underframe.AddChild(self.pemailcheck)
			self.underframe.AddChild(self.temailcheck)
			self.underframe.AddChild(self.CreatePButton)
			return
			
		elif msg.what == 380220:
			i = 1
			w = BApplication.be_app.CountWindows()
			while w > i:
				if BApplication.be_app.WindowAt(i).Title()==self.kWindowName:
					thiswindow=i
				i=i+1
			BApplication.be_app.WindowAt(thiswindow).PostMessage(1)
			BApplication.be_app.WindowAt(thiswindow).PostMessage(2)
			BApplication.be_app.WindowAt(thiswindow).PostMessage(3)
			BApplication.be_app.WindowAt(thiswindow).PostMessage(4)
			BApplication.be_app.WindowAt(thiswindow).PostMessage(5)
			BApplication.be_app.WindowAt(thiswindow).PostMessage(210220)
			return
			
		elif msg.what == 210220:
			if self.namecheck.GetState() and self.langcheck.GetState() and self.teamcheck.GetState() and self.pemailcheck.GetState() and self.temailcheck.GetState():
				##### sezione per creare l'utente nel file ini
				sectname = self.name.Text()#.replace(" ","") no needed
				if not self.firstime:
					Config.read(confile)
					names=ConfigSectionMap("Users")['names']
					if names.find(sectname)>-1:
						say = BAlert('What', 'The user already exists. Nothing to do', 'Ok',None, None, None, 3)
						say.Go()
						return
					else:
						cfgfile = open(confile,'w')
				else:
					names=""
					cfgfile = open(confile,'w')
					Config.add_section('Users')

				Config.set('Users','names', (names+sectname+";"))
				Config.set('Users','default', sectname)
				Config.add_section(sectname)
				Config.set(sectname,'name', self.name.Text())
				Config.set(sectname,'lang', self.lang.Text())
				Config.set(sectname,'team', self.team.Text())
				Config.set(sectname,'pe-mail', self.pemail.Text())
				Config.set(sectname,'te-mail', self.temail.Text())
				Config.write(cfgfile)
				cfgfile.close()
				say = BAlert('yeah', 'User added successfully. It\'s the default one now.', 'Ok',None, None, None, 3)
				say.Go()
				BApplication.be_app.WindowAt(0).PostMessage(777)
				self.Quit()
				return
			else:
				say = BAlert('oops', 'Check failed. Compile properly the fields and try again', 'Ok',None, None, None, 3)
				say.Go()
				return
			
		elif msg.what == 1:
			non=self.name.Text()
			if non=="":
				self.namecheck.UpdateState(False)
			else:
				#check for (no " ") and no ";"
				if non.find(';') > -1:
					say = BAlert('oops', 'Name should not include the ; character', 'Ok',None, None, None, 3)
					say.Go()
					self.namecheck.UpdateState(False)
				else:
					self.namecheck.UpdateState(True)
			return
		elif msg.what == 2:
			if self.lang.Text()=="":
				self.langcheck.UpdateState(False)
			else:
				self.langcheck.UpdateState(True)
			return
		elif msg.what == 3:
			if self.team.Text()=="":
				self.teamcheck.UpdateState(False)
			else:
				self.teamcheck.UpdateState(True)
			return
		elif msg.what == 4:
			pemailing=self.pemail.Text()
			if pemailing=="":
				self.pemailcheck.UpdateState(False)
			else:
				#check email correctness
				if self.email_regex.match(pemailing):
					self.pemailcheck.UpdateState(True)
				else:
					say = BAlert('oops', 'Personal e-mail is not a valid e-mail', 'Ok',None, None, None, 3)
					say.Go()
					self.pemailcheck.UpdateState(False)
			return
		elif msg.what == 5:
			temailing=self.temail.Text()
			if temailing=="":
				self.temailcheck.UpdateState(False)
			else:
				#check email correctness
				if self.email_regex.match(temailing):
					self.temailcheck.UpdateState(True)
				else:
					say = BAlert('oops', 'Team e-mail is not a valid e-mail', 'Ok',None, None, None, 3)
					say.Go()
					self.temailcheck.UpdateState(False)
			return
		else:
			return

	def QuitRequested(self):
		BApplication.be_app.WindowAt(0).PostMessage(777)
		self.Quit()
		return 0

class PView(BView):
	def __init__(self,frame,name,immagine):
		self.immagine=immagine
		self.frame=frame
		BView.__init__(self,self.frame,name,B_FOLLOW_ALL_SIDES,B_WILL_DRAW)
		
	def UpdateImg(self,immagine):
		self.immagine=immagine
		a,b,c,d=self.frame
		rect=(0,0,c-a,d-b)
		self.DrawBitmap(self.immagine,rect)

	def Draw(self,rect):
		BView.Draw(self,rect)
		a,b,c,d=self.frame
		rect=(0,0,c-a,d-b)
		self.DrawBitmap(self.immagine,rect)

class AboutWindow(BWindow):
	kWindowFrame = (50, 50, 600, 730)
	kButtonFrame = (kWindowFrame[2]-205,kWindowFrame[3]-89,kWindowFrame[2]-54,kWindowFrame[3]-54)#(395, 641, 546, 676)
	kWindowName = "About"
	kButtonName = "Close"
	BUTTON_MSG = struct.unpack('!l', 'PRES')[0]

	def __init__(self):							
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_MODAL_WINDOW, B_NOT_RESIZABLE)
		brec=self.Bounds()
		bbox=BBox(brec, 'underbox', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(bbox)
		self.CloseButton = BButton(self.kButtonFrame, self.kButtonName, self.kButtonName, BMessage(self.BUTTON_MSG))
		zxc,xcv,cvb,vbn=brec
		cise=(4,4,cvb-4,vbn-44)
		cjamput=(4,0,cvb-14,vbn-48)
		self.messagjio= BTextView(cise, 'TxTView', cjamput, B_FOLLOW_ALL, B_WILL_DRAW)
		self.messagjio.SetStylable(1)
		self.messagjio.MakeSelectable(0)
		self.messagjio.MakeEditable(0)		
		stuff = '\n\t\t\t\t\t\t\t\t\t'+appname+'\n\n\t\t\t\t\t\t\t\t\t\t\t\tMy personal PO editor\n\t\t\t\t\t\t\t\t\t\t\t\tfor Haiku, version '+ver+' '+state+'\n\t\t\t\t\t\t\t\t\t\t\t\tbuild 221217\n\n\t\t\t\t\t\t\t\t\t\t\t\tby Fabio Tomat\n\t\t\t\t\t\t\t\t\t\t\t\te-mail:\n\t\t\t\t\t\t\t\t\t\t\t\tf.t.public@gmail.com\n\n\n\n\n\n\nMIT LICENSE\nCopyright © 2021 Fabio Tomat\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'
		n = stuff.find(appname)
		m = stuff.find('MIT LICENSE')
		command=[(0, be_plain_font, (0, 0, 0, 0)), (n, be_bold_font, (0, 0, 0, 0)), (n + 5, be_plain_font, (100, 100, 100, 0)),(m,be_bold_font,(0,0,0,0)),(m+11,be_plain_font,(100,100,100,0))]
		self.messagjio.SetText(stuff, command)
		bbox.AddChild(self.messagjio)
		bbox.AddChild(self.CloseButton)
		self.CloseButton.MakeFocus(1)
		link=sys.path[0]+"/data/HaiPO.png"
		self.img=BTranslationUtils.GetBitmap(link)
		self.photoframe=PView((40,50,255,255),"photoframe",self.img)
		bbox.AddChild(self.photoframe)

	def MessageReceived(self, msg):
		if msg.what == self.BUTTON_MSG:
			self.Quit()
		else:
			return
			
class TranslatorComment(BWindow):
	kWindowFrame = (150, 150, 450, 300)
	kWindowName = "Translator comment"
	
	def __init__(self,listindex,indextab,item,encoding):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		ix,iy,fx,fy=bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		self.tcommentview=BTextView((4,4,fx-4,fy-50),"commentview",(4,4,fx-12,fy-48),B_FOLLOW_ALL)
		self.underframe.AddChild(self.tcommentview)
		kButtonFrame = (fx-150, fy-40, fx-10, fy-10)
		kButtonName = "Save comment"
		self.savebtn = BButton(kButtonFrame, kButtonName, kButtonName, BMessage(5252))
		self.underframe.AddChild(self.savebtn)
		self.item=item
		self.indextab=indextab
		self.listindex=listindex
		self.encoding=encoding
		if self.item.tcomment!="":
			self.tcommentview.SetText(self.item.tcomment.encode(self.encoding))
		
	def Save(self):
		bckpmsg=BMessage(16893)
		cursel=BApplication.be_app.WindowAt(0).editorslist[self.indextab]
		bckpmsg.AddInt8('savetype',3)
		bckpmsg.AddInt32('tvindex',self.listindex)
		bckpmsg.AddInt32('tabview',self.indextab)
		bckpmsg.AddString('tcomment',self.item.tcomment)
		bckpmsg.AddString('bckppath',cursel.backupfile)
		BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
		

	def MessageReceived(self, msg):
		if msg.what == 5252:
			self.item.tcomment=self.tcommentview.Text().decode(self.encoding)
			self.Save()
			BApplication.be_app.WindowAt(0).postabview.Select(self.indextab)
			BApplication.be_app.WindowAt(0).editorslist[self.indextab].list.lv.DeselectAll()
			BApplication.be_app.WindowAt(0).editorslist[self.indextab].list.lv.Select(self.listindex)
			self.Quit()
		else:	
			return BWindow.MessageReceived(self, msg)
			
class MyListView(BListView):
	def __init__(self, frame, name, type, resizingMode, flags):
		BListView.__init__(self, frame, name, type, resizingMode, flags)
		#self.preselected=-1
	
	def MouseDown(self,point):
		if self.CurrentSelection() >-1:
			if self.ItemAt(self.CurrentSelection()).hasplural:
				lmsgstr=BApplication.be_app.WindowAt(0).listemsgstr
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
				itemtext=BApplication.be_app.WindowAt(0).listemsgstr[0].trnsl
				if itemtext.tosave:
					if itemtext.Text()!= itemtext.oldtext:
						itemtext.Save()
			if showspell:
				BApplication.be_app.WindowAt(0).PostMessage(333111)
			if tm:
				cirmsg=BMessage(738033)
				cirmsg.AddString('s',self.ItemAt(self.CurrentSelection()).Text())
				BApplication.be_app.WindowAt(0).PostMessage(cirmsg)
#				thread.start_new_thread( self.tmcommunicate, (self.listemsgid[self.srctabview.Selection()].src.Text(),) )
		return BListView.MouseDown(self,point)

class KListView(BListView):
	def __init__(self,frame, name,type,align,flags):
		BListView.__init__(self, frame, name, type, align, flags)
	def KeyDown(self,char,bytes):
		if ord(char) == 127:
			delmsg=BMessage(431110173)
			delmsg.AddString("sugj",self.ItemAt(self.CurrentSelection()).Text())#check if it needs encoding
			BApplication.be_app.WindowAt(0).PostMessage(delmsg)
			self.RemoveItem(self.ItemAt(self.CurrentSelection()))
		return BListView.KeyDown(self,char,bytes)

class ScrollSugj:
	HiWhat = 141# Doubleclick --> paste to trnsl TextView
	def __init__(self, rect, name):
		self.lv = KListView(rect, name, B_SINGLE_SELECTION_LIST,B_FOLLOW_LEFT_RIGHT|B_FOLLOW_BOTTOM,B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_FRAME_EVENTS)#B_FOLLOW_ALL_SIDES
		msg = BMessage(self.HiWhat)
		self.lv.SetInvocationMessage(msg)
		self.sv = BScrollView('ScrollSugj', self.lv, B_FOLLOW_LEFT_RIGHT|B_FOLLOW_BOTTOM, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, 0, 0, B_FANCY_BORDER)#B_FOLLOW_ALL_SIDES
		
	def SelectedText(self):
		return self.lv.ItemAt(self.lv.CurrentSelection()).Text()

	def Clear(self):
		self.lv.DeselectAll()
		while self.lv.CountItems()>0:
				self.lv.RemoveItem(self.lv.ItemAt(0))

class ScrollView:
	HiWhat = 32 #Doubleclick --> open translator comment window
	Selmsgstr = 460550

	def __init__(self, rect, name):
		self.lv = MyListView(rect, name, B_SINGLE_SELECTION_LIST,B_FOLLOW_ALL_SIDES,B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_FRAME_EVENTS)
		msg=BMessage(self.Selmsgstr)
		self.lv.SetSelectionMessage(msg)
		msg = BMessage(self.HiWhat)
		self.lv.SetInvocationMessage(msg)
		self.sv = BScrollView('ScrollView', self.lv, B_FOLLOW_ALL_SIDES, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, 0, 0, B_FANCY_BORDER)

	def reload(self,arrayview,pofile,encoding):
			self.occumemo=[]
			i=0
			self.lv.DeselectAll()
			while self.lv.CountItems()>i:
				self.lv.RemoveItem(self.lv.ItemAt(0))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
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
							item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(encoding)))
						if entry.previous_msgid_plural:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
						if entry.previous_msgctxt:
							item.SetPrevious(True)
							item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(encoding)))
						item.SetLineNum(entry.linenum)					
					self.lv.AddItem(item)
			

		
	def SelectedText(self):
			return self.lv.ItemAt(self.lv.CurrentSelection()).Text()

	def topview(self):
		return self.sv

	def listview(self):
		return self.lv

class MyListItem(BListItem):
	nocolor = (0, 0, 0, 0)
	frame=[0,0,0,0]

	def __init__(self, txt):
		self.text = txt
		BListItem.__init__(self)
	
	def DrawItem(self, owner, frame,complete):
		self.frame = frame
		#complete = True
		if self.IsSelected() or complete: # 
			color = (200,200,200,255)
			owner.SetHighColor(color)
			owner.SetLowColor(color)
			owner.FillRect(frame)
		self.color = self.nocolor
		owner.SetHighColor(self.color)
		owner.MovePenTo(frame[0],frame[3]-2)
		owner.DrawString(self.text)
		owner.SetLowColor((255,255,255,255))

	def Text(self):
		return self.text

#class StringBListItem(BListItem):
#	def __init__(self,text):
#		self.text=text
#		BListItem.__init__(self)
		
#	def DrawItem(self, owner, frame,complete):
#		self.frame = frame
#		#complete = True
#		if self.IsSelected() or complete: # 
#			color = (200,200,200,255)
#			owner.SetHighColor(color)
#			owner.SetLowColor(color)
#			owner.FillRect(frame)
#			self.color = (0,0,0,0)
#		owner.SetHighColor(self.color)
#		self.font = be_plain_font
#		owner.SetFont(self.font)
#		owner.MovePenTo(frame[0]+30,frame[3]-2)
#		owner.DrawString(self.text)
class SugjItem(BListItem):
	nocolor = (0, 0, 0, 0)
	frame=[0,0,0,0]
	def __init__(self,sugj,lev):
		self.text=sugj
		tl=len(sugj)
		if deb:
			print sugj
			print tl
		self.percent=(100*(tl-lev))/tl
		BListItem.__init__(self)

	def DrawItem(self, owner, frame,complete):
		self.frame = frame
		if self.IsSelected() or complete: # 
			color = (200,200,200,255)
			owner.SetHighColor(color)
			owner.SetLowColor(color)
			owner.FillRect(frame)
		self.color = self.nocolor
		owner.MovePenTo(frame[0]+5,frame[3]-2)
		if self.percent == 100:
			self.font = be_bold_font
			tempcolor = (0,200,0,0)
		else:
			self.font = be_plain_font
			tempcolor = (20,20,20,0)
		owner.SetHighColor(tempcolor)
		owner.SetFont(self.font)
		xtxt=str(self.percent)+"%"
		owner.DrawString(xtxt)
		ww=self.font.StringWidth(xtxt)
		owner.SetHighColor(self.color)
		self.font = be_plain_font
		owner.SetFont(self.font)
		owner.MovePenTo(frame[0]+ww+10,frame[3]-2)#40
		owner.DrawString(self.text)
		
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
		if self.IsSelected() or complete: # 
			color = (200,200,200,255)
			owner.SetHighColor(color)
			owner.SetLowColor(color)
			owner.FillRect(frame)
		self.color = self.nocolor
		owner.MovePenTo(frame[0]+5,frame[3]-2)
		self.font = be_plain_font
		tempcolor = (20,20,20,0)
		owner.SetHighColor(tempcolor)
		owner.SetFont(self.font)
		owner.DrawString(self.text)
		#owner.SetHighColor(self.color)
		#self.font = be_plain_font
		#owner.SetFont(self.font)
		#owner.MovePenTo(frame[0]+40,frame[3]-2)
		#owner.DrawString(self.text)
		
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
	
	def __init__(self, msgids,msgstrs,entry,comments,context,state,encoding,plural):
		if plural:
			self.text = msgids[0].encode(encoding)  #(english) should this always be utf-8?
		else:
			self.text = msgids.encode(encoding)
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
		self.frame = frame
		#complete = True
		if self.IsSelected() or complete: # 
			color = (200,200,200,255)
			owner.SetHighColor(color)
			owner.SetLowColor(color)
			owner.FillRect(frame)
			if self.state == self.untranslated: 
				self.color = (0,0,255,0)
			elif self.state == self.translated:
				self.color = self.nocolor
			elif self.state == self.fuzzy:
				self.color = (153,153,0,0)
			elif self.state == self.obsolete:
				self.color = (150,75,0)

		if self.state == 0:
				self.color = (0,0,255,0)
		elif self.state == 1:
				self.color = self.nocolor
		elif self.state == 2:
				self.color = (153,153,0,0)
		elif self.state == 3:
				self.color = (97,10,10,0)
		
		if self.hasplural:
			owner.MovePenTo(frame[0],frame[3]-2)
			self.font = be_bold_font
			tempcolor = (200,0,0,0)
			owner.SetHighColor(tempcolor)
			owner.SetFont(self.font)
			xtxt='Pl >>'
			owner.DrawString(xtxt)
			ww=self.font.StringWidth(xtxt)
			owner.SetHighColor(self.color)
			self.font = be_plain_font
			owner.SetFont(self.font)
			owner.MovePenTo(frame[0]+ww+5,frame[3]-2)
			owner.DrawString(self.text)
		else:
			owner.SetHighColor(self.color)
			owner.MovePenTo(frame[0],frame[3]-2)
			owner.DrawString(self.text)
			owner.SetLowColor((255,255,255,255))
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
	global deb
	def __init__(self,superself,frame,name,textRect,resizingMode,flags):
		self.superself=superself
		self.oldtext=""
#		self.telptst=self.oldtext
		self.oldtextloaded=False
		self.tosave=False
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)
		self.mousemsg=struct.unpack('!l', '_MMV')[0]
		self.dragmsg=struct.unpack('!l', 'MIME')[0]
		self.dragndrop = False
		self.event= threading.Event()
		self.SetStylable(1)
		self.evstile=[]
		self.analisi=[]
		self.analyzetxt=[]
		self.pop = BPopUpMenu('popup')
		
	def Save(self):
		cursel=self.superself.editorslist[self.superself.postabview.Selection()]
		thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
		thisBlistitem.tosave=True
		tabs=len(self.superself.listemsgstr)-1
		bckpmsg=BMessage(16893)
		bckpmsg.AddInt8('savetype',1)
		bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
		bckpmsg.AddInt8('plurals',tabs)
		bckpmsg.AddInt32('tabview',self.superself.postabview.Selection())
		if tabs == 0:
			thisBlistitem.txttosave=self.Text()
			#thisBlistitem.msgstrs=self.Text().decode(self.superself.encoding)
			thisBlistitem.msgstrs=self.Text().decode(self.superself.editorslist[self.superself.postabview.Selection()].encodo)
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
		else:
			thisBlistitem.txttosavepl=[]
			thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
			thisBlistitem.msgstrs=[]
			#thisBlistitem.msgstrs.append(self.superself.listemsgstr[0].trnsl.Text().decode(self.superself.encoding))
			thisBlistitem.msgstrs.append(self.superself.listemsgstr[0].trnsl.Text().decode(self.superself.editorslist[self.superself.postabview.Selection()].encodo))
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
			cox=1
			while cox < tabs+1:
				#thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text().decode(self.superself.encoding))
				thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text().decode(self.superself.editorslist[self.superself.postabview.Selection()].encodo))
				thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
				bckpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgstr[cox].trnsl.Text())
				cox+=1
		bckpmsg.AddString('bckppath',cursel.backupfile)
		BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
		self.superself.infoprogress.SetText(str(cursel.pofile.percent_translated())) #reinsert if something doesn't work properly but it should write in 16892/3

	def checklater(self,name,oldtext,cursel,indexBlistitem):
			if deb:
				print "start checklater"
			mes=BMessage(112118)
			mes.AddInt8('cursel',cursel)
			mes.AddInt32('indexBlistitem',indexBlistitem)
			mes.AddString('oldtext',oldtext)
			self.event.wait(0.1)
			BApplication.be_app.WindowAt(0).PostMessage(mes)
			if deb:
				print "end checklater"

	def MouseUp(self,point):
		self.superself.drop.acquire()
		if self.dragndrop:
			cursel=self.superself.postabview.Selection()
			selection=self.superself.editorslist[cursel]
			indexBlistitem=selection.list.lv.CurrentSelection()
			name=time.time()
			BTextView.MouseUp(self,point)
			thread.start_new_thread( self.checklater, (str(name), self.Text(),cursel,indexBlistitem,) )
			self.dragndrop = False
			self.superself.drop.release()
			return
		self.superself.drop.release()
		if showspell:
			ubi1,ubi2 = self.GetSelection()
			if ubi1 == ubi2:
				ubi1,ubi2=self.FindWord(ubi1)
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
			cursel=self.superself.editorslist[self.superself.postabview.Selection()]
			thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
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
			if ochar in (B_DOWN_ARROW,B_UP_ARROW,10,B_PAGE_UP,B_PAGE_DOWN,10,49,50,51,52,53): #B_ENTER =10?
				self.superself.sem.acquire()
				value=self.superself.modifier #CTRL pressed
				shrtctvalue=self.superself.shortcut
				self.superself.sem.release()
				item=self.superself.editorslist[self.superself.postabview.Selection()].list.lv.ItemAt(self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection())
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
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
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
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
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
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
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
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
						return
					return BTextView.KeyDown(self,char,bytes)
				elif ochar == 49:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",0)
						BApplication.be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 50:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",1)
						BApplication.be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 51:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",2)
						BApplication.be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 52:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",3)
						BApplication.be_app.WindowAt(0).PostMessage(cpmsg)
						return
					else:
						return BTextView.KeyDown(self,char,bytes)
				elif ochar == 53:
					if shrtctvalue:
						cpmsg=BMessage(8147420)
						cpmsg.AddInt8("sel",4)
						BApplication.be_app.WindowAt(0).PostMessage(cpmsg)
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
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
						return
					else:
						if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
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
					BApplication.be_app.WindowAt(0).PostMessage(BMessage(71))
					return
				else:
					#insert b char
					if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
						self.tosave=True
						return BTextView.KeyDown(self,char,bytes)
				return
			elif ochar == B_ESCAPE: # Restore to the saved string
				self.SetText(self.oldtext)
				self.tosave=False
				thisBlistitem=self.superself.editorslist[self.superself.postabview.Selection()].list.lv.ItemAt(self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection())
				thisBlistitem.tosave=False
				thisBlistitem.txttosave=""
				#print "Seleziono la fine?"
				fine=len(self.oldtext)
				self.Select(fine,fine)
				return
			else:
				if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
					if ochar == 115:					#CTRL+SHIF+S
						self.superself.sem.acquire()
						value=self.superself.shortcut #CTRL SHIFT pressed
						self.superself.sem.release()
						if value:
							BApplication.be_app.WindowAt(0).PostMessage(33)
							return


					BTextView.KeyDown(self,char,bytes)
					if self.oldtext != self.Text():
						thisBlistitem=self.superself.editorslist[self.superself.postabview.Selection()].list.lv.ItemAt(self	.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection())
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

						BApplication.be_app.WindowAt(0).PostMessage(333111)
					return
		except:
			if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
				thisBlistitem=self.superself.editorslist[self.superself.postabview.Selection()].list.lv.ItemAt(self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection())
				thisBlistitem.tosave=True
				thisBlistitem.txttosave=self.Text()
				self.tosave=True   # This says you should save the string before proceeding
				return BTextView.KeyDown(self,char,bytes)
		
	def SetPOReadText(self,text):
		self.oldtext=text
		self.oldtextloaded=True
		self.SetText(text)
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
			self.analisi.append((unicodedata.category(unichr(ord(l[sd]))),l[sd]))  # char by char examination category print
			if sd==0:
				try:
					if l[sd]+l[sd+1] in inclusion:
						pass
					else:
						if unicodedata.category(unichr(ord(l[sd]))) in esclusion:
							l[sd]=" "
				except:
					pass
			if sd==se-1:
				try:
					if l[sd-1]+l[sd] in inclusion:
						pass
					else:
						if unicodedata.category(unichr(ord(l[sd]))) in esclusion:
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
						if unicodedata.category(unichr(ord(l[sd]))) in esclusion:
							l[sd]=" "
				except:
					pass
			sd+=1
		eltxt="".join(l)
		
		#diffeltxt=eltxt.decode(self.superself.encoding,errors='replace')
		diffeltxt=eltxt.decode(self.superself.editorslist[self.superself.postabview.Selection()].encodo,errors='replace')
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
		if deb:
			print "stdout_data:",stdout_data
		for s in stdout_data:
			if s != "":
				words=s.split()
				if deb:
#					print words
#					print newareltxt
					print "s:",s
				if s[0] == "&":
					# there are suggestions
					liw = s.find(words[3]) #string start-index that indicates the beginning of the number
					lun = len(words[3])-1  #string lenght except ":"
					iz = liw+len(words[3])+1 #string end of the number that indicates the beginning of solutions
					solutions = s[iz:]
					sugi = solutions.split(", ")
					outs = s[liw:liw+lun]   # <<<<------ number that hunspell indicates as where is the word to fix
					# here you check where is the correct byte for that hunspell-index
					if deb:
						print "outs:",outs
						print newareltxt
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
			BApplication.be_app.WindowAt(0).PostMessage(982757)
			#self.superself.checkres.SetText("☒")
			if errors[0].pos>0 or errors == []:
				stile.append((0, be_plain_font, (0, 0, 0, 0)))
				stile=startinserting(stile,errors)
			else:
				stile = startinserting(stile,errors)
		else:
			BApplication.be_app.WindowAt(0).PostMessage(735157)
			#self.superself.checkres.SetText("☑")
		
		evstyle.acquire()
		self.evstile=stile
		evstyle.release()
		posizion=self.GetSelection()
		mj=BMessage(222888)
		mj.AddInt32("start",posizion[0])
		mj.AddInt32("end",posizion[1])
		BApplication.be_app.WindowAt(0).PostMessage(mj)
				
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

class word2fix():
	def __init__(self,word,opos,pos): # opos sarà da eliminare
		self.word = word
		self.sugg = []
		self.pos = pos
		self.opos = opos
	def add(self,sugg):
		self.sugg.append(sugg)
	def many(self):
		return len(self.sugg)
	def position(self):
		return self.pos
	def strings(self):
		return self.sugg

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
		tst=unicode(hrdwrk,'utf-8')
		lis = list(tst)
		foundo = 0
		for index,ci in enumerate(lis):
			a=bytearray(ci.encode('utf-8'))
			bob=self.PointAt(index)
			a_hex=[hex(x) for x in a]
			if deb:
				print bob,index,a_hex,self.ByteAt(index),"lungh.str.:",self.TextLength()
			#print "a_hex[0]:",a_hex[0],ci.encode('utf-8')
			if len(a_hex)>1:
				i=0
				stmp=""
				while i<len(a_hex):
					stmp+="\\"+a_hex[i][1:]
					i+=1
				if deb:
					print "abbiamo un carattere multibyte",stmp
				if stmp in self.spaces:
					foundo=self.Text().find(ci.encode('utf-8'),foundo)
					asd=self.PointAt(foundo)
					foundo+=1
	 				color = (0,0,200,0)
	 				self.SetHighColor(color)
	 				self.MovePenTo((asd[0][0]+(self.font.StringWidth(ci.encode('utf-8'))/2),asd[0][1]+asd[1]-3))
	 				self.DrawString('͜')#'̳')#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
	 				color = (0,0,0,0)
	 				self.SetHighColor(color)
	 		else:
	 			mum="\\"+a_hex[0][1:]
	 			if mum in self.spaces:
		 			foundo=self.Text().find(ci.encode('utf-8'),foundo)
	 				asd=self.PointAt(foundo)
	 				foundo+=1
	 				if index+1<len(lis):
	 					a=bytearray(lis[index+1].encode('utf-8'))
		 				a_hex=[hex(x) for x in a]
		 				if len(a_hex)==1:
	 						stmp="\\"+a_hex[0][1:]
	 						if stmp in self.spaces:
	 							color = (200,0,0,0)
	 							self.SetHighColor(color)
	 							self.MovePenTo((asd[0][0]+(self.font.StringWidth(ci.encode('utf-8'))/2),asd[0][1]+asd[1]-3))
		 						self.DrawString('̳·̳')#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
		 						color = (0,0,0,0)
	 							self.SetHighColor(color)
	 						elif stmp == "\\xa":
	 							color = (200,0,0,0)
			 					self.SetHighColor(color)
		 						self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
	 							self.DrawString('̳')
		 						color = (0,0,0,0)
		 						self.SetHighColor(color)
	 						elif stmp == "\\x9":
	 							color = (200,0,0,0)
			 					self.SetHighColor(color)
		 						self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
	 							self.DrawString('̳')
		 						color = (0,0,0,0)
		 						self.SetHighColor(color)
	 					else:
	 						i=0
							stmp=""
							while i<len(a_hex):
								stmp+="\\"+a_hex[i][1:]
								i+=1
							if stmp in self.spaces:
								color = (200,0,0,0)
	 							self.SetHighColor(color)
	 							self.MovePenTo((asd[0][0]+(self.font.StringWidth(ci.encode('utf-8'))/2),asd[0][1]+asd[1]-3))
		 						self.DrawString('̳·̳')#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
		 						color = (0,0,0,0)
	 							self.SetHighColor(color)
	 				else:
	 					color = (200,0,0,0)
	 					self.SetHighColor(color)
	 					self.MovePenTo((asd[0][0]+(self.font.StringWidth(ci.encode('utf-8'))/2),asd[0][1]+asd[1]-3))
		 				self.DrawString('̳')#'.')##'_')#(' ̳')#' ᪶ ')#'˽'
		 				color = (0,0,0,0)
	 					self.SetHighColor(color)
	 			elif mum=="\\xa":
	 				foundo=self.Text().find(ci.encode('utf-8'),foundo)
	 				asd=self.PointAt(foundo)
	 				foundo+=1
	 				color = (200,0,0,0)
			 		self.SetHighColor(color)
		 			self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
		 			self.DrawString('⏎')
		 			color = (0,0,0,0)
		 			self.SetHighColor(color)
		 		elif mum=="\\x9":
	 				color = (200,0,0,0)
			 		self.SetHighColor(color)
			 		foundo=self.Text().find(ci.encode('utf-8'),foundo)
	 				asd=self.PointAt(foundo)
	 				foundo+=1
		 			self.MovePenTo((asd[0][0],asd[0][1]+asd[1]-3))
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
	 				self.DrawString(wst)
		 			color = (0,0,0,0)
		 			self.SetHighColor(color)

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
		
class srctabbox(BBox):
	def __init__(self,playground1,name,altece):
		self.name = name
		BBox.__init__(self,(0,0,playground1[2]-playground1[0],playground1[3]-playground1[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.hsrc = playground1[3] - playground1[1] - altece
		self.src = srcTextView((playground1[0],playground1[1],playground1[2]-playground1[0]-18,playground1[3]-playground1[1]),name+'_source_BTextView',(5.0,5.0,playground1[2]-30,playground1[3]-5),B_FOLLOW_ALL,B_WILL_DRAW|B_FRAME_EVENTS)
		self.src.MakeEditable(False)
		self.AddChild(self.src)
		bi,bu,bo,ba = playground1
		self.scrollbsrc=BScrollBar((bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.src,0.0,0.0,B_VERTICAL)
		self.AddChild(self.scrollbsrc)
class trnsltabbox(BBox):
	def __init__(self,playground2,name,altece,superself):
		self.name = name
		BBox.__init__(self,(0,0,playground2[2]-playground2[0],playground2[3]-playground2[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.trnsl = EventTextView(superself,(playground2[0],playground2[1],playground2[2]-playground2[0]-18,playground2[3]-playground2[1]),name+'_translation_BTextView',(5.0,5.0,playground2[2]-30,playground2[3]-5),B_FOLLOW_ALL,B_WILL_DRAW|B_FRAME_EVENTS)
		self.trnsl.MakeEditable(True)
		self.AddChild(self.trnsl)
		bi,bu,bo,ba = playground2
		self.scrollbtrans=BScrollBar((bo -20,1,bo-5,ba-5),name+'_ScrollBar',self.trnsl,0.0,0.0,B_VERTICAL)
		self.AddChild(self.scrollbtrans)

class HeaderWindow(BWindow):
	kWindowFrame = (150, 150, 500, 600)
	kWindowName = "Po header"
	
	def __init__(self,indextab,pofile,encoding):
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		bounds=self.Bounds()
		ix,iy,fx,fy=bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		self.headerview=BTextView((4,4,fx-4,fy-50),"headerview",(4,4,fx-12,fy-48),B_FOLLOW_ALL)
		self.underframe.AddChild(self.headerview)
		kButtonFrame = (fx-150, fy-40, fx-10, fy-10)
		kButtonName = "Save header"
		self.savebtn = BButton(kButtonFrame, kButtonName, kButtonName, BMessage(5252))
		self.underframe.AddChild(self.savebtn)
		self.indextab=indextab
		self.pofile=pofile
		self.encoding=encoding
		if self.pofile.header!="":
			self.headerview.SetText(self.pofile.header.encode(self.encoding))
		
	def Save(self):
		bckpmsg=BMessage(16893)
		cursel=BApplication.be_app.WindowAt(0).editorslist[self.indextab]
		bckpmsg.AddInt8('savetype',4)
		bckpmsg.AddInt32('tabview',self.indextab)
		bckpmsg.AddString('header',self.headerview.Text().decode(self.encoding))
		bckpmsg.AddString('bckppath',cursel.backupfile)
		BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
		

	def MessageReceived(self, msg):
		if msg.what == 5252:
			self.Save()
			self.Quit()
		else:
			return BWindow.MessageReceived(self, msg)


class POEditorBBox(BBox):
	def __init__(self,frame,name,percors,pofileloaded,arrayview,encoding,loadtempfile):
		self.pofile = pofileloaded
		self.name = name
		#self.encoding=encoding
		self.encodo=encoding
		if loadtempfile:
			self.backupfile = percors
			percors = percors.replace('.temp','')
			self.filen, self.file_ext = os.path.splitext(percors)
		else:
			self.filen, self.file_ext = os.path.splitext(percors)	
			self.backupfile= self.filen+".temp"+self.file_ext
		self.orderedmetadata=self.pofile.ordered_metadata()
		self.fp=BFilePanel(B_SAVE_PANEL)
		pathorig,nameorig=os.path.split(percors)
		self.fp.SetPanelDirectory(pathorig)
		self.fp.SetSaveText(nameorig)
		self.writter = threading.Semaphore()

#		if file_ext=='.po':
#			self.typefile=0
#		elif file_ext=='.mo':
#			self.typefile=1
#		elif file_ext=='.gmo':
#			self.typefile=2
#		elif file_ext=='.pot':

		ind=0
		for entry in self.pofile:
				ind=ind+1
		
		contor = frame
		a,s,d,f = contor
		BBox.__init__(self,(a,s,d-5,f-35),name,B_FOLLOW_ALL,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		contor=self.Bounds()
		l, t, r, b = contor
		self.list = ScrollView((5, 5, r -20, b-5), name+'_ScrollView')
		self.AddChild(self.list.topview())
		self.scrollb = BScrollBar((r -19,5,r-5,b-5),name+'_ScrollBar',self.list.listview(),0.0,float(ind),B_VERTICAL)#len(datab)
		self.AddChild(self.scrollb)
		self.occumemo=[]
		if arrayview[0]:
			for entry in self.pofile.fuzzy_entries():
				item=None
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
					item.SetLineNum(entry.linenum)
				self.list.lv.AddItem(item)
		if arrayview[1]:
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
					item.SetLineNum(entry.linenum)
				self.list.lv.AddItem(item)
		if arrayview[2]:
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
					item.SetLineNum(entry.linenum)
				self.list.lv.AddItem(item)
		if arrayview[3]:
			for entry in self.pofile.obsolete_entries():
				if entry and entry.msgid_plural:
					if entry.comment:
						comments = entry.comment
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
					item.SetLineNum(entry.linenum)
				else:
					if entry.comment:
						comments = entry.comment
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
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encodo)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encodo)))
					item.SetLineNum(entry.linenum)
				self.list.lv.AddItem(item)		

	def Save(self,path):
		if deb:
			print "start Save PoEditorBBOX"
			print "path:",path
		self.pofile.save(path)
		svdlns=[]  #moved to fix reference before assignment
		#print "pezzo finale = ",path[-7:]
		if path[-7:] != "temp.po":
			execpath = find_executable("msgfmt-x86")
			comtwo = execpath+" -c "+path
			checker = Popen( comtwo.split(' '), stdout=PIPE,stderr=PIPE)
			jessude,err= checker.communicate()
			#svdlns=[]
			for ries in err.split('\n'):
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
						w = BApplication.be_app.CountWindows()
						while w > i:
							title=BApplication.be_app.WindowAt(i).Title()
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
								BApplication.be_app.WindowAt(i).PostMessage(mxg)
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
		if deb:
			print "end Save PoEditorBBOX"
		
class translationtabview(BTabView):
	def __init__(self,frame,name,width,risizingMode,flags,superself):
		self.superself=superself
		BTabView.__init__(self,frame,name,width,risizingMode,flags)
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
	def MouseDown(self,point):
		numtabs=len(self.superself.listemsgstr)
		gg=0
		while gg<numtabs:
			if (point[0]>=self.TabFrame(gg)[0]) and (point[0]<=self.TabFrame(gg)[2]) and (point[1]>=self.TabFrame(gg)[1]) and (point[1]<=self.TabFrame(gg)[3]):
				self.superself.srctabview.Select(gg)
			gg=gg+1
		BApplication.be_app.WindowAt(0).PostMessage(12343)
		BTabView.MouseDown(self,point)
		self.superself.listemsgstr[self.Selection()].trnsl.MakeFocus()
		lngth=self.superself.listemsgstr[self.Selection()].trnsl.TextLength()
		self.superself.listemsgstr[self.Selection()].trnsl.Select(lngth,lngth)
		self.superself.listemsgstr[self.Selection()].trnsl.ScrollToSelection()
		#return 

class sourcetabview(BTabView):
	def __init__(self,frame,name,width,risizingMode,flags,superself):
		self.superself=superself
		BTabView.__init__(self,frame,name,width,risizingMode,flags)
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
	def MouseDown(self,point):
		numtabs=len(self.superself.listemsgstr)
		gg=0
		while gg<numtabs:
			if (point[0]>=self.TabFrame(gg)[0]) and (point[0]<=self.TabFrame(gg)[2]) and (point[1]>=self.TabFrame(gg)[1]) and (point[1]<=self.TabFrame(gg)[3]):
				self.superself.transtabview.Select(gg)
			gg=gg+1
		BApplication.be_app.WindowAt(0).PostMessage(12343)
		BTabView.MouseDown(self,point)
		self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.MakeFocus()
		lngth=self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.TextLength()
		self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.Select(lngth,lngth)
		self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.ScrollToSelection()
		#return BTabView.MouseDown(self,point)

class postabview(BTabView):
	def __init__(self,superself,frame,name,width):
		self.superself=superself
		BTabView.__init__(self,frame,name,width)
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
	def MouseDown(self,point):
		numtabs=len(self.superself.editorslist)
		gg=0
		while gg<numtabs:
			if (point[0]>=self.TabFrame(gg)[0]) and (point[0]<=self.TabFrame(gg)[2]) and (point[1]>=self.TabFrame(gg)[1]) and (point[1]<=self.TabFrame(gg)[3]):
				if self.Selection()!=gg:
					self.superself.NichilizeTM()
					shouldstop=False
					self.superself.infoprogress.SetText(str(self.superself.editorslist[gg].pofile.percent_translated()))
					if self.superself.editorslist[gg].list.lv.CurrentSelection()==-1:
						####try to remove all the comments
						try:
							self.superself.commentview.RemoveSelf()
							self.superself.scrollcomment.RemoveSelf()
							self.superself.headlabel.RemoveSelf()
						except:
							pass
						try:
							self.superself.contextview.RemoveSelf()
							self.superself.scrollcontext.RemoveSelf()
							self.superself.contextlabel.RemoveSelf()
						except:
							pass
						try:
							self.superself.tcommentview.RemoveSelf()
							self.superself.scrolltcomment.RemoveSelf()
							self.superself.tcommentlabel.RemoveSelf()
						except:
							pass
						try:
							self.superself.previousview.RemoveSelf()
							self.superself.scrollprevious.RemoveSelf()
							self.superself.labelprevious.RemoveSelf()
						except:
							pass
						self.superself.valueln.SetText("")
					if self.superself.editorslist[self.Selection()].list.lv.CurrentSelection()>-1:
						hasplural=self.superself.editorslist[self.Selection()].list.lv.ItemAt(self.superself.editorslist[self.Selection()].list.lv.CurrentSelection()).hasplural
						if hasplural:
							lung=len(self.superself.listemsgstr)
							pick=0
							while pick<lung:
								thistranslEdit=self.superself.listemsgstr[pick].trnsl
								if thistranslEdit.tosave:
									shouldstop=True
								pick+=1
						else:
							if self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.tosave:
								shouldstop=True
					if shouldstop:
						say = BAlert('save', 'You are on tab '+str(self.Selection())+' And you are switching to tab '+str(gg)+' Temporary save changes before switching to another po file?', 'Yes','No', 'Cancel', None , 3)
						out=say.Go()
						if out == 0:  # Yes
							#save and deselect
							cursel=self.superself.editorslist[self.Selection()]
							thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
							thisBlistitem.tosave=True
							tabs=len(self.superself.listemsgstr)-1
							bckpmsg=BMessage(16893)
							bckpmsg.AddInt8('savetype',1)
							bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
							bckpmsg.AddInt8('plurals',tabs)
							bckpmsg.AddInt32('tabview',self.Selection())
							if tabs == 0:
								thisBlistitem.txttosave=self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.Text()
								bckpmsg.AddString('translation',thisBlistitem.txttosave)
								#save singular
							else:
								#save all
								thisBlistitem.txttosavepl=[]
								thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
								bckpmsg.AddString('translation',thisBlistitem.txttosave)
								cox=1
								while cox < tabs+1:
									thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
									bckpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgstr[cox].trnsl.Text())
									cox+=1
							bckpmsg.AddString('bckppath',cursel.backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
							cursel.list.lv.DeselectAll()
						elif out == 1: # No
							#empty trnsl and src, than deselect 
							far=len(self.superself.listemsgstr)
							imp=0
							while imp<far:
								self.superself.listemsgstr[imp].trnsl.tosave=False
								self.superself.listemsgstr[imp].trnsl.txttosave=""
								self.superself.listemsgstr[imp].trnsl.txttosavepl=[]
								self.superself.listemsgstr[imp].trnsl.SetText("")
								imp+=1
							fir=len(self.superself.listemsgid)
							imp=0
							while imp<fir:
								self.superself.listemsgid[imp].src.SetText("")
								imp+=1
							self.superself.editorslist[self.Selection()].list.lv.DeselectAll()
						else:# or out == 2: means Cancel
							return
					if self.superself.editorslist[gg].list.lv.CurrentSelection()>-1:
						oldselection=self.superself.editorslist[gg].list.lv.CurrentSelection()
						self.superself.editorslist[gg].list.lv.DeselectAll()
						self.superself.editorslist[gg].list.lv.Select(oldselection)
						self.superself.editorslist[gg].list.lv.ScrollToSelection()
					else:
						self.superself.Nichilize()
						bounds = self.superself.Bounds()
						l, t, r, b = bounds
						binds = self.superself.background.Bounds()
						luwidth=self.superself.lubox.Bounds()[2]-self.superself.lubox.Bounds()[0]
						c,p,d,s = binds
						plygrnd2 = (5, b-142,r -luwidth-5, s-2)
						altece = self.superself.srctabview.TabHeight()
						tabrc2 = (3, 3, plygrnd2[2] - plygrnd2[0], plygrnd2[3] - plygrnd2[1]-altece)
						self.superself.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self.superself))
						self.superself.transtablabels.append(BTab())
						self.superself.transtabview.AddTab(self.superself.listemsgstr[0],self.superself.transtablabels[0])
						################### BUG? ###################
						#self.superself.transtabview.Draw(self.superself.transtabview.Bounds())
						self.superself.transtabview.Select(1)									############# bug fix
						self.superself.transtabview.Select(0)
						idlen=len(self.superself.listemsgid)
						x=0
						while x!=idlen:
							self.superself.listemsgid[x].src.SetText("")
							x+=1
						#################### BUG ?##################
						#self.superself.srctabview.Select(1)
						#self.superself.srctabview.Select(0)
						self.superself.srctabview.Draw(self.superself.srctabview.Bounds())
			gg=gg+1
		
		return BTabView.MouseDown(self,point)

#class BDoubleScrollBar(BScrollBar):
#	def __init__(self,rect,name,bview1,bview2,min,max,orientation):
#		self.bview2=bview2
#		BScrollBar.__init__(self,rect,name,bview1,float(min),float(max),orientation)
#		
#	def ValueChanged(self,newvalue):
#		self.bview2.Select(self.bview1.CurrentSelection)
#		return BScrollBar.ValueChanged(newvalue)
	
class pairedListView(BListView):
	def __init__(self, rect, name,paired):
		BListView.__init__(self,rect, name, B_SINGLE_SELECTION_LIST,B_FOLLOW_ALL_SIDES,B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_FRAME_EVENTS)
		self.pairedlv=paired
	def SelectionChanged(self):
		self.pairedlv.Select(self.CurrentSelection())
		self.pairedlv.ScrollToSelection()
		#return BListView.SelectionChanged(self)
class AnalyScrllVw1:
	HiWhat = 83 #Doubleclick
	Selmsgstr = 7755

	def __init__(self, rect, name,paired):
		self.lv = pairedListView(rect, name, paired)
		msg=BMessage(self.Selmsgstr)
		self.lv.SetSelectionMessage(msg)
		msg = BMessage(self.HiWhat)
		self.lv.SetInvocationMessage(msg)
		self.sv = BScrollView('AnalysisScrollView', self.lv, B_FOLLOW_ALL_SIDES, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, 0, 1, B_FANCY_BORDER)

class AnalyScrllVw2:
	HiWhat = 83 #Doubleclick
	Selmsgstr = 7755

	def __init__(self, rect, name):
		self.lv = BListView(rect, name, B_SINGLE_SELECTION_LIST,B_FOLLOW_ALL_SIDES,B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_FRAME_EVENTS)
		msg=BMessage(self.Selmsgstr)
		self.lv.SetSelectionMessage(msg)
		msg = BMessage(self.HiWhat)
		self.lv.SetInvocationMessage(msg)
		self.sv = BScrollView('AnalysisScrollView', self.lv, B_FOLLOW_ALL_SIDES, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, 0, 1, B_FANCY_BORDER)

class Analysis(BWindow):
	Selmsgstr = 320
	HiWhat =  684
	def __init__(self,encoding):
		kWindowFrame = (250, 150, 755, 497)
		kWindowName = "String analysis"
		BWindow.__init__(self, kWindowFrame, kWindowName, B_FLOATING_WINDOW, B_NOT_RESIZABLE)
		self.encoding = encoding
		bounds=self.Bounds()
		l,t,r,b = bounds
		self.underframe= BBox(bounds, 'underframe', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.underframe)
		self.achrin=[]
		self.orig=AnalyScrllVw2((50,5,67,342),"Original-text")
		self.ansv=AnalyScrllVw1((5,5,30,342),"Analysis-text",self.orig.lv)
		self.underframe.AddChild(self.ansv.sv)
		self.underframe.AddChild(self.orig.sv)
		rect = (85,5,r-5,150)
		self.undertextview = BBox(rect, 'undertextview', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_FANCY_BORDER)
		self.underframe.AddChild(self.undertextview)
		self.cpytrnsl = BTextView((2,2,r-5-85-2,150-5-2),"copytext",(4,4,rect[2]-rect[0]-4,rect[3]-rect[0]-4),B_FOLLOW_ALL)
		self.undertextview.AddChild(self.cpytrnsl)
		rect = (87,155,185,328)
		self.plv = BListView(rect, 'PeraulisListView', B_SINGLE_SELECTION_LIST,B_FOLLOW_ALL_SIDES,B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_FRAME_EVENTS)
		self.psv = BScrollView('PeraulisScrollView', self.plv, B_FOLLOW_ALL_SIDES, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, 1, 1, B_FANCY_BORDER)
		msg=BMessage(self.Selmsgstr)
		self.plv.SetSelectionMessage(msg)
		msg = BMessage(self.HiWhat)
		self.plv.SetInvocationMessage(msg)
		self.underframe.AddChild(self.psv)
		rect = (205,155,r-7,342)
		self.swres = BTextView(rect,"SingleWordAnalysis",(4,4,rect[2]-rect[0]-4,rect[3]-rect[0]-4),B_FOLLOW_ALL)
		self.swres.MakeEditable(0)
		self.underframe.AddChild(self.swres)

	def MessageReceived(self, msg):
		if msg.what == 43285:
			stringa=msg.FindString('word')
			elemento=MyListItem(stringa)
			self.ansv.lv.AddItem(elemento)
		elif msg.what == 43250:
			stringa=msg.FindString('word')
			elemento=MyListItem(stringa)
			self.orig.lv.AddItem(elemento)
		elif msg.what == 43288:
			self.plv.MakeEmpty()
			stringa=msg.FindString('text')
			self.cpytrnsl.SetText(stringa)
			lungjece=self.cpytrnsl.TextLength()
			i = 0
			peraulis=[]
			while i<lungjece:
				p=self.cpytrnsl.FindWord(i)
				peraule=self.cpytrnsl.Text()[p[0]:p[1]]
				if peraule !=" ":
					if peraule in peraulis:
						pass
					else:
						element=MyListItem(peraule)
						self.plv.AddItem(element)
						peraulis.append(peraule)
					i=p[1]
				i+=1
		elif msg.what == 320:
			if showspell:
				if self.swres.Text()!="":
					self.swres.SelectAll()
					self.swres.Clear()
				txt=self.plv.ItemAt(self.plv.CurrentSelection()).Text()
				speller = Popen( comm, stdout=PIPE, stdin=PIPE, stderr=PIPE)
				stdout_data = speller.communicate(input=txt)[0]
				self.swres.SetText(stdout_data)				
			
		
		return BWindow.MessageReceived(self, msg)
		
class PoWindow(BWindow):
	Menus = (
		('File', ((295485, 'Open'), (2, 'Save'), (1, 'Close'), (5, 'Save as...'),(None, None),(B_QUIT_REQUESTED, 'Quit'))),
		('Translation', ((3, 'Copy from source (ctrl+shift+s)'), (32,'Edit comment'), (70,'Done and next'), (71,'Mark/Unmark fuzzy (ctrl+b)'), (72, 'Previous w/o saving'),(73,'Next w/o saving'),(None, None), (6, 'Find source'), (7, 'Find/Replace translation'))),
		('View', ((74,'Fuzzy'), (75, 'Untranslated'),(76,'Translated'),(77, 'Obsolete'))),
		('Settings', ((40, 'General'),(41, 'User settings'), (42, 'Po properties'), (43, 'Po header'), (44, 'Spellcheck'), (45,'Translation Memory'))),
		('About', ((8, 'Help'),(None, None),(9, 'About')))
		)

	def __init__(self, frame):
		selectionmenu=0
		BWindow.__init__(self, frame, 'My personal PO editor for Haiku!', B_TITLED_WINDOW,0)
		bounds = self.Bounds()
		self.bar = BMenuBar(bounds, 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		self.modifier=False
		self.poview=[True,True,True,False]
		self.drop = threading.Semaphore()
		self.sem = threading.Semaphore()
		self.shortcut=False
		global confile,setencoding,deb
		try:
				Config.read(confile)
				self.poview[0]=Config.getboolean('Settings', 'Fuzzy')
		except (ConfigParser.NoSectionError):
				print "ops! no Settings section for po listing"
		except (ConfigParser.NoOptionError):
				cfgfile = open(confile,'w')
				Config.set('Settings','Fuzzy',True)
				Config.write(cfgfile)
				cfgfile.close()
		try:
				Config.read(confile)
				self.poview[1]=Config.getboolean('Settings', 'Untranslated')
		except (ConfigParser.NoSectionError):
				print "ops! no Settings section for po listing"
		except (ConfigParser.NoOptionError):
				cfgfile = open(confile,'w')
				Config.set('Settings','Untranslated',True)
				Config.write(cfgfile)
				cfgfile.close()
		try:
				Config.read(confile)
				self.poview[2]=Config.getboolean('Settings', 'Translated')
		except (ConfigParser.NoSectionError):
				print "ops! no Settings section for po listing"
		except (ConfigParser.NoOptionError):
				cfgfile = open(confile,'w')
				Config.set('Settings','Translated',True)
				Config.write(cfgfile)
				cfgfile.close()
		try:
				Config.read(confile)
				self.poview[3]=Config.getboolean('Settings', 'Obsolete')
		except (ConfigParser.NoSectionError):
				print "ops! no Settings section for po listing"
		except (ConfigParser.NoOptionError):
				cfgfile = open(confile,'w')
				Config.set('Settings','Obsolete',False)
				Config.write(cfgfile)
				cfgfile.close()
		try:
				Config.read(confile)
				self.modifiervalue=int(Config.get('Settings','modifierkey'))
		except (ConfigParser.NoSectionError):
				print "ops! no Settings section for modifier key"
				cfgfile = open(confile,'w')
				Config.add_section('Settings')
				Config.set('Settings','modifierkey',4100)
				Config.write(cfgfile)
				cfgfile.close()
				self.modifiervalue=4100 #1058 ALT;4100 CTRL
		except (ConfigParser.NoOptionError):
				cfgfile = open(confile,'w')
				Config.set('Settings','modifierkey',4100)
				Config.write(cfgfile)
				cfgfile.close()
				self.modifiervalue=4100 #1058 ALT;4100 CTRL
		
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
						msg = BMessage(k)
						menuitem = BMenuItem(name, msg)
						#in base a Settings
						if name == "Fuzzy":
							menuitem.SetMarked(self.poview[0])
						elif name == "Untranslated":
							menuitem.SetMarked(self.poview[1])
						elif name == "Translated":
							menuitem.SetMarked(self.poview[2])
						elif name == "Obsolete":
							menuitem.SetMarked(self.poview[3])
						menu.AddItem(menuitem)
			if savemenu:
				self.savemenu = menu
				self.bar.AddItem(self.savemenu)
			else:
				self.bar.AddItem(menu)
		l, t, r, b = bounds
		self.AddChild(self.bar)
		# GRAY COLOR BBOX
		self.background = BBox((l, t + barheight, r, b), 'background', B_FOLLOW_ALL,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.background)
		binds = self.background.Bounds()
		c,p,d,s = binds
		###### OPEN PANEL
		#entryfilter= BEntry.BEntry(".po",True)
#		node=BNode(".po")
#		if (node.InitCheck() != B_OK):
#			print "node not inizialized"
#		else:
#			print "node initialized"
		self.ofp=BFilePanel()
		self.lubox=BBox((d*3/4,2,d,s), 'leftunderbox', B_FOLLOW_TOP_BOTTOM|B_FOLLOW_RIGHT, B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS|B_NAVIGABLE,B_FANCY_BORDER)
		asd,dfg,ghj,jkl=self.lubox.Bounds()
		hig=round(self.lubox.GetFontHeight()[0])
		txtw="Completed:"
		self.infoforprogress=BStringView((4,jkl-hig-4,self.lubox.StringWidth(txtw),jkl-4),"infotxt",txtw, B_FOLLOW_BOTTOM|B_FOLLOW_LEFT)
		lengthtxt=self.lubox.StringWidth("100%")
		self.prcntstring=BStringView((ghj-self.lubox.StringWidth("%")-4,jkl-hig-4,ghj-4,jkl-4),"prcnt","%", B_FOLLOW_BOTTOM|B_FOLLOW_RIGHT)
		self.lubox.AddChild(self.prcntstring)
		self.infoprogress=BStringView((ghj-lengthtxt-self.lubox.StringWidth("%")-4,jkl-hig-4,ghj-self.lubox.StringWidth("%")-4,jkl-4),"progresstxt","", B_FOLLOW_BOTTOM|B_FOLLOW_RIGHT)
		self.infoprogress.SetAlignment(B_ALIGN_RIGHT)
		txtx="Line Number:"
		self.infoln=BStringView((4,jkl-hig*2-8,self.lubox.StringWidth(txtx),jkl-hig-8),"infoln",txtx, B_FOLLOW_BOTTOM|B_FOLLOW_LEFT)
		self.valueln=BStringView((8+self.lubox.StringWidth(txtx),jkl-hig*2-8,ghj-4,jkl-hig-8),"valueln","", B_FOLLOW_BOTTOM|B_FOLLOW_RIGHT)
		self.valueln.SetAlignment(B_ALIGN_RIGHT)
		self.lubox.AddChild(self.infoln)
		self.lubox.AddChild(self.valueln)
		self.lubox.AddChild(self.infoforprogress)
		self.lubox.AddChild(self.infoprogress)
		self.tempbtn=BButton((4,jkl-hig*3-33,ghj-68,jkl-hig*2-29), "txtanal", "Analyze", BMessage(8384),B_FOLLOW_BOTTOM)
		self.lubox.AddChild(self.tempbtn)
		if not showspell:
			self.tempbtn.Hide()
		self.event= threading.Event()
		self.background.AddChild(self.lubox)
		if tm:
			delt=100
			self.tmpanel = BBox((5.0, b-barheight-245-delt+3,d*3/4-5,b-barheight-245-3), 'tmbox', B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT, B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS|B_NAVIGABLE,B_FANCY_BORDER)
			(tpa,tpb,tpc,tpd)=self.tmpanel.Bounds()
			self.tmscrollsugj=ScrollSugj((tpa+2,tpb+2,tpc-17,tpd-2), 'ScrollSugj') #AAAA4
			self.tmpanel.AddChild(self.tmscrollsugj.sv)
			aaa,bbb,ccc,ddd = self.tmpanel.Bounds()#l, t, r, b
			self.sscrlb = BScrollBar((ccc -16,1,ccc-1,ddd-1),'Sugj_ScrollBar',self.tmscrollsugj.lv,0.0,float(r),B_VERTICAL)#len(datab)
			self.tmpanel.AddChild(self.sscrlb)
			self.background.AddChild(self.tmpanel)
			#self.errorstr=BStringView((tpa+2,tpb+2,tpc-17,tpd-2),"errorstring","Error connecting to Translation Memory server",B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT)
			#self.background.AddChild(self.errorstr)
			#self.errorstr.Hide()
		else:
			delt=3
		self.postabview = postabview(self,(5.0, 5.0, d*3/4-5, b-barheight-245-delt), 'postabview',B_WIDTH_FROM_LABEL)

		altece = self.postabview.TabHeight()
		tfr = (5.0, 5.0, d*3/4-5, s-5)
		self.trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])

		self.tabslabels=[]
		self.editorslist=[]
		
		self.background.AddChild(self.postabview)

		self.speloc = threading.Semaphore()
		self.intime=time.time()

		playground1 = (5,b-268,r - d*1/4-5, s-120)
		self.srctabview = sourcetabview(playground1, 'sourcetabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS,self)

		altece = self.srctabview.TabHeight()
		tabrc = (3.0, 3.0, playground1[2] - playground1[0], playground1[3] - playground1[1]-altece-1)
		self.srctablabels=[]
		self.listemsgid=[]
		self.background.AddChild(self.srctabview)
		
		self.sourcebox=srctabbox(tabrc,'msgid',altece)
		self.listemsgid.append(self.sourcebox)
		self.srctablabels.append(BTab())
		self.srctabview.AddTab(self.listemsgid[0], self.srctablabels[0])
		
		luwidth=self.lubox.Bounds()[2]-self.lubox.Bounds()[0]
		playground2 = (5, b-142,r -luwidth-5, s-2)
		self.transtabview = translationtabview(playground2, 'translationtabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS,self)#BTabView(playground2, 'translationtabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT)

		tabrc = (3, 3, playground2[2] - playground2[0], playground2[3] - playground2[1]-altece)
		self.transtablabels=[]
		self.listemsgstr=[]
		self.background.AddChild(self.transtabview)

		self.transbox=trnsltabbox(tabrc,'msgstr',altece,self)
		self.listemsgstr.append(self.transbox)
		self.transtablabels.append(BTab())
		self.transtabview.AddTab(self.listemsgstr[0], self.transtablabels[0])
		#self.postabview.Draw(self.postabview.Bounds())
		#self.transtabview.Draw(self.transtabview.Bounds())
		##### if first launch, it opens the profile creator wizard and sets default enconding for polib
		if  firstrun:
			setencoding = False
			goonplz = True
			try:
				Config.read(confile)
				tst = ConfigSectionMap("Settings")['wizardprompt']
				if tst == "False":
					goonplz = False
			except:
				pass
			if goonplz:
				BApplication.be_app.WindowAt(0).PostMessage(305)
		else:
			#try:
				Config.read(confile)
				#self.setencoding=Config.getboolean('Settings', 'customenc')
				#if self.setencoding:
				#print setencoding
				if setencoding:
					try:
						usero = ConfigSectionMap("Users")['default']
						self.encoding = ConfigSectionMap(usero)['encoding']
					except: #(ConfigParser.NoSectionError):
						print ("custom encoding method specified but no encoding indicated")
						self.encoding = "utf-8"
						try:
							usero = ConfigSectionMap("Users")['default']
							cfgfile = open(confile,'w')
							Config.set(usero,'encoding',"utf-8")
							Config.write(cfgfile)
							cfgfile.close()
						except:
							print "error writing user encoding to config.ini, is there a default user?"
							setencoding = False
						
			#except (ConfigParser.NoSectionError):
			#	print "ops! no Settings section for custom encoding"
			#	setencoding = False
			#except:
			#	setencoding = False

		if showspell:
			thread.start_new_thread( self.speloop, () )
			self.spellabel = BStringView((8,jkl-hig*3-70,ghj-8,jkl-hig*2-62),"spellabel","Spellcheck status: enabled",B_FOLLOW_BOTTOM)
			self.spellresp = BStringView((8,jkl-hig*3-58,ghj-88,jkl-hig*2-46),"spellresp","Spellcheck reply:",B_FOLLOW_BOTTOM)
			self.spellcount = BStringView((ghj-88,jkl-hig*3-58,ghj-68,jkl-hig*2-46),"spellresp","C",B_FOLLOW_BOTTOM)
			self.checkres = BTextView((ghj-64,jkl-hig*3-54,ghj-8,jkl-hig*2-18),"checkres",(17.5,5,ghj-8-15,(jkl-hig*2-28)-15),B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM) # ☐ ☑ ☒
			self.checkres.SetStylable(True)
			self.font=BFont()
			#self.font.PrintToStream()
			self.font.SetSize(28.0)
			#setshear 45-135
			#setface(B_ITALIC_FACE)B_UNDERSCORE_FACE, B_STRIKEOUT_FACE OUTLINE
			self.font.SetFace(B_BOLD_FACE)
			self.checkres.SetFontAndColor(0,1,self.font)
			self.checkres.SetText("☐")
			self.checkres.MakeEditable(False)
			self.lubox.AddChild(self.spellabel)
			self.lubox.AddChild(self.spellresp)
			self.lubox.AddChild(self.checkres)
			self.lubox.AddChild(self.spellcount)
		else:
			self.spellabel= BStringView((8,jkl-hig*3-80,ghj-8,jkl-hig*2-72),"spellabel","Spellcheck status: disabled")
			self.lubox.AddChild(self.spellabel)
			
		self.netlock=threading.Semaphore()
			
############# end of _init_ ################
			
	def NichilizeTM(self):
		if tm:
			self.tmscrollsugj.Clear()
			
	def FrameResized(self,x,y):
			i=self.postabview.Selection()
			if i>-1:
				h,j,k,l = self.editorslist[i].Bounds()
				zx,xc,cv,vb = self.editorslist[i].scrollb.Bounds()
				for b in self.editorslist:
					if b == self.editorslist[i]:
						pass
					else:
						b.ResizeTo(k,l)
						b.list.lv.ResizeTo(k-27,l-10)
						b.list.sv.ResizeTo(k-23,l-6)
					
						b.scrollb.MoveTo(k-21,5)
						b.scrollb.ResizeTo(cv-zx,l-10)
			try:
				h,j,k,l=self.contextview.Bounds()
				a,s,d,f=self.scrollcontext.Bounds()
				self.scrollcontext.ResizeTo(d-a,l-j)
			except:
				pass
			try:
				h,j,k,l=self.previousview.Bounds()
				a,s,d,f=self.scrollprevious.Bounds()
				self.scrollprevious.ResizeTo(d-a,l-j)
			except:
				pass
			try:
				h,j,k,l=self.commentview.Bounds()
				a,s,d,f=self.scrollcomment.Bounds()
				self.scrollcomment.ResizeTo(d-a,l-j)
			except:
				pass
			try:
				h,j,k,l=self.tcommenttview.Bounds()
				a,s,d,f=self.scrolltcomment.Bounds()
				self.scrolltcomment.ResizeToP(d-a,l-j)
			except:
				pass
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
						pck.append(src.decode(self.encoding))#'utf-8'
						send_pck=pickle.dumps(pck)
						tmsocket.send(send_pck)
						pck_answer=tmsocket.recv(4096)#1024
						if self.listemsgid[self.srctabview.Selection()].src.Text() == src: #check again if I changed the selection
							answer=pickle.loads(pck_answer)
							sugjmsg=BMessage(5391359)
							ts=len(answer)
							if deb:
								print "lunghezza della risposta",ts
							sugjmsg.AddInt16('totsugj',ts)
							x=0
							while x <ts:
								sugjmsg.AddString('sugj_'+str(x),answer[x][0].encode('utf-8'))
								sugjmsg.AddInt8('lev_'+str(x),answer[x][1])
								x+=1
							BApplication.be_app.WindowAt(0).PostMessage(sugjmsg)
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
				txt1=src[1].encode(self.encoding)
				if txt0==None:
					#add to tm dictionary
					txt2=src[2].encode(self.encoding)
					st2=txt2.decode(self.encoding)
					st2.replace('<','&lt;')
					st2.replace('>','&gt;')
					st1=txt1.decode(self.encoding)
					st1.replace('<','&lt;')
					st1.replace('>','&gt;')
					pck.append((txt0,st1,st2))
				else:
					#remove from tm dictionary
					txt2=src[2].decode(self.encoding)
					txt2.replace('<','&lt;')
					txt2.replace('>','&gt;')
					st1=txt1.decode(self.encoding)
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


	def MessageReceived(self, msg):
#		print "Is this a system message?", msg.IsSystem()
		if msg.what == B_MODIFIERS_CHANGED:
			value=msg.FindInt32("modifiers")
			self.sem.acquire()
			if value==self.modifiervalue or value==self.modifiervalue+8 or value ==self.modifiervalue+32 or value ==self.modifiervalue+40:
				if deb:
					print "modificatore"
				self.modifier=True
				self.shortcut = False
			elif value == self.modifiervalue+4357 or value==self.modifiervalue+265 or value==self.modifiervalue+289 or value == self.modifiervalue+297:
				if deb:
					print "scorciatoia"
				self.shortcut = True
				self.modifier = False
			else:
				if deb:
					print "altro"
				self.modifier=False
				self.shortcut=False
			self.sem.release()
			return
#		elif msg.what == B_UNMAPPED_KEY_DOWN:
#			msg.PrintToStream()
		elif msg.what == B_KEY_DOWN:	#on tab key pressed, focus on translation or translation of first item list of translations
			key=msg.FindInt32('key')
			lung = len(self.editorslist)
			if lung > 0:
				if key==38: #tab key
					if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
						self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus() ###########à LOOK HERE 
					else:
						self.editorslist[self.postabview.Selection()].list.lv.Select(0)
						self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
				elif key in (98,87,54,33):
					if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection() < 0:
						self.editorslist[self.postabview.Selection()].list.lv.Select(0)
						self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
#				elif key == 61: # s key      ######## TODO: check, because it seems useless
#					if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
#						self.sem.acquire()
#						if self.shortcut:
#							BApplication.be_app.WindowAt(0).PostMessage(33)
#						else:
#							pass
#						self.sem.release()
			return

		elif msg.what == 295485:
			self.ofp.Show()
			return
			
		elif msg.what == 1:
			# Close opened file
			if len(self.editorslist)>1:
				whichrem=self.postabview.Selection()
				if whichrem>0:
					actualselection=self.editorslist[whichrem-1].list.lv.CurrentSelection()
					if actualselection>-1:
						self.editorslist[whichrem-1].list.lv.DeselectAll()
						self.editorslist[whichrem-1].list.lv.Select(actualselection)
					else:
						self.Nichilize()
						bounds = self.Bounds()
						l, t, r, b = bounds
						binds = self.background.Bounds()
						luwidth=self.lubox.Bounds()[2]-self.lubox.Bounds()[0]
						c,p,d,s = binds
						plygrnd2 = (5, b-142,r -luwidth-5, s-2)
						altece = self.srctabview.TabHeight()
						tabrc2 = (3, 3, plygrnd2[2] - plygrnd2[0], plygrnd2[3] - plygrnd2[1]-altece)
						self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
						self.transtablabels.append(BTab())
						self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
						################### BUG? ###################
						self.transtabview.Select(1)									###### bug fix
						self.transtabview.Select(0)
						#self.transtabview.Draw(self.transtabview.Bounds())
						self.listemsgid[0].src.SetText("")
						#self.srctabview.Select(1)
						#self.srctabview.Select(0)
						self.srctabview.Draw(self.srctabview.Bounds())
				else:
					actualselection=self.editorslist[whichrem+1].list.lv.CurrentSelection()
					if actualselection>-1:
						self.editorslist[whichrem-1].list.lv.DeselectAll()
						self.editorslist[whichrem-1].list.lv.Select(actualselection)
					else:
						self.Nichilize()
						bounds = self.Bounds()
						l, t, r, b = bounds
						binds = self.background.Bounds()
						luwidth=self.lubox.Bounds()[2]-self.lubox.Bounds()[0]
						c,p,d,s = binds
						plygrnd2 = (5, b-142,r -luwidth-5, s-2)
						altece = self.srctabview.TabHeight()
						tabrc2 = (3, 3, plygrnd2[2] - plygrnd2[0], plygrnd2[3] - plygrnd2[1]-altece)
						self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
						self.transtablabels.append(BTab())
						self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
						################### BUG? ###################
						self.transtabview.Select(1)									###### bug fix
						self.transtabview.Select(0)
						#self.transtabview.Draw(self.transtabview.Bounds())
						self.listemsgid[0].src.SetText("")
						#self.srctabview.Select(1)
						#self.srctabview.Select(0)
						self.srctabview.Draw(self.srctabview.Bounds())
				self.postabview.RemoveTab(whichrem)
				self.tabslabels.pop(whichrem)
				self.editorslist.pop(whichrem)
			elif len(self.editorslist) == 1:
				whichrem=self.postabview.Selection()
				self.Nichilize()
				bounds = self.Bounds()
				l, t, r, b = bounds
				binds = self.background.Bounds()
				luwidth=self.lubox.Bounds()[2]-self.lubox.Bounds()[0]
				c,p,d,s = binds
				plygrnd2 = (5, b-142,r -luwidth-5, s-2)
				altece = self.srctabview.TabHeight()
				tabrc2 = (3, 3, plygrnd2[2] - plygrnd2[0], plygrnd2[3] - plygrnd2[1]-altece)
				self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
				self.transtablabels.append(BTab())
				self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
				################### BUG? ###################
				self.transtabview.Select(1)									###### bug fix
				self.transtabview.Select(0)
				#self.transtabview.Draw(self.transtabview.Bounds())
				self.listemsgid[0].src.SetText("")
				#self.srctabview.Select(1)
				#self.srctabview.Select(0)
				self.srctabview.Draw(self.srctabview.Bounds())
				self.postabview.RemoveTab(whichrem)
				self.postabview.Draw(self.postabview.Bounds())
#				self.postabview.Hide()     # <----- Bug fix
#				self.postabview.Show()	   # <----- Bug fix
				self.tabslabels.pop(whichrem)
				self.editorslist.pop(whichrem)
			return
			
		elif msg.what == 2:
			# Save current file
			if len(self.editorslist)>0:     ###### FIX HERE IT DOESN'T WORK!! no real save
				if deb:
					print "controllo modifica eventtextview"
				if self.listemsgstr[self.transtabview.Selection()].trnsl.tosave:
					if deb:
						print "eventtextview modificato... \n si procede a salvare"
					self.listemsgstr[self.transtabview.Selection()].trnsl.Save()
					if deb:
						print "salvato"
				try:
					Config.read(confile)
					namo=ConfigSectionMap("Users")['default']
					defname=namo+' <'+ConfigSectionMap(namo)['pe-mail']+'>'
					grp=ConfigSectionMap(namo)['team']+' <'+ConfigSectionMap(namo)['te-mail']+'>'
				except:
					defname=self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']
					grp=self.editorslist[self.postabview.Selection()].pofile.metadata['Language-Team']
				now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
				savepath=self.editorslist[self.postabview.Selection()].filen+self.editorslist[self.postabview.Selection()].file_ext

				self.editorslist[self.postabview.Selection()].writter.acquire()
				self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']=defname
				self.editorslist[self.postabview.Selection()].pofile.metadata['Language-Team']=grp
				self.editorslist[self.postabview.Selection()].pofile.metadata['PO-Revision-Date']=now
				self.editorslist[self.postabview.Selection()].pofile.metadata['X-Editor']=version
				if deb:
					print "Function save: starting thread"
				thread.start_new_thread( self.editorslist[self.postabview.Selection()].Save, (savepath,) )
			return

		elif msg.what == 3:
			#copy from source from menù
			if len(self.editorslist)>0:
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
					self.cod=self.editorslist[self.postabview.Selection()].encodo
					cursel=self.editorslist[self.postabview.Selection()]
					thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
					thisBlistitem.tosave=True
					tabs=len(self.listemsgstr)-1
					bckpmsg=BMessage(16893)
					bckpmsg.AddInt8('savetype',1)
					bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
					bckpmsg.AddInt8('plurals',tabs)
					bckpmsg.AddInt32('tabview',self.postabview.Selection())
					if tabs == 0:   #->      if not thisBlistitem.hasplural:                         <-------------------------- or this?
						thisBlistitem.txttosave=thisBlistitem.text.decode(self.cod)#(self.encoding)
						thisBlistitem.msgstrs=thisBlistitem.txttosave
						bckpmsg.AddString('translation',thisBlistitem.txttosave.encode(self.cod))#(self.encoding)) # <------------ check if encode in self.encoding or utf-8
					else:
						thisBlistitem.txttosavepl=[]
						thisBlistitem.txttosave=self.listemsgid[0].src.Text().decode(self.cod)#(self.encoding)
						thisBlistitem.msgstrs=[]
						thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
						bckpmsg.AddString('translation',thisBlistitem.txttosave.encode(self.cod))#(self.encoding)(self.encoding)) # <------------ check if encode in self.encoding or utf-8
						cox=1
						while cox < tabs+1:
							thisBlistitem.msgstrs.append(self.listemsgid[1].src.Text().decode(self.cod))#(self.encoding)(self.encoding))
							thisBlistitem.txttosavepl.append(self.listemsgid[1].src.Text().decode(self.cod))#(self.encoding)(self.encoding))
							bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())    #<------- check removed encode(self.encoding)
							cox+=1
					bckpmsg.AddString('bckppath',cursel.backupfile)
					BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)

					kmesg=BMessage(130550)
					kmesg.AddInt8('movekind',0)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
			return
		elif msg.what == 431110173:
			#delete a suggestion on remote tmserver
			txtdel=msg.FindString("sugj")
			srcdel=self.listemsgid[self.srctabview.Selection()].src.Text()
			cmd=("d","e","l")
			mx=[cmd,srcdel,txtdel]
			thread.start_new_thread( self.tmcommunicate, (mx,) )
			
		elif msg.what == 8147420:
			# copy from tm suggestions
			if len(self.editorslist)>0:
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
					askfor=msg.FindInt8("sel")
					if self.tmscrollsugj.lv.CountItems()>askfor:
						self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.tmscrollsugj.lv.ItemAt(askfor).text)
						lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
						self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
						self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
						self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
#						print self.tmscrollsugj.lv.ItemAt(askfor).text #settext con tutte i vari controlli ortografici mettere tosave = True a eventtextview interessato
						
		elif msg.what == 33:
			#copy from source from keyboard
			if len(self.editorslist)>0:
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
					self.cod=self.editorslist[self.postabview.Selection()].encodo
					cursel=self.editorslist[self.postabview.Selection()]
					thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
					thisBlistitem.tosave=True
					tabs=len(self.listemsgstr)-1
					bckpmsg=BMessage(16893)
					bckpmsg.AddInt8('savetype',1)
					bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
					bckpmsg.AddInt8('plurals',tabs)
					bckpmsg.AddInt32('tabview',self.postabview.Selection())
					if tabs == 0:   #->      if not thisBlistitem.hasplural:                         <-------------------------- or this?
						thisBlistitem.txttosave=thisBlistitem.text.decode(self.cod)#(self.encoding)
						thisBlistitem.msgstrs=thisBlistitem.txttosave
						bckpmsg.AddString('translation',thisBlistitem.txttosave.encode(self.cod))#(self.encoding)) # <------------ check if encode in self.encoding or utf-8
					else:
						thisBlistitem.txttosavepl=[]
						thisBlistitem.txttosave=self.listemsgid[0].src.Text().decode(self.cod)#((self.encoding)
						thisBlistitem.msgstrs=[]
						thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
						bckpmsg.AddString('translation',thisBlistitem.txttosave.encode(self.cod))#(self.encoding)) # <------------ check if encode in self.encoding or utf-8
						cox=1
						while cox < tabs+1:
							thisBlistitem.msgstrs.append(self.listemsgid[1].src.Text().decode(self.cod))#(self.encoding))
							thisBlistitem.txttosavepl.append(self.listemsgid[1].src.Text().decode(self.cod))#(self.encoding))
							bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())    #<------- check removed encode(self.encoding)
							cox+=1
					bckpmsg.AddString('bckppath',cursel.backupfile)
					BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
					if tabs == 0:
						self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.listemsgid[self.srctabview.Selection()].src.Text())
					else:
						p=len(self.listemsgstr)
						pi=0
						while pi<p:
							if pi==0:
								self.listemsgstr[0].trnsl.SetText(self.listemsgid[0].src.Text())
							else:
								self.listemsgstr[pi].trnsl.SetText(self.listemsgid[1].src.Text())
							pi+=1
					self.editorslist[self.postabview.Selection()].Hide()
					self.editorslist[self.postabview.Selection()].Show() #Updates the MsgStrItem
					lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
					self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
					self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
					BApplication.be_app.WindowAt(0).PostMessage(12343)
		elif msg.what == 5:
			# Save as
			if len(self.editorslist)>0:
				self.editorslist[self.postabview.Selection()].fp.Show()
				i = 1
				w = BApplication.be_app.CountWindows()
				while w > i:
					title=BApplication.be_app.WindowAt(i).Title()
					result=title.lower().find("python2.7")    ###################### TODO: find a better solution #########################
					if result>-1:
						thiswindow=i
						BApplication.be_app.WindowAt(i).PostMessage(B_KEY_DOWN)#<---- Fixes bug: save button not enabled
					i=i+1
			
		elif msg.what == 6:
			# Find source
			if len(self.editorslist)>0:
				self.Findsrc = Findsource()
				self.Findsrc.Show()
		
		elif msg.what == 7:
			# Find/Replace translation
			if len(self.editorslist)>0:
				self.FindReptrnsl = FindRepTrans()
				self.FindReptrnsl.Show()
		
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
			try:
				Config.read(confile)
				sezpres = False
				sezions=Config.sections()
				for x in sezions:
					if x == "Users":
						sezpres = True
				if sezpres:
						self.usersettings = ImpostazionsUtent()
						self.usersettings.Show()
						self.SetFlags(B_AVOID_FOCUS)
				else:
						self.maacutent = MaacUtent(True)
						self.maacutent.Show()
						self.SetFlags(B_AVOID_FOCUS)
			except:
				pass
			return
		
		elif msg.what == 32:
			#Double clic = translator comment
			if len(self.editorslist)>0:
				indextab=self.postabview.Selection()
				cursel=self.editorslist[indextab]
				listsel=cursel.list.lv.CurrentSelection()
				if listsel>-1:
					thisBlistitem=cursel.list.lv.ItemAt(listsel)
					self.tcommentdialog=TranslatorComment(listsel,indextab,thisBlistitem,self.encoding)
					self.tcommentdialog.Show()
			
		elif msg.what == 42:
			# PO metadata
			if len(self.editorslist)>0:
				self.POMetadata = POmetadata()
				self.POMetadata.Show()

				self.POMetadata.pofile = self.editorslist[self.postabview.Selection()].pofile
				self.POMetadata.orderedmetadata = self.editorslist[self.postabview.Selection()].orderedmetadata
				i = 1
				w = BApplication.be_app.CountWindows()
				while w > i:
					if BApplication.be_app.WindowAt(i).Title()=="POSettings":
						thiswindow=i
					i=i+1
				BApplication.be_app.WindowAt(thiswindow).PostMessage(99111)
			return

		elif msg.what == 43:
			#Po header
			if len(self.editorslist)>0:
				tmp = self.postabview.Selection()
				self.HeaderWindow = HeaderWindow(tmp,self.editorslist[tmp].pofile,self.editorslist[tmp].encodo)#self.encoding)
				self.HeaderWindow.Show()
			return

		elif msg.what == 44:
			#spelcheck settings
#			if 'self.splchset' in locals():
			#if hasattr(self, 'splchset'):
			self.splchset = SpellcheckSettings()
			self.splchset.Show()
		elif msg.what == 45:
			#spelcheck settings
			self.tmset = TMSettings()
			self.tmset.Show()
		elif msg.what == 70:
			# Done and next
			if len(self.editorslist)>0:
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
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
						cursel=self.editorslist[self.postabview.Selection()]
						thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
						thisBlistitem.tosave=True
						tabs=len(self.listemsgstr)-1
						bckpmsg=BMessage(16893)
						bckpmsg.AddInt8('savetype',1)
						bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
						bckpmsg.AddInt8('plurals',tabs)
						bckpmsg.AddInt32('tabview',self.postabview.Selection())
						if tabs == 0:   #->      if not thisBlistitem.hasplural:                         <-------------------------- or this?
							thisBlistitem.txttosave=thistranslEdit.Text()#.decode(self.encoding)		 <----- reinsert this
							bckpmsg.AddString('translation',thisBlistitem.txttosave)
						else:
							thisBlistitem.txttosavepl=[]
							thisBlistitem.txttosave=self.listemsgstr[0].trnsl.Text()#.decode(self.encoding)     <----- reinsert this
							bckpmsg.AddString('translation',thisBlistitem.txttosave)
							cox=1
							while cox < tabs+1:
								thisBlistitem.txttosavepl.append(self.listemsgstr[1].trnsl.Text())
								bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgstr[cox].trnsl.Text())
								cox+=1
						bckpmsg.AddString('bckppath',cursel.backupfile)
						BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
					kmesg=BMessage(130550)
					kmesg.AddInt8('movekind',4)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
			return

		elif msg.what == 72:
			# previous without saving
			if len(self.editorslist)>0:
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
					thistranslEdit=self.listemsgstr[self.transtabview.Selection()].trnsl
					if thistranslEdit.tosave:
						thisBlistitem=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
						thisBlistitem.tosave=False
						thisBlistitem.txttosave=""
					kmesg=BMessage(130550)
					kmesg.AddInt8('movekind',1)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
			
		elif msg.what == 73:
			# next without saving
			if len(self.editorslist)>0:
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
					thistranslEdit=self.listemsgstr[self.transtabview.Selection()].trnsl
					if thistranslEdit.tosave:
						thisBlistitem=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
						thisBlistitem.tosave=False
						thisBlistitem.txttosave=""
					kmesg=BMessage(130550)
					kmesg.AddInt8('movekind',0)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
		
		elif msg.what == 74:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, None , 3)
			out=say.Go()
			if out == 0:
				#save first
				BApplication.be_app.WindowAt(0).PostMessage(2)
				if self.poview[0]:
				#try:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(74)
					men.SetMarked(0)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Fuzzy',False)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[0]=False
				else:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(74)
					men.SetMarked(1)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Fuzzy',True)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[0]=True
				for b in self.editorslist:
					b.list.reload(self.poview,b.pofile,b.encodo)#self.encoding)
			return
					
		elif msg.what == 75:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, None , 3)
			out=say.Go()
			if out == 0:
				#save first
				BApplication.be_app.WindowAt(0).PostMessage(2)
				if self.poview[1]:
				#try:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(75)
					men.SetMarked(0)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Untranslated',False)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[1]=False
				else:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(75)
					men.SetMarked(1)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Untranslated',True)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[1]=True
				for b in self.editorslist:
					b.list.reload(self.poview,b.pofile,b.encodo)#self.encoding)
			return

		elif msg.what == 76:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, None , 3)
			out=say.Go()
			if out == 0:
				#save first
				BApplication.be_app.WindowAt(0).PostMessage(2)
				if self.poview[2]:
				#try:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(76)
					men.SetMarked(0)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Translated',False)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[2]=False
				else:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(76)
					men.SetMarked(1)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Translated',True)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[2]=True
				for b in self.editorslist:
					b.list.reload(self.poview,b.pofile,b.encodo)#self.encoding)
			return
		
		elif msg.what == 77:
			#this is slow due to reload
			say = BAlert('Save unsaved work', 'To proceed you need to save this file first, proceed?', 'Yes','No', None, None , 3)
			out=say.Go()
			if out == 0:
				#save first
				BApplication.be_app.WindowAt(0).PostMessage(2)
				if self.poview[3]:
				#try:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(77)
					men.SetMarked(0)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Obsolete',False)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[3]=False
				else:
					Config.read(confile)
					sezpresent = False
					men=self.savemenu.FindItem(77)
					men.SetMarked(1)
					sezioni=Config.sections()
					for x in sezioni:
						if x == "Settings":
							sezpresent = True
					if not sezpresent:
						Config.add_section('Settings')
					cfgfile = open(confile,'w')
					Config.set('Settings','Obsolete',True)
					Config.write(cfgfile)
					cfgfile.close()
					self.poview[3]=True
				for b in self.editorslist:
					b.list.reload(self.poview,b.pofile,b.encodo)#self.encoding)
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
				if (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1) and (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()<self.editorslist[self.postabview.Selection()].list.lv.CountItems()):
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()+1)
					self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
				elif self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()==-1:
					self.editorslist[self.postabview.Selection()].list.lv.Select(0)
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif movetype == 1:
				#select one up
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>0 :
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()-1)
				elif self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()==-1:
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CountItems()-1)
				self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif movetype == 2:
				#select one page up
				thisitem=self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()
				if thisitem > -1:
					pass
				else:
					thisitem=0
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.ItemFrame(thisitem)
				hitem=rectangular[3]-rectangular[1]
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.Bounds()
				hwhole=rectangular[3]-rectangular[1]
				page=int(hwhole//hitem)
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>(page-1) :
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()-page)
				else:
					self.editorslist[self.postabview.Selection()].list.lv.Select(0)
				self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif movetype == 3:
				#select one page down
				thisitem=self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()
				if thisitem > -1:
					pass
				else:
					thisitem=0
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.ItemFrame(thisitem)
				hitem=rectangular[3]-rectangular[1]
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.Bounds()
				hwhole=rectangular[3]-rectangular[1]
				page=int(hwhole//hitem)
				if (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1) and (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()<self.editorslist[self.postabview.Selection()].list.lv.CountItems()-page):
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()+page)	
				else:
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CountItems()-1)	
				self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			elif  movetype == 4:
				#select next untranslated (or needing work) string
				if (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1):
					spice = self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()+1
					if spice == self.editorslist[self.postabview.Selection()].list.lv.CountItems():
						spice = 0
				else:
					self.editorslist[self.postabview.Selection()].list.lv.Select(0)
					self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
					spice=0
				tt=0
				tt=spice
				counting=0
				lookingfor = True
				max = self.editorslist[self.postabview.Selection()].list.lv.CountItems()
				while lookingfor:
					blistit=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(tt)
					if blistit.state==0 or blistit.state==2:
						lookingfor = False
						self.editorslist[self.postabview.Selection()].list.lv.Select(tt)
						self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
					tt+=1
					counting +=1
					if counting == max:
						lookingfor = False
					if tt==max:
						tt=0
				#self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated())) # reinsert if not working properly
			thisBlistitem=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
			try:
				if thisBlistitem.tosave: #it happens when something SOMEHOW has not been saved
					print("testo da salvare (this shouldn\'t happen)",thisBlistitem.txttosave)
			except:
				pass
			if self.listemsgstr[self.transtabview.Selection()].trnsl.Text()!="":
				BApplication.be_app.WindowAt(0).PostMessage(333111)
			#NON AGGIUNGERE QUI RICHIESTA TM PANEL
			return

		elif msg.what == 305:
			#USER CREATOR WIZARD
			self.maacutent = MaacUtent(True)
			self.maacutent.Show()
			self.SetFlags(B_AVOID_FOCUS)
			return
			
		elif msg.what == 9631:
			#ris=msg.FindInt16('index')
			sugg=msg.FindString('sugg')
			sorig=msg.FindString('sorig')
			indi=msg.FindInt32('indi')
			indf=msg.FindInt32('indf')
			self.listemsgstr[self.transtabview.Selection()].trnsl.Delete(indi,indf)
			self.listemsgstr[self.transtabview.Selection()].trnsl.Insert(indi,sugg)
			self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			BApplication.be_app.WindowAt(0).PostMessage(12343)#(333111)
			return
			
		elif msg.what == 982757:
			self.checkres.SetFontAndColor(0,1,self.font,B_FONT_ALL,(150,0,0,0))
			self.checkres.SetText("☒")
		elif msg.what == 735157:
			self.checkres.SetFontAndColor(0,1,self.font,B_FONT_ALL,(0,150,0,0))
			self.checkres.SetText("☑")
		elif msg.what == 112118:
			#launch a delayed check
			if deb:
				print "start delayed check"
			oldtext=msg.FindString('oldtext')
			cursel=msg.FindInt8('cursel')
			indexBlistitem=msg.FindInt32('indexBlistitem')
			tabs=len(self.listemsgstr)-1
			if cursel == self.postabview.Selection():
				tmp=self.editorslist[cursel]
				if indexBlistitem == tmp.list.lv.CurrentSelection():
					if self.listemsgstr[self.transtabview.Selection()].trnsl.oldtext != self.listemsgstr[self.transtabview.Selection()].trnsl.Text():  ### o è meglio controllare nel caso di plurale tutti gli eventtextview?
						self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			self.intime=time.time()
			if deb:
				print "end delayed check"

		elif msg.what == 16893:
			try:
				Config.read(confile)
				defname=ConfigSectionMap("Users")['default']
			except:
				defname=self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']
			now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
			# save to backup and update the blistitem
			bckppath = msg.FindString('bckppath')
			savetype = msg.FindInt8('savetype')
			if savetype == 0: #simple save used for fuzzy state and metadata change
				self.editorslist[self.postabview.Selection()].writter.acquire()
				self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']=defname
				self.editorslist[self.postabview.Selection()].pofile.metadata['PO-Revision-Date']=now
				self.editorslist[self.postabview.Selection()].pofile.metadata['X-Editor']=version
				thread.start_new_thread( self.editorslist[self.postabview.Selection()].Save, (bckppath,) )
				#self.editorslist[self.postabview.Selection()].pofile.save(bckppath)
				return
			elif savetype == 2:
				#save of metadata
				indexroot=msg.FindInt8('indexroot')
				self.editorslist[indexroot].writter.acquire()
				self.editorslist[indexroot].pofile.metadata['Last-Translator']=defname # metadata saved from po settings
				self.editorslist[indexroot].pofile.metadata['PO-Revision-Date']=now
				self.editorslist[indexroot].pofile.metadata['X-Editor']=version
				thread.start_new_thread( self.editorslist[indexroot].Save, (bckppath,) )
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
						mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text().decode(self.encoding),self.listemsgstr[self.transtabview.Selection()].trnsl.Text().decode(self.encoding))
						thread.start_new_thread( self.tmcommunicate, (mx,) )


				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('translation')
				tabbi=msg.FindInt8('plurals')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				scheda.writter.acquire()
				entry = scheda.list.lv.ItemAt(tvindex).entry
				if entry and entry.msgid_plural:
						y=0
						textsavepl=[]
						entry.msgstr_plural[0] = textsave.decode(scheda.encodo)#self.encoding)
						while y < tabbi:
							varname='translationpl'+str(y)                                               ########################### give me one more eye?
							intended=msg.FindString(varname)
							textsavepl.append(intended) #useless???
							y+=1
							entry.msgstr_plural[y]=intended.decode(scheda.encodo)#self.encoding)
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						if entry.previous_msgid:
							entry.previous_msgid=None
						if entry.previous_msgid_plural:
							entry.previous_msgid_plural=None
						if entry.previous_msgctxt:
							entry.previous_msgctxt=None
				elif entry and not entry.msgid_plural:
						entry.msgstr = textsave.decode(scheda.encodo)#self.encoding)
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						if entry.previous_msgid:
							entry.previous_msgid=None
						if entry.previous_msgid_plural:
							entry.previous_msgid_plural=None
						if entry.previous_msgctxt:
							entry.previous_msgctxt=None
				scheda.pofile.metadata['Last-Translator']=defname
				scheda.pofile.metadata['PO-Revision-Date']=now
				scheda.pofile.metadata['X-Editor']=version
				thread.start_new_thread( scheda.Save, (bckppath,) )
				#scheda.pofile.save(bckppath)
				scheda.list.lv.ItemAt(tvindex).state=1
				scheda.list.lv.ItemAt(tvindex).tosave=False
				scheda.list.lv.ItemAt(tvindex).txttosave=""
				scheda.list.lv.ItemAt(tvindex).txttosavepl=[]
				return
			elif savetype == 3:
				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('tcomment')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				scheda.writter.acquire()
				entry = scheda.list.lv.ItemAt(tvindex).entry
				entry.tcomment=textsave
				scheda.pofile.metadata['Last-Translator']=defname
				scheda.pofile.metadata['PO-Revision-Date']=now
				scheda.pofile.metadata['X-Editor']=version
				thread.start_new_thread( scheda.Save, (bckppath,) )
				#scheda.pofile.save(bckppath)
				self.postabview.Select(intscheda)
				scheda.list.lv.DeselectAll()
				scheda.list.lv.Select(tvindex)
				return
			elif savetype == 4:
				textsave=msg.FindString('header')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				scheda.writter.acquire()
				scheda.pofile.header=textsave
				scheda.pofile.metadata['Last-Translator']=defname
				scheda.pofile.metadata['PO-Revision-Date']=now
				scheda.pofile.metadata['X-Editor']=version
				thread.start_new_thread( scheda.Save, (bckppath,) )
				#scheda.pofile.save(bckppath)
				return
			self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated()))
			return
			
		elif msg.what == 445380:
			#open procedure
			txtpath=msg.FindString("path")
			mimesuptbool = False
			mimesubtbool = False
			extbool = False
			mimeinstalled=False
			mimecheck = "True"
			self.NichilizeTM()
			if os.path.isfile(confile):
				try:
					Config.read(confile)
					mimecheck=ConfigSectionMap("Settings")['mimecheck']
				except: #(ConfigParser.NoSectionError):
					say = BAlert('Check Mimetype?', 'This is the first time you open a file, do you wish check the files for their mimetype?', 'Yes','No', None, None , 3)
					out=say.Go()
					Config.read(confile)
					cfgfile = open(confile,'w')
					try:
						Config.add_section('Settings')
					except:
						pass
					if out == 0:
						Config.set('Settings','mimecheck','True')
					else:
						Config.set('Settings','mimecheck','False')
					Config.write(cfgfile)
					cfgfile.close()

			if mimecheck == "True":
			#try:
				letsgo=False
				supt = msg.FindString("mime_supertype")
				if supt == "text" or supt == "application":
					mimesuptbool=True
					subt = msg.FindString("mime_subtype")
					if (subt == "x-gettext-translation") or (subt == "x-gettext-translation-template"): # mimetype is ok
						mimesubtbool = True
						letsgo=True
					else:
						mimesubtbool = False
						if subt == "plain" or subt == "octet-stream": #maybe gettext mimetype not installed
							extension = msg.FindString("extension")
							if extension == ".po" or extension == ".pot" or extension == ".mo":
								extbool = True
								letsgo=True
								mimeinstalled=True
							else:
								extbool = False
								letsgo=True
						else: 										# this is a different file, not a gettext one
							say = BAlert('oops', "this is not a gettext translation file but a "+subt+" "+supt, 'Ok',None, None, None, 3)
							say.Go()
							return
				else:							 # a totally different file, not a text-application file 
					mimesuptbool=False
					extension = msg.FindString("extension")
					if extension == ".po" or extension == ".pot" or extension == ".mo":    # but has the right extension
						extbool = True
						letsgo=True
					else:
						say = BAlert('oops', "This is not a gettext file, mimetype is: \'"+supt+"\' and his extension is: "+extension, 'Ok',None, None, None, 3)
						say.Go()
						return
				if letsgo:
					if setencoding:
						#try:
							try:
								Config.read(confile)
								usero = ConfigSectionMap("Users")['default']
								self.encoding = ConfigSectionMap(usero)['encoding']
							except:
								print "error setting up self.encoding, error reading config.ini"
								print "setting self.encoding as utf-8"
								self.encoding = "utf-8"
							fileenc = polib.detect_encoding(txtpath)
							if fileenc.lower() != self.encoding:
								say = BAlert('Cyd', "It seems that file encoding is different from user encoding. Choose the encoding to use globally.", "The file encoding","The user defined", "Abort loading",None,3) # TO FIX, use a BALERT or something else ,"do you wish to use user encoding setting, file encoding setting or abort loading the file?"
								#this will let you choose what to use, and set self.encoding accordingly
								out=say.Go()
								if out == 2:
									return
								elif out == 0:
									self.encoding = fileenc
							try:
								self.pof = polib.pofile(txtpath,encoding=self.encoding)
							except(UnicodeError):
								say = BAlert('Wrongenc', "Error loading the file with the selected encoding","Ok",None,None,None,4)
								say.Go()
								return
							except:
								say = BAlert('GenericError', "Error loading the file","Ok",None,None,None,4)
								say.Go()
								return
							if mimeinstalled:
								say = BAlert('oops', "The file is ok, but there's no gettext mimetype installed in your system", 'Ok',None, None, None, 3)
								say.Go()
							tfr = self.postabview.Bounds()
							trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])
							ordmdata=self.pof.ordered_metadata()
							a,b = checklang(ordmdata)
							if a and not b:
								say = BAlert('oops', "User language differs from po language", 'Go on',None, None, None, 3)
								say.Go()
							self.loadPOfile(txtpath,trc,self.pof,self.encoding)
							self.Nichilize()
							bounds = self.Bounds()
							l, t, r, b = bounds
							binds = self.background.Bounds()
							luwidth=self.lubox.Bounds()[2]-self.lubox.Bounds()[0]
							c,p,d,s = binds
							plygrnd2 = (5, b-142,r -luwidth-5, s-2)
							altece = self.srctabview.TabHeight()
							tabrc2 = (3, 3, plygrnd2[2] - plygrnd2[0], plygrnd2[3] - plygrnd2[1]-altece)
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
							self.transtablabels.append(BTab())
							self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
							################### BUG? ###################
							self.transtabview.Select(1)									###### bug fix
							self.transtabview.Select(0)
							#self.transtabview.Draw(self.transtabview.Bounds())
							self.listemsgid[0].src.SetText("")
							#self.srctabview.Select(1)
							#self.srctabview.Select(0)
							self.srctabview.Draw(self.srctabview.Bounds())
						#except:
						#	test = compiletest(mimesuptbool,mimesubtbool,extbool)
						#	say = BAlert('oops', 'Failed to load: '+test, 'Ok',None, None, None, 3)
						#	say.Go()
					else:
						# reinsert commented lines
						#try:
							self.encoding ="utf-8"
							self.pof = polib.pofile(txtpath,encoding=self.encoding)
							if mimeinstalled:
								say = BAlert('oops', "The file is ok, but there's no gettext mimetype installed in your system", 'Ok',None, None, None, 3)
								say.Go()
							tfr = self.postabview.Bounds()
							trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])
							ordmdata=self.pof.ordered_metadata()
							a,b = checklang(ordmdata)
							if a and not b:
								say = BAlert('oops', "User language differs from po language", 'Go on',None, None, None, 3)
								say.Go()
							self.loadPOfile(txtpath,trc,self.pof,self.encoding)
							self.Nichilize()
							bounds = self.Bounds()
							l, t, r, b = bounds
							binds = self.background.Bounds()
							luwidth=self.lubox.Bounds()[2]-self.lubox.Bounds()[0]
							c,p,d,s = binds
							plygrnd2 = (5, b-142,r -luwidth-5, s-2)
							altece = self.srctabview.TabHeight()
							tabrc2 = (3, 3, plygrnd2[2] - plygrnd2[0], plygrnd2[3] - plygrnd2[1]-altece)
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
							self.transtablabels.append(BTab())
							self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
							################### BUG? ###################
							self.transtabview.Select(1)									###### bug fix
							self.transtabview.Select(0)
							#self.transtabview.Draw(self.transtabview.Bounds())
							self.listemsgid[0].src.SetText("")
							#self.srctabview.Select(1)
							#self.srctabview.Select(0)
							self.srctabview.Draw(self.srctabview.Bounds())
			else:
				if setencoding:
					try:
						Config.read(confile)
						usero = ConfigSectionMap("Users")['default']
	#			cfgfile = open(confile,'w')
	#			try:
	#				Config.set(usero,'spell_esclusion',self.esclus.Text())
	#				Config.write(cfgfile)
	#			except:
	#				print "Cannot save esclusion chars"
	#			cfgfile.close()
	#			Config.read(confile)
						self.encoding = ConfigSectionMap(usero)['encoding']
					except:
						print "error reading encoding from config.ini for setting up self.encoding as mimecheck = False"
						print "setting self.encoding as utf-8"
						self.encoding="utf-8"
					################### TODO: check why here we are not loading anything? ################
				else:
					self.encoding="utf-8"
					self.pof = polib.pofile(txtpath,encoding=self.encoding)
					tfr = self.postabview.Bounds()
					trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])
					ordmdata=self.pof.ordered_metadata()
					a,b = checklang(ordmdata)
					if a and not b:
						say = BAlert('oops', "User language differs from po language", 'Go on',None, None, None, 3)
						say.Go()
					self.loadPOfile(txtpath,trc,self.pof,self.encoding)

			if len(self.editorslist) == 1:
				self.postabview.Draw(self.postabview.Bounds())
				#self.postabview.Select(1) # bug fix closing last one file and opening a new one
				#self.postabview.Select(0) # bug fix
				
			#except:
			#	e = None
			#if e is None:
			#		pass
			return
			
		elif msg.what == 71:
			# mark unmark as fuzzy
			if len(self.editorslist)>0:
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
					self.editorslist[self.postabview.Selection()].writter.acquire()
					self.workonthisentry = self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()).entry
					if 'fuzzy' in self.workonthisentry.flags:
						self.workonthisentry.flags.remove('fuzzy')
						if self.workonthisentry.previous_msgid:
							self.workonthisentry.previous_msgid=None
						if self.workonthisentry.previous_msgid_plural:
							self.workonthisentry.previous_msgid_plural=None
						if self.workonthisentry.previous_msgctxt:
							self.workonthisentry.previous_msgctxt=None
						self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()).state=1
					else:
						self.workonthisentry.flags.append('fuzzy')
						self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()).state=2
					self.editorslist[self.postabview.Selection()].Hide()
					self.editorslist[self.postabview.Selection()].Show() #Updates the MsgStrItem
					self.editorslist[self.postabview.Selection()].writter.release()
					bckpmsg=BMessage(16893)
					bckpmsg.AddInt8('savetype',0)
					bckpmsg.AddString('bckppath',self.editorslist[self.postabview.Selection()].backupfile)
					BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
					#self.editorslist[self.postabview.Selection()].list.reload(self.poview,self.editorslist[self.postabview.Selection()].pofile,self.encoding)
			return
		
		elif msg.what == 8384:
			self.analysisW=Analysis(self.editorslist[self.postabview.Selection()].encodo)#self.encoding)
			self.analysisW.Show()
			i = 1
			w = BApplication.be_app.CountWindows()
			while w > i:
				if BApplication.be_app.WindowAt(i).Title()=="String analysis":
					thiswindow=i
				i+=1
			if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
				caratars=self.listemsgstr[self.transtabview.Selection()].trnsl.Analisi()
				for items in caratars:
					pmsg=BMessage(43285)
					pmsg.AddString('word',items[0])
					BApplication.be_app.WindowAt(thiswindow).PostMessage(pmsg)
					pmsg=BMessage(43250)
					pmsg.AddString('word',items[1])
					BApplication.be_app.WindowAt(thiswindow).PostMessage(pmsg)
				copytxt = self.listemsgstr[self.transtabview.Selection()].trnsl.Text()
				pmsg=BMessage(43288)
				pmsg.AddString('text',copytxt)
				BApplication.be_app.WindowAt(thiswindow).PostMessage(pmsg)

		elif msg.what == 12343:
			if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
				try:
					self.listemsgstr[self.transtabview.Selection()].trnsl.CheckSpell()
				except:
					pass

		elif msg.what == 54173:
			#Save as 
			txt=self.editorslist[self.postabview.Selection()].fp.GetPanelDirectory()
			savepath= BEntry(txt,True).GetPath().Path()
			e = msg.FindString("name")
			completepath = savepath +"/"+ e
			actualtab=self.editorslist[self.postabview.Selection()]
			actualtab.pofile.save(completepath)
			actualtab.name=e
			actualtab.percors=completepath
			actualtab.pofile= polib.pofile(completepath,encoding=actualtab.encoding)
			self.tabslabels[self.postabview.Selection()].SetLabel(e);
			actualtab.filen, actualtab.file_ext = os.path.splitext(completepath)
			actualtab.backupfile= actualtab.filen+".temp"+actualtab.file_ext
			return

		elif msg.what == 83419:
			self.NichilizeTM()

		elif msg.what == 104501:
			self.tmscrollsugj.lv.AddItem(ErrorItem("┌─────────────────────┐"))#───────────────────────────────────
			self.tmscrollsugj.lv.AddItem(ErrorItem("     Error connecting to Translation Memory server     "))
			self.tmscrollsugj.lv.AddItem(ErrorItem("└─────────────────────┘"))#──────────────────────────────
			return
		elif msg.what == 460550:
			# selection from listview
			#if tm:
			#	self.NichilizeTM()
			bounds = self.Bounds()
			l, t, r, b = bounds
			binds = self.background.Bounds()
			luwidth=self.lubox.Bounds()[2]-self.lubox.Bounds()[0]
			c,p,d,s = binds
			plygrnd1 = (5,b-268,r - luwidth-5, s-120)
			plygrnd2 = (5, b-142,r -luwidth-5, s-2)
			altece = self.srctabview.TabHeight()
			tabrc = (3.0, 3.0, plygrnd1[2] - plygrnd1[0], plygrnd1[3] - plygrnd1[1]-altece)
			tabrc2 = (3, 3, plygrnd2[2] - plygrnd2[0], plygrnd2[3] - plygrnd2[1]-altece)
			END_DOWN_MSG = struct.unpack('!l', '_KYD')[0]
			END_UP_MSG = struct.unpack('!l', '_KYU')[0]
			if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
				
#				txttosearch=self.editorslist[self.postabview.Selection()].list.SelectedText()
#				
#				#######  check for multiple occurencies just for debug ########
#				count=0
#				for entry in self.editorslist[self.postabview.Selection()].pofile:
#					if entry.msgid.encode(self.encoding) == txttosearch:
#						count = count +1
#						if count > 1:
#							print "multiple occurrencies for this entry msgid"
#							break
#				################################################################
				item=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
				if item.hasplural:
							beta=len(item.msgstrs)
							self.Nichilize()
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr[0]',altece,self))
							self.transtablabels.append(BTab())
							self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
							self.listemsgid.append(srctabbox((3,3,self.listemsgid[0].Bounds()[2]+3,self.listemsgid[0].Bounds()[3]+3),'msgid_plural',altece))
							self.srctablabels.append(BTab())
							self.srctabview.AddTab(self.listemsgid[1], self.srctablabels[1])
							x=len(self.listemsgid)-1
							self.srctabview.SetFocusTab(x,True)
							self.srctabview.Select(x)
							self.srctabview.Select(0)
							self.listemsgid[0].src.SetText(item.msgids[0].encode(self.editorslist[self.postabview.Selection()].encodo))#self.encoding))
							self.listemsgid[1].src.SetText(item.msgids[1].encode(self.editorslist[self.postabview.Selection()].encodo))#self.encoding))
							ww=0
							while ww<beta:
								self.transtablabels.append(BTab())
								if ww == 0:
									self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs[0].encode(self.editorslist[self.postabview.Selection()].encodo))#self.encoding))
									self.transtabview.SetFocusTab(x,True)
									self.transtabview.Select(x)
									self.transtabview.Select(0)
								else:
									self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr['+str(ww)+']',altece,self))
									self.listemsgstr[ww].trnsl.SetPOReadText(item.msgstrs[ww].encode(self.editorslist[self.postabview.Selection()].encodo))#self.encoding))
									self.transtabview.AddTab(self.listemsgstr[ww],self.transtablabels[ww])
								ww=ww+1
				else:
							self.Nichilize()
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
							self.transtablabels.append(BTab())
							self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
#######################################################################
							self.listemsgid[0].src.SetText(item.msgids.encode(self.editorslist[self.postabview.Selection()].encodo))#self.encoding))
							self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs.encode(self.editorslist[self.postabview.Selection()].encodo))#self.encoding))
############################### bugfix workaround? ####################						 
							self.transtabview.Select(1)									#################  <----- needed to fix
							self.transtabview.Select(0)									#################  <----- a bug, tab0 will not appear
							#self.transtabview.Draw(self.transtabview.Bounds())
							#self.srctabview.Select(1)									#################  <----- so forcing a tabview update
							#self.srctabview.Select(0)
							self.srctabview.Draw(self.srctabview.Bounds())
				self.valueln.SetText(str(item.linenum))
				asd,sdf,dfg,fgh=self.lubox.Bounds()
				hig=round(self.lubox.GetFontHeight()[0])
				if item.comments!="":
					try:
						self.commentview.RemoveSelf()
						self.scrollcomment.RemoveSelf()
						self.headlabel.RemoveSelf()
					except:
						pass
					self.headlabel=BStringView((4,4,dfg-4,hig+4),"Header","Comments:",B_FOLLOW_TOP|B_FOLLOW_LEFT)
					self.commentview=BTextView((8,4+hig,dfg-26,200),"commentview",(4,4,179,197),B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT)
					self.commentview.MakeEditable(False)
					self.lubox.AddChild(self.headlabel)
					self.scrollcomment=BScrollBar((dfg-24,4+hig,dfg-8,200),'commentview_ScrollBar',self.commentview,0.0,0.0,B_VERTICAL)
					self.lubox.AddChild(self.scrollcomment)
					self.lubox.AddChild(self.commentview)
					self.commentview.SetText(item.comments)
				else:
					try:
						self.commentview.RemoveSelf()
						self.scrollcomment.RemoveSelf()
						self.headlabel.RemoveSelf()
					except:
						pass
				if item.context!="":
					try:
						self.contextview.RemoveSelf()
						self.scrollcontext.RemoveSelf()
						self.contextlabel.RemoveSelf()
					except:
						pass
					self.contextlabel=BStringView((4,208,dfg-4,hig+208),"Context","Context:",B_FOLLOW_TOP|B_FOLLOW_LEFT)
					self.lubox.AddChild(self.contextlabel)
					self.contextview=BTextView((8,hig+208,dfg-26,300),"contextview",(4,4,179,292),B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT)
					self.contextview.MakeEditable(False)
					self.scrollcontext=BScrollBar((dfg-24,hig+208,dfg-8,300),'contextview_ScrollBar',self.contextview,0.0,0.0,B_VERTICAL)
					self.lubox.AddChild(self.scrollcontext)
					self.lubox.AddChild(self.contextview)
					self.contextview.SetText(item.context)
				else:
					try:
						self.contextview.RemoveSelf()
						self.scrollcontext.RemoveSelf()
						self.contextlabel.RemoveSelf()
					except:
						pass
				if item.tcomment!="":
					try:
						self.tcommentview.RemoveSelf()
						self.scrolltcomment.RemoveSelf()
						self.tcommentlabel.RemoveSelf()
					except:
						pass
					self.tcommentlabel=BStringView((4,408,dfg-4,hig+408),"Tcomment","Translator comment:",B_FOLLOW_TOP|B_FOLLOW_LEFT)
					self.lubox.AddChild(self.tcommentlabel)
					self.tcommentview=BTextView((8,hig+408,dfg-26,500),"tcommentview",(4,4,179,292),B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT)
					self.tcommentview.MakeEditable(False)
					self.scrolltcomment=BScrollBar((dfg-24,hig+408,dfg-8,500),'tcommentview_ScrollBar',self.tcommentview,0.0,0.0,B_VERTICAL)
					self.lubox.AddChild(self.scrolltcomment)
					self.lubox.AddChild(self.tcommentview)
					self.tcommentview.SetText(item.tcomment)
				else:
					try:
						self.tcommentview.RemoveSelf()
						self.scrolltcomment.RemoveSelf()
						self.tcommentlabel.RemoveSelf()
					except:
						pass
				if item.previous:
					try:
						self.previousview.RemoveSelf()
						self.scrollprevious.RemoveSelf()
						self.labelprevious.RemoveSelf()
					except:
						pass
					
					self.labelprevious=BStringView((4,308,dfg-4,hig+308),"Previous","Previous:",B_FOLLOW_TOP|B_FOLLOW_LEFT)
					self.lubox.AddChild(self.labelprevious)
					self.previousview=BTextView((8,hig+308,dfg-26,400),"previousview",(4,4,dfg-asd-36,fgh/3-8),B_FOLLOW_TOP|B_FOLLOW_LEFT_RIGHT,B_WILL_DRAW)
					self.previousview.MakeEditable(False)
					self.scrollprevious=BScrollBar((dfg-24,hig+308,dfg-8,400),'previousview_ScrollBar',self.previousview,0.0,0.0,B_VERTICAL)
					self.lubox.AddChild(self.scrollprevious)
					resultxt=""
					bolds=[]
					plain=[]
					color1=(0,0,0,0)
					color2=(50,50,50,0)
					command=[]
					for items in item.previousmsgs:
						actualtxt= items[0]+":\n"+items[1]+"\n"
						resultxt += actualtxt
						minornum=resultxt.find(actualtxt)
						mid=actualtxt.find(items[1])
						plainadd=minornum+mid
						command.append((minornum,be_bold_font, color1))
						command.append((plainadd,be_plain_font, color2))
					self.previousview.SetStylable(1)
					self.previousview.SetText(resultxt, command)
					self.lubox.AddChild(self.previousview)
				else:
					try:
						self.previousview.RemoveSelf()
						self.scrollprevious.RemoveSelf()
						self.labelprevious.RemoveSelf()
					except:
						pass
				self.listemsgstr[0].trnsl.MakeFocus()

#							beta=len(sorted(entry.msgstr_plural.keys()))
				
				############################ GO TO THE END OF THE TEXT #############################
				lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
				self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
#				num=self.listemsgstr[self.transtabview.Selection()].trnsl.CountLines()
#				self.listemsgstr[self.transtabview.Selection()].trnsl.GoToLine(num)
				self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
				if tm:
					if deb:
						print ("da richiedere: ",self.listemsgid[self.srctabview.Selection()].src.Text())
					#TODO: azzerare ScrollSugj
					#print "eseguo riga: 4984"
					thread.start_new_thread( self.tmcommunicate, (self.listemsgid[self.srctabview.Selection()].src.Text(),) )
					
			else:
				if tm:
					self.NichilizeTM()
				self.Nichilize()				
				self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
				self.transtablabels.append(BTab())
				self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
				################### BUG? ###################
				self.transtabview.Select(1)									#################  <----- needed to fix a bug
				self.transtabview.Select(0)
				#print "ho eseguito transtabview.Draw()"
				#self.transtabview.Draw(self.transtabview.Bounds())
				#############################################
				self.listemsgid[0].src.SetText("")
			return


		elif msg.what ==  777:
			#Removing B_AVOID_FOCUS flag
			self.SetFlags(0)
			return
		elif msg.what == 222888:
			# stylize eventtextview for checkspell
			evstyle.acquire()
			self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.listemsgstr[self.transtabview.Selection()].trnsl.Text(),self.listemsgstr[self.transtabview.Selection()].trnsl.evstile)
			evstyle.release()
			self.listemsgstr[self.transtabview.Selection()].trnsl.Select(msg.FindInt32("start"),msg.FindInt32("end"))
			self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
			return
		elif msg.what == 963741:
			schplur = msg.FindInt8('plural')
			#schsrcplur = msg.FindInt8('srcplur')
			self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
			self.transtabview.Select(schplur)
			if schplur>0:
				self.srctabview.Select(1)
			inizi=msg.FindInt32('inizi')
			fin=msg.FindInt32('fin')
			srctrnsl=msg.FindInt8('srctrnsl')
			#indolor=msg.FindInt8('index')
			name=time.time()
			thread.start_new_thread( self.highlightlater, (str(name),inizi, fin,schplur,srctrnsl,) )
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
		elif msg.what == 333111:
			self.speloc.acquire()
			self.intime=time.time()
			self.speloc.release()
			return
		elif msg.what == 7484:
			self.spellcount.SetText(msg.FindString('graph'))
			return
		elif msg.what == 946389:
			percors=msg.FindString("percors")
			filo=open("/boot/home/where.txt","w")
			filo.write(percors)
			filo.close()
			return
		elif msg.what == 5391359:
			r=msg.FindInt16('totsugj')
			act=0
			while act<r:
				self.tmscrollsugj.lv.AddItem(SugjItem(msg.FindString('sugj_'+str(act)),msg.FindInt8('lev_'+str(act))))
				act+=1
			#se tra gli elementi non c'è 100% ma il BListItem è segnato come tradotto, è il caso di inviarlo al file tmx
			if self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()).state == 1:	
				if self.tmscrollsugj.lv.CountItems()>0:
					if self.tmscrollsugj.lv.ItemAt(0).percent < 100:
						mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text().decode(self.encoding),self.listemsgstr[self.transtabview.Selection()].trnsl.Text().decode(self.encoding))
						thread.start_new_thread( self.tmcommunicate, (mx,) )
						#print "beh, questo è corretto ma ha suggerimenti sbagliati, salvare in tmx!"
				else:
					mx=(None,self.listemsgid[self.srctabview.Selection()].src.Text().decode(self.encoding),self.listemsgstr[self.transtabview.Selection()].trnsl.Text().decode(self.encoding))
					#print "eseguo riga: 5083"
					thread.start_new_thread( self.tmcommunicate, (mx,) )
					#print "mah, questo è corretto ma non ha suggerimenti, da salvare in tmx!"
			return
		elif msg.what == 738033:
			if tm:
				self.NichilizeTM()
			thread.start_new_thread(self.tmcommunicate,(msg.FindString('s'),))
			return
		elif msg.what == 141:
			#copia testo da scrollsugj su transtabview attuale
			try:
				self.listemsgstr[self.transtabview.Selection()].trnsl.SetText(self.tmscrollsugj.lv.ItemAt(self.tmscrollsugj.lv.CurrentSelection()).Text())
				self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus()
				lngth=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
				self.listemsgstr[self.transtabview.Selection()].trnsl.Select(lngth,lngth)
				self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToSelection()
				#notifica necessità di salvataggio
				self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
			except:
				if deb:
					print "Not a SugjItem, but an ErrorItem as not having .Text() function"
			return
		else:
			BWindow.MessageReceived(self, msg)
	
	def	speloop(self):
		if deb:
			print "start speloop"
		ev = threading.Event()
		global quitter
		quitter = True
		t1 = time.time()
		steps=['˹','  ˺','  ˼','˻']
		y=0
		while quitter:
			self.speloc.acquire()
			tbef = self.intime
			self.speloc.release()
			ev.wait(0.5)
			mux=BMessage(7484)
			mux.AddString('graph',str(steps[y]))
			BApplication.be_app.WindowAt(0).PostMessage(mux)
			self.speloc.acquire()
			taft = self.intime
			self.speloc.release()
			if tbef == taft:
				if taft > t1:
					if len(self.listemsgstr)>0:
						traduzion=self.listemsgstr[self.transtabview.Selection()].trnsl.Text()
						if traduzion != "":
							BApplication.be_app.WindowAt(0).PostMessage(12343)
				t1 = time.time()
			y+=1
			if y == len(steps):
				y=0
		if deb:
			print "end speloop"
			
		
	def highlightlater(self,name,inizi,fin,schede,srctrnsl): #why name?     <--------------------
		if deb:
			print "start highlightlater"
		self.event.wait(0.1)
		if srctrnsl==0:
			mexacio = BMessage(852630)
		else:
			mexacio = BMessage(852631)
		mexacio.AddInt32("inizi",inizi)
		mexacio.AddInt32("fin",fin)
		mexacio.AddInt8("schede",schede)
#		mexacio.AddInt8("srctrnsl",srctrnsl)
		BApplication.be_app.WindowAt(0).PostMessage(mexacio)
		if deb:
			print "end highlightlater"
		
			
	def  loadPOfile(self,pathtofile,bounds,pofile,encodo):
			# add a tab in the editor's tabview
			head, tail = os.path.split(pathtofile)
			startTime = time.time()
			filen, file_ext = os.path.splitext(pathtofile)
			backupfile = filen+".temp"+file_ext
			if os.path.exists(backupfile):
				if os.path.getmtime(backupfile)>os.path.getmtime(pathtofile):
					say = BAlert('Backup exist', 'There\'s a recent temporary backup file, open it instead?', 'Yes','No', None, None , 3)
					out=say.Go()
					if out == 0:
#						apro il backup
						temppathtofile=backupfile
						temppofile = polib.pofile(backupfile,encoding=encodo)#self.encoding)
						self.editorslist.append(POEditorBBox(bounds,tail,temppathtofile,temppofile,self.poview,encodo,True))
					else:
#						apro il file originale
						self.editorslist.append(POEditorBBox(bounds,tail,pathtofile,pofile,self.poview,encodo,False))
				else:
#					apro il file originale
					self.editorslist.append(POEditorBBox(bounds,tail,pathtofile,pofile,self.poview,encodo,False))
			else:
#				apro il file originale
				self.editorslist.append(POEditorBBox(bounds,tail,pathtofile,pofile,self.poview,encodo,False))
			executionTime = (time.time() - startTime)
			print('Load-time in seconds: ' + str(executionTime))
			self.tabslabels.append(BTab())
			x=len(self.editorslist)-1
			self.postabview.AddTab(self.editorslist[x], self.tabslabels[x])
			self.postabview.SetFocusTab(x,True)
			self.postabview.Select(x)
			self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated()))
			self.postabview.Hide()
			self.postabview.Show()
			
			
	def QuitRequested(self):
		print "So long and thanks for all the fish"
		BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
		return 1
		
def checklang(orderedata):
	Config.read(confile)
	try:
		usero = ConfigSectionMap("Users")['default']
		cfgchklng=Config.getboolean('Settings', 'checklang')
		if cfgchklng:
			retu=False
			for e in orderedata:
				if e[0]=='Language':
					if e[1] == ConfigSectionMap(usero)['lang']:
						retu = True
			return (cfgchklng,retu) 
		else:
			return (cfgchklng,False)
	except:
		try:
			cfgfile = open(confile,'w')
			Config.set('Settings','checklang','False')
			Config.write(cfgfile)
			cfgfile.close()
		except:
			pass
		return (False,False)

class HaiPOApp(BApplication.BApplication):
	def __init__(self):
		BApplication.BApplication.__init__(self, "application/x-vnd.HaiPO-Editor")



	def ReadyToRun(self):
		window((100,80,960,720))

	def ArgvReceived(self, argv):
		global deb
		if deb:
			i=0
			strigo=""
			while i < len(argv):
				strigo=strigo+argv[i]+" "
				i+=1
			filo=open("/boot/home/argv.txt","w")
			filo.write(strigo)
			filo.close()
		i=2
		while i < len(argv):
			if os.path.exists(argv[i]):
				entryref=BEntry(argv[i])
				percors = entryref.GetPath()
				mksg=BMessage(B_REFS_RECEIVED)
				mksg.AddRef("refs",entryref.GetRef())
				self.RefsReceived(mksg);
			elif argv[i]=='-d':
				deb=True
				print "Debug Mode ON"
			i+=1
		
	def RefsReceived(self, msg):
		
		if msg.what == B_REFS_RECEIVED:
			if deb:
				import io
				real_stdout=sys.stdout
				fake_stdout=io.BytesIO()
				try:
					sys.stdout=fake_stdout
					o=0
					while o<msg.CountNames(B_ANY_TYPE):
						print msg.GetInfo(B_ANY_TYPE,o)
						o+=1				
				finally:
					sys.stdout=real_stdout
					outputstring=fake_stdout.getvalue()
					filo=open("/boot/home/mex.txt","w")
					filo.write(outputstring)
					filo.close()
					fake_stdout.close()
			i = 0
			while 1:
				try:
					e = msg.FindRef("refs", i)
					entryref = BEntry(e,True)
					percors = entryref.GetPath()
					self.txtpath= percors.Path()
					if deb:
						filo=open("/boot/home/refrecpath.txt","w")
						filo.write(percors.Path())
						filo.close()
					mehh=BMessage(183654)
					mehh.AddString("percors",percors.Path())
					BApplication.be_app.PostMessage(mehh)
				except:
					e = None
				if e is None:
					break
				i = i + 1
				
	def MessageReceived(self, msg):
		if msg.what == B_SAVE_REQUESTED:
			e = msg.FindString("name")
			messaggio = BMessage(54173)
			messaggio.AddString("name",e)
			BApplication.be_app.WindowAt(0).PostMessage(messaggio)
			return
		if msg.what == 183654:
			percors=msg.FindString("percors")
			self.elaborate_path(os.path.abspath(percors))
			if deb:
				mah=BMessage(946389)
				mah.AddString("percors",percors)
				BApplication.be_app.WindowAt(0).PostMessage(mah)

	def elaborate_path(self,percors):
					reallaunchpath=os.path.realpath(sys.argv[0])
					if percors == reallaunchpath:
						return
					self.txtpath = percors
					filename, file_extension = os.path.splitext(self.txtpath)
					static = BMimeType()
					mime = static.GuessMimeType(self.txtpath)
					mimetype = repr(mime.Type()).replace('\'','')
					supertype,subtype = mimetype.split('/')
					smesg=BMessage(445380)
					smesg.AddString("path",self.txtpath)
					smesg.AddString("extension",file_extension)
					smesg.AddString("mime_supertype",supertype)
					smesg.AddString("mime_subtype",subtype)
					BApplication.be_app.WindowAt(0).PostMessage(smesg)
				
	def QuitRequested(self):
		quitter = False
		return 1
		

def compiletest(supt,subt,ext):
	if supt:
		if subt:
			test = "Mime supertype and subtype are ok! but failed anyway. Check the file!"
		else:
			if ext:
				test = "Mime supertype and file extension are ok, but NOT mime subtype. Check the file!"
			else:
				test = "Only mime supertype is ok. Wrong file!?"
	else:
		if ext:
			test = "Mime is wrong but extension is ok, check the file!"
		else:
			test = "This should not be viewed"
	return test
		
		
def window(rectangle):
	window = PoWindow(rectangle)
	window.Show()

global notready
notready=True

HaiPO = HaiPOApp()
HaiPO.Run()
