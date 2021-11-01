#!/boot/system/bin/python
# -*- coding: utf-8 -*-

#   A Simple PO editor for Haiku.
#   Copyright (C) 2021  Fabio Tomat
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>


#******************************************************
#
# Notes: implementare X-generator
#
#******************************************************

import os,sys,ConfigParser,struct,re,threading
try:
	import polib
except:
	print "Your python environment has no polib module"

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
global confile
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
#	cfgfile = open(confile,'w')
#	Config.add_section('Users')
#	Config.set('User','names', "") #Pippo,Pierino,
#	Config.set('User','default', "") #Pippo
#	cfgfile.close()


#	Config.set('Pippo','name', "Pippo Franco")
#	Config.set('Pippo','lang', "fur")
#	Config.set('Pippo','team', "Friulian")
#	Config.set('Pippo','pe-mail', "f.t.public@gmail.com")
#	Config.set('Pippo','te-mail', "fur@li.org")

jes = False

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
	from BAlert import BAlert
	from BListItem import BListItem
	from BStatusBar import BStatusBar
	from BTranslationUtils import *
	from BFile import BFile
	from BNode import BNode
	from BMimeType import BMimeType
	from BCheckBox import BCheckBox
	from BView import BView
#	import BFilePanel, BEntry
	from BFilePanel import BFilePanel
	from BEntry import BEntry
	from BScrollBar import BScrollBar
	from InterfaceKit import B_PAGE_UP,B_PAGE_DOWN,B_TAB,B_ESCAPE,B_DOWN_ARROW,B_UP_ARROW,B_V_SCROLL_BAR_WIDTH,B_FULL_UPDATE_ON_RESIZE,B_VERTICAL,B_FOLLOW_ALL,B_FOLLOW_TOP,B_FOLLOW_LEFT,B_FOLLOW_RIGHT,B_WIDTH_FROM_LABEL,B_TRIANGLE_THUMB,B_BLOCK_THUMB,B_FLOATING_WINDOW,B_TITLED_WINDOW,B_WILL_DRAW,B_NAVIGABLE,B_FRAME_EVENTS,B_ALIGN_CENTER,B_FOLLOW_ALL_SIDES,B_MODAL_WINDOW,B_FOLLOW_TOP_BOTTOM,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT_RIGHT,B_SINGLE_SELECTION_LIST,B_NOT_RESIZABLE,B_NOT_ZOOMABLE,B_PLAIN_BORDER,B_FANCY_BORDER,B_NO_BORDER,B_ITEMS_IN_COLUMN,B_AVOID_FOCUS
	from AppKit import B_QUIT_REQUESTED,B_KEY_UP,B_KEY_DOWN,B_MODIFIERS_CHANGED,B_UNMAPPED_KEY_DOWN,B_REFS_RECEIVED,B_SAVE_REQUESTED,B_CANCEL,B_WINDOW_RESIZED
	from StorageKit import B_SAVE_PANEL,B_OPEN_PANEL,B_FILE_NODE,B_READ_ONLY
	from SupportKit import B_ERROR,B_ENTRY_NOT_FOUND,B_OK
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
	def __init__(self,frame,name,lang,team,pemail,temail,default):
		self.frame=frame
		self.name=name
		BBox.__init__(self,self.frame,name,B_FOLLOW_LEFT | B_FOLLOW_TOP,B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)#self.name,B_FOLLOW_ALL_SIDES,B_WILL_DRAW)
		bounds=self.Bounds()
		l,t,r,b = bounds
		h=round(self.GetFontHeight()[0])
		self.username = BTextControl((20, 16, r - 50, h + 18 ), 'name', 'Profile name:', name, BMessage(6))#b - 16
		self.lang = BTextControl((20, 32 + h, r - 50, 2*h + 50), 'lang', 'Language:', lang, BMessage(7))
		self.team = BTextControl((20, 48 + 2*h, r - 50, 3*h + 66), 'team', 'Team name:', team, BMessage(8))
		self.pemail = BTextControl((20, 64 + 3*h, r - 50, 4*h + 82), 'pemail', 'Personal e-mail:', pemail, BMessage(9))
		self.temail = BTextControl((20, 80 + 4*h, r - 50, 5*h + 98), 'temail', 'Team e-mail:', temail, BMessage(10))
		self.default = BCheckBox((20, 5*h + 101, r - 50, 6*h + 119),'chkdef','Default user',BMessage(150380))
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
		self.userstabview = BTabView((5.0, 5.0, r-5, t+6*h+190), 'tabview')#,B_WIDTH_FROM_LABEL,B_FOLLOW_ALL,B_NAVIGABLE)
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
				if name == defaultuser:
					self.userviewlist.append(PeopleBView(tfr,name,lang,team,pemail,temail,True))
				else:
					self.userviewlist.append(PeopleBView(tfr,name,lang,team,pemail,temail,False))
				self.tabslabels.append(BTab())
				self.userstabview.AddTab(self.userviewlist[x], self.tabslabels[x])
				x=x+1
		except:
			say = BAlert('Oops', 'No config file or users found', 'Ok',None, None, None, 3)
			say.Go()
			self.Quit()
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
			BApplication.be_app.WindowAt(0).PostMessage(777)
			self.Quit()
			return
		elif msg.what == 295050:
			l,t,r,b = self.Bounds()
			#self.ResizeTo(300.0,300.0)
			#self.introtxt.Hide()
			self.introtxt2.Hide()
			self.ProceedButton.Hide()
			self.CloseButton.Hide()
			self.ResizeBy(0.0,300.0)
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
	kWindowFrame = (150, 150, 650, 620)
	kButtonFrame = (395, 425, 490, 460)
	kWindowName = "About"
	kButtonName = "Close"
	BUTTON_MSG = struct.unpack('!l', 'PRES')[0]

	def __init__(self):							
		BWindow.__init__(self, self.kWindowFrame, self.kWindowName, B_MODAL_WINDOW, B_NOT_RESIZABLE)#|B_WILL_DRAW
		bbox=BBox((0,0,500,470), 'underbox', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(bbox)
		self.CloseButton = BButton(self.kButtonFrame, self.kButtonName, self.kButtonName, BMessage(self.BUTTON_MSG))		
		cise=(10,4,490,420)
		cjamput=(0,0,480,420)
		self.messagjio= BTextView(cise, 'TxTView', cjamput, B_FOLLOW_ALL, B_WILL_DRAW)
		self.messagjio.SetStylable(1)
		self.messagjio.MakeSelectable(0)
		self.messagjio.MakeEditable(0)
		stuff = '\n\t\t\t\t\t\t\t\tHaiPO\n\n\t\t\t\t\t\t\t\t\t\t\tA simple PO editor\n\t\t\t\t\t\t\t\t\t\t\tfor Haiku, version 0.1\n\t\t\t\t\t\t\t\t\t\t\tcodename "Pobeda"\n\n\t\t\t\t\t\t\t\t\t\t\tby Fabio Tomat aka TmTFx\n\t\t\t\t\t\t\t\t\t\t\te-mail:\n\t\t\t\t\t\t\t\t\t\t\tf.t.public@gmail.com\n\n\n\n\nGNU GENERAL PUBLIC LICENSE:\nThis program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program.  If not, see \n<http://www.gnu.org/licenses/>'
		n = stuff.find('HaiPO')
		m = stuff.find('This')
		self.messagjio.SetText(stuff, [(0, be_plain_font, (0, 0, 0, 0)), (n, be_bold_font, (0, 150, 0, 0)), (n + 5, be_plain_font, (0, 0, 0, 0)),(m,be_plain_font,(100,150,0,0))])
		bbox.AddChild(self.messagjio)
		bbox.AddChild(self.CloseButton)
		self.CloseButton.MakeFocus(1)
		link=sys.path[0]+"/data/HaiPO.png"
		self.img=BTranslationUtils.GetBitmap(link)
		self.photoframe=PView((40,40,255,255),"photoframe",self.img)
		bbox.AddChild(self.photoframe)

	def MessageReceived(self, msg):
		if msg.what == self.BUTTON_MSG:
			self.Quit()
		else:
			return


class ScrollView:
	HiWhat = 32 #Doppioclick --> set as fuzzy?
	Selmsgstr = 460550

	def __init__(self, rect, name):#, OPTION, type):
		self.lv = BListView(rect, name, B_SINGLE_SELECTION_LIST,B_FOLLOW_ALL_SIDES,B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_FRAME_EVENTS)#,OPTION)
		msg=BMessage(self.Selmsgstr)
		self.lv.SetSelectionMessage(msg)
		msg = BMessage(self.HiWhat)
		self.lv.SetInvocationMessage(msg)
		self.sv = BScrollView('ScrollView', self.lv, B_FOLLOW_ALL_SIDES, B_FULL_UPDATE_ON_RESIZE|B_WILL_DRAW|B_NAVIGABLE|B_FRAME_EVENTS, 0, 0, B_FANCY_BORDER)

	def reload(self,arrayview,pofile,encoding):
			i=0
			while self.lv.CountItems()>i:
				self.lv.RemoveItem(self.lv.ItemAt(0))
			if arrayview[0]:
				for entry in pofile.fuzzy_entries():
					if entry and entry.msgid_plural:
						print (entry.msgid + " has plural")
						item = MsgStrItem(entry.msgid,2,encoding,True)
					else:
						item = MsgStrItem(entry.msgid,2,encoding,False)
					self.lv.AddItem(item)
			if arrayview[1]:
				for entry in pofile.untranslated_entries():
					if entry and entry.msgid_plural:
						print (entry.msgid + " has plural")
						item = MsgStrItem(entry.msgid,0,encoding,True)
					else:
						item = MsgStrItem(entry.msgid,0,encoding,False)
					self.lv.AddItem(item)
			if arrayview[2]:
				for entry in pofile.translated_entries():
					if entry and entry.msgid_plural:
						print (entry.msgid + " has plural")
						item = MsgStrItem(entry.msgid,1,encoding,True)
					else:
						item = MsgStrItem(entry.msgid,1,encoding,False)
					self.lv.AddItem(item)
			if arrayview[3]:
				for entry in pofile.obsolete():
					if entry and entry.msgid_plural:
						print (entry.msgid + " has plural")
						item = MsgStrItem(entry.msgid,3,encoding,True)
					else:
						item = MsgStrItem(entry.msgid,3,encoding,False)
					self.lv.AddItem(item)
			self.lv.DeselectAll()

			#self.lv.Select(0) no need to select anything
		
	def SelectedText(self):
			return self.lv.ItemAt(self.lv.CurrentSelection()).Text()

	def topview(self):
		return self.sv

	def listview(self):
		return self.lv


		
class MsgStrItem(BListItem):
	nocolor = (0, 0, 0, 0)
	####  states table
	untranslated = 0
	translated = 1
	fuzzy = 2
	obslete = 3
	hasplural = False
	frame=[0,0,0,0]

	def __init__(self, text,state,encoding,plural):
		self.text = text.encode(encoding)  #it's in english should this be always utf-8
		self.state=state
		self.hasplural=plural
		BListItem.__init__(self)

	def DrawItem(self, owner, frame,complete):
		self.frame = frame
		#complete = True
		if self.IsSelected() or complete: # 
			color = (200,200,200,255)
			owner.SetHighColor(color)
			owner.SetLowColor(color)
			owner.FillRect(frame)
			if self.state == 0: 
				self.color = (0,0,255,0)
			elif self.state == 1:
				self.color = self.nocolor
			elif self.state == 2:
				self.color = (153,153,0,0)
			elif self.state == 3:
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
			owner.DrawString('Pl >>')
			owner.SetHighColor(self.color)
			self.font = be_plain_font
			owner.SetFont(self.font)
			owner.MovePenTo(frame[0]+30,frame[3]-2)
			owner.DrawString(self.text)
		else:
			owner.SetHighColor(self.color)
			owner.MovePenTo(frame[0],frame[3]-2)
			owner.DrawString(self.text)
			owner.SetLowColor((255,255,255,255))
		#owner.StrokeTriangle((float(frame[2]-10),float(frame[3]+3)),(frame[2]-2,frame[3]+3),(frame[2]-6,frame[3]+7.5));#,B_SOLID_HIGH
		
	def Text(self):
		return self.text


class EventTextView(BTextView):
	def __init__(self,superself,frame,name,textRect,resizingMode,flags):
		self.superself=superself
		self.oldtext=""
		self.oldtextloaded=False
		self.tosave=False
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)

	def KeyDown(self,char,bytes):
		
		####################### TODO   controllo ortografia ##############################
		#self.Insert(char)
		try:
			ochar=ord(char)
			print ochar
			if ochar in (B_DOWN_ARROW,B_UP_ARROW,B_TAB,B_PAGE_UP,B_PAGE_DOWN):
				self.superself.sem.acquire()
				value=self.superself.modifier#self.superself.modifier #CTRL pressed
				self.superself.sem.release()
				
				kmesg=BMessage(130550)
				if ochar == B_DOWN_ARROW:
					if value:
						# one element down
						kmesg.AddInt8('movekind',0)
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
						if self.tosave:
							bckpmsg=BMessage(17893)
							bckpmsg.AddString('bckppath',self.superself.backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
				elif ochar == B_UP_ARROW:
					if value:
						# one element up
						kmesg.AddInt8('movekind',1)
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
						if self.tosave:
							bckpmsg=BMessage(17893)
							bckpmsg.AddString('bckppath',self.superself.backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
				elif ochar == B_PAGE_UP:
					if value:
						# one page up
						kmesg.AddInt8('movekind',2)
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
						if self.tosave:
							bckpmsg=BMessage(17893)
							bckpmsg.AddString('bckppath',self.superself.backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
				elif ochar == B_PAGE_DOWN:
					if value:
						# one page down
						kmesg.AddInt8('movekind',3)
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
						print "seleziono una pagina in giù"
						if self.tosave:
							bckpmsg=BMessage(17893)
							bckpmsg.AddString('bckppath',self.superself.backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
				elif ochar == B_TAB:
					if not value:
						# next string needing work
						kmesg.AddInt8('movekind',4)
						BApplication.be_app.WindowAt(0).PostMessage(kmesg)
						if self.tosave:
							bckpmsg=BMessage(17893)
							bckpmsg.AddString('bckppath',self.superself.backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
				elif ochar == 103 or ochar == 7:
					if value:
						BApplication.be_app.WindowAt(0).PostMessage(BMessage(71))
				if ochar != B_TAB: # needed to pass up/down keys to textview
					return BTextView.KeyDown(self,char,bytes)
			elif ochar == B_ESCAPE: ######################## Restore to the saved string #####################
				self.SetText(self.oldtext)
				self.tosave=False
				return
			else:
				if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
					self.tosave=True  #### This says you should save the string before proceeding
					return BTextView.KeyDown(self,char,bytes)
		except:
			if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
				self.tosave=True   #### This says you should save the string before proceeding
				return BTextView.KeyDown(self,char,bytes)
		
	def SetPOReadText(self,text):
		self.oldtext=text
		self.oldtextloaded=True
		self.SetText(text)
		self.tosave=False
		
class srctabbox(BBox):
	def __init__(self,playground1,name,altece):
		self.name = name
#		print playground1
#		print (0,0,playground1[3]-playground1[1],playground1[3]-playground1[0])
		#(0,0,playground1[3]-playground1[1],playground1[3]-playground1[0])
		#newplayground=(playground1[0],playground1[1],playground1[2]-5,playground1[3]-5)
		BBox.__init__(self,(0,0,playground1[2]-playground1[0],playground1[3]-playground1[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)#frame
		self.hsrc = playground1[3] - playground1[1] - altece 
		self.src = BTextView((playground1[0],playground1[1],playground1[2]-playground1[0],playground1[3]-playground1[1]),name+'_source_BTextView',(5.0,5.0,playground1[2]-5,playground1[3]-5),B_FOLLOW_ALL,B_WILL_DRAW|B_FRAME_EVENTS)#B_FOLLOW_BOTTOM | B_FOLLOW_LEFT_RIGHT
		self.src.MakeEditable(False)
		self.AddChild(self.src)
class trnsltabbox(BBox):
	def __init__(self,playground2,name,altece,superself):
		self.name = name
#		print playground1
#		print (0,0,playground1[3]-playground1[1],playground1[3]-playground1[0])
		#print playground2
		#(0,0,playground2[3]-playground2[1],playground2[3]-playground2[0])
		BBox.__init__(self,(0,0,playground2[2]-playground2[0],playground2[3]-playground2[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)#frame
		#self.htrans= playground2[3] - playground2[1] - altece
		#newplayground2 = (playground2[0]+1,playground2[1]+1,playground2[2]-2,playground2[3]-2)
		self.trnsl = EventTextView(superself,(playground2[0],playground2[1],playground2[2]-playground2[0],playground2[3]-playground2[1]),name+'_translation_BTextView',(5.0,5.0,playground2[2]-5,playground2[3]-5),B_FOLLOW_ALL,B_WILL_DRAW|B_FRAME_EVENTS)#B_FOLLOW_BOTTOM | B_FOLLOW_LEFT_RIGHT
		self.trnsl.MakeEditable(True)
		self.AddChild(self.trnsl)

class POEditorBBox(BBox):
	def __init__(self,frame,name,percors,pofileloaded,arrayview,encoding):
		self.pofile = pofileloaded
		self.name = name
		#self.modifier=False      #perchè sta qui questo?
		self.encoding=encoding
		filen, file_ext = os.path.splitext(percors)
#		if file_ext=='.po':
#			self.typefile=0
#		elif file_ext=='.mo':
#			self.typefile=1
#		elif file_ext=='.gmo':
#			self.typefile=2
#		elif file_ext=='.pot':
#			
		self.backupfile= filen+".temp"+file_ext
		ind=0
		datab=[]
		for entry in self.pofile:
				datab.append((ind,entry.msgid,entry.msgstr))
				ind=ind+1
		
		contor = frame
		a,s,d,f = contor
		BBox.__init__(self,(a,s,d-5,f-35),name,B_FOLLOW_ALL,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)#frame
		contor=self.Bounds()
		l, t, r, b = contor
		self.list = ScrollView((5, 5, r -22, b-5), name+'_ScrollView')#-247
		self.AddChild(self.list.topview())
		self.scrollb = BScrollBar((r -21,5,r-5,b-5),name+'_ScrollBar',self.list.listview(),0.0,float(len(datab)),B_VERTICAL)#-247
		self.AddChild(self.scrollb)
		

#		playground1 = (5,b-243,r -5, b-123)
#		self.srctabview = BTabView(playground1, 'sourcetabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS)
##		tabfr = (5.0, 5.0, d*3/4-5, s-5)#(10.0, 10.0, d-25, s - 5 - altece)
#		tabfr = self.srctabview.Bounds()
##		print tabfr
#		#tabrc = (1.0,1.0, tabfr[2]-2,tabfr[3]-2)
##		print tabrc #playground1[2] - playground1[0], playground1[3] - playground1[1])
#		altece = self.srctabview.TabHeight()
#		tabrc = (3.0, 3.0, playground1[2] - playground1[0], playground1[3] - playground1[1]-altece)
#		self.srctablabels=[]
#		self.listemsgid=[]
#		self.AddChild(self.srctabview)
#		
#		self.sourcebox=srctabbox(tabrc,'msgid',altece)
##		self.AddChild(self.source)
#		self.listemsgid.append(self.sourcebox)
#		self.srctablabels.append(BTab())
#		self.srctabview.AddTab(self.listemsgid[0], self.srctablabels[0])
#		self.source = self.listemsgid[0].src
######################################################################################################
#		
#		playground2 = (5, b-120,r -5, b-5)
#		self.transtabview = translationtabview(playground2, 'translationtabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS)#BTabView(playground2, 'translationtabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT)
#
#		tabrc = (3, 3, playground2[2] - playground2[0], playground2[3] - playground2[1]-altece)
#		self.transtablabels=[]
#		self.listemsgstr=[]
#		self.AddChild(self.transtabview)
##		
##		self.htrans= playground2[3] - playground2[1] - altece
##		self.trnsl = EventTextView(self,playground2,name+'_translation_BTextView',(5.0,5.0,playground2[2]-2,playground2[3]-2),B_FOLLOW_BOTTOM | B_FOLLOW_LEFT_RIGHT,B_WILL_DRAW|B_FRAME_EVENTS)
##		self.trnsl.MakeEditable(True)
#		self.transbox=trnsltabbox(tabrc,'msgstr',altece,self)
#		self.listemsgstr.append(self.transbox)
#		self.transtablabels.append(BTab())
#		self.transtabview.AddTab(self.listemsgstr[0], self.transtablabels[0])
#		self.translation = self.listemsgstr[0].trnsl
#		#self.AddChild(self.translation)
		
		if arrayview[0]:
			for entry in self.pofile.fuzzy_entries():
				if entry and entry.msgid_plural:
#					print (entry.msgid + " has plural")
					item = MsgStrItem(entry.msgid,2,encoding,True)
				else:
					item = MsgStrItem(entry.msgid,2,encoding,False)
				self.list.lv.AddItem(item)
		if arrayview[1]:
			for entry in self.pofile.untranslated_entries():
				if entry and entry.msgid_plural:
#					print (entry.msgid + " has plural")
					item = MsgStrItem(entry.msgid,0,encoding,True)
				else:
					item = MsgStrItem(entry.msgid,0,encoding,False)
				self.list.lv.AddItem(item)
		if arrayview[2]:
			for entry in self.pofile.translated_entries():
				if entry and entry.msgid_plural:
#					print "len msgstrplural",len(sorted(entry.msgstr_plural.keys()))
#					print (entry.msgid + " has plural")
					item = MsgStrItem(entry.msgid,1,encoding,True)
				else:

					item = MsgStrItem(entry.msgid,1,encoding,False)
				self.list.lv.AddItem(item)
		if arrayview[3]:
			for entry in self.pofile.obsolete():
				if entry and entry.msgid_plural:
#					print (entry.msgid + " has plural")
					item = MsgStrItem(entry.msgid,3,encoding,True)
				else:
					item = MsgStrItem(entry.msgid,3,encoding,False)
				self.list.lv.AddItem(item)

class translationtabview(BTabView):
	def __init__(self,frame,name,width,risizingMode,flags):
		BTabView.__init__(self,frame,name,width,risizingMode,flags)
	def Draw(self,updateRect):
		BTabView.Draw(self,updateRect)
#	def DrawBox(self,selTabRect):
#		return BTabView.DrawBox(self,selTabRect)
#	def DrawTabs(self): #non esiste!!!
#		return BTabView.DrawTabs(self)
	def MouseDown(self,point):
		#BApplication.be_app.PostMessage(BMessage(B_WINDOW_RESIZED))
		print self.TabFrame(self.Selection())
		print "ho mandato il messaggio"
		return BTabView.MouseDown(self,point)

class PoWindow(BWindow):
	Menus = (
		('File', ((295485, 'Open'), (2, 'Save'), (1, 'Close'), (5, 'Save as...'),(None, None),(B_QUIT_REQUESTED, 'Quit'))),
		('Translation', ((3, 'Copy from source'), (4,'Edit comment'), (70,'Done and next'), (71,'Mark/Unmark fuzzy'), (72, 'Previous'),(73,'Next'),(None, None), (6, 'Find'), (7, 'Replace'))),
		('View', ((74,'Fuzzy'), (75, 'Untranslated'),(76,'Translated'),(77, 'Obsolete'))),
		('Settings', ((41, 'User settings'), (42, 'Po properties')	)),
		('About', ((3, 'Help'),(None, None),(4, 'About')))
		)
	def __init__(self, frame):
		selectionmenu=0
		BWindow.__init__(self, frame, 'Simple PO editor for Haiku!', B_TITLED_WINDOW,0)#, B_WILL_DRAW
		bounds = self.Bounds()
		self.bar = BMenuBar(bounds, 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		self.modifier=False
		self.poview=[True,True,True,False]
		self.sem = threading.Semaphore()
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
				Config.set('Settings','modifierkey',4132)
				Config.write(cfgfile)
				cfgfile.close()
				self.modifiervalue=4132 #1058 ALT;4132 CTRL
		except (ConfigParser.NoOptionError):
				cfgfile = open(confile,'w')
				Config.set('Settings','modifierkey',4132)
				Config.write(cfgfile)
				cfgfile.close()
				self.modifiervalue=4132 #1058 ALT;4132 CTRL
		
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
		##### COLOR GRAY UNDER LISTS

		self.background = BBox((l, t + barheight, r, b), 'background', B_FOLLOW_ALL,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.background)
		binds = self.background.Bounds()
		
		c,p,d,s = binds
		###### SAVE PANEL
		self.fp=BFilePanel(B_SAVE_PANEL)
		self.fp.SetPanelDirectory("/boot/home/Desktop")
		self.fp.SetSaveText("lavôr.po")
		###### OPEN PANEL
		#entryfilter= BEntry.BEntry(".po",True)
#		node=BNode(".po")
#		if (node.InitCheck() != B_OK):
#			print "node not inizialized"
#		else:
#			print "node initialized"
		self.ofp=BFilePanel()
		self.lubox=BBox((d*3/4,2,d,s), 'leftunderbox', B_FOLLOW_TOP_BOTTOM|B_FOLLOW_RIGHT, B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS|B_NAVIGABLE,B_FANCY_BORDER)# B_NO_BORDER)B_FOLLOW_ALL_SIDES // B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM|B_FOLLOW_TOP//B_FOLLOW_TOP|B_FOLLOW_RIGHT
		self.background.AddChild(self.lubox)
		self.postabview = BTabView((5.0, 5.0, d*3/4-5, b-barheight-245), 'postabview',B_WIDTH_FROM_LABEL)#,B_WIDTH_FROM_LABEL,B_FOLLOW_ALL,B_NAVIGABLE) s-5 o b-260 circa
		#print(5.0, 5.0, d*3/4-5, s-5)
		altece = self.postabview.TabHeight()
		tfr = (5.0, 5.0, d*3/4-5, s-5)#(10.0, 10.0, d-25, s - 5 - altece)
		self.trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])

		self.tabslabels=[]
		self.editorslist=[]
		
		self.background.AddChild(self.postabview)
		
		
		
		
		playground1 = (5,b-268,r - d*1/4-5, s-120)
		self.srctabview = BTabView(playground1, 'sourcetabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS)
#		tabfr = (5.0, 5.0, d*3/4-5, s-5)#(10.0, 10.0, d-25, s - 5 - altece)
#		tabfr = self.srctabview.Bounds()
#		print tabfr
		#tabrc = (1.0,1.0, tabfr[2]-2,tabfr[3]-2)
#		print tabrc #playground1[2] - playground1[0], playground1[3] - playground1[1])
		altece = self.srctabview.TabHeight()
		tabrc = (3.0, 3.0, playground1[2] - playground1[0], playground1[3] - playground1[1]-altece)
		self.srctablabels=[]
		self.listemsgid=[]
		self.background.AddChild(self.srctabview)
		
		self.sourcebox=srctabbox(tabrc,'msgid',altece)
#		self.AddChild(self.source)
		self.listemsgid.append(self.sourcebox)
		self.srctablabels.append(BTab())
		self.srctabview.AddTab(self.listemsgid[0], self.srctablabels[0])
		############################################################################################################### ELIMINARE SELF.SOURCE ###########################################################################################################
		self.source = self.listemsgid[0].src
######################################################################################################
		
		playground2 = (5, b-142,r -d*1/4-5, s-2)
		self.transtabview = translationtabview(playground2, 'translationtabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS)#BTabView(playground2, 'translationtabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT)

		tabrc = (3, 3, playground2[2] - playground2[0], playground2[3] - playground2[1]-altece)
		print tabrc,"original tabrc"
		self.transtablabels=[]
		self.listemsgstr=[]
		self.background.AddChild(self.transtabview)
#		
#		self.htrans= playground2[3] - playground2[1] - altece
#		self.trnsl = EventTextView(self,playground2,name+'_translation_BTextView',(5.0,5.0,playground2[2]-2,playground2[3]-2),B_FOLLOW_BOTTOM | B_FOLLOW_LEFT_RIGHT,B_WILL_DRAW|B_FRAME_EVENTS)
#		self.trnsl.MakeEditable(True)
		self.transbox=trnsltabbox(tabrc,'msgstr',altece,self)
		self.listemsgstr.append(self.transbox)
		self.transtablabels.append(BTab())
		self.transtabview.AddTab(self.listemsgstr[0], self.transtablabels[0])
		#################################################################################################################### ELIMINARE SELF.TRANSLATION ############################################################################################
		self.translation = self.listemsgstr[0].trnsl
		#self.AddChild(self.translation)
		
		
		

		
		##### if first launch, it opens the profile creator wizard and sets default enconding for polib
		if  firstrun:
			self.setencoding = False
			BApplication.be_app.WindowAt(0).PostMessage(305)
		else:
			try:
				Config.read(confile)
				self.setencoding=Config.getboolean('Settings', 'customenc')
				if self.setencoding:
					try:
						self.encoding = ConfigSectionMap("Settings")['encoding']
					except (ConfigParser.NoSectionError):
						print ("custom encoding method specified but no encoding indicated")
						self.setencoding = False
			except (ConfigParser.NoSectionError):
				print "ops! no Settings section for custom encoding"
				self.setencoding = False
			except (ConfigParser.NoOptionError):
				self.setencoding = False
			
	def FrameResized(self,x,y):
			i=self.postabview.Selection()
			h,j,k,l = self.editorslist[i].Bounds()
			zx,xc,cv,vb = self.editorslist[i].scrollb.Bounds()
			for b in self.editorslist:
				if b == self.editorslist[i]:
					pass
					#######################  do you need this?
#					z,x,c,v=b.list.sv.Bounds()
#					b.list.sv.ResizeTo(c,v)
#					b.list.lv.ResizeTo(c-20,v-20) #invece di numero fisso mettere larghezza scrollbars B_H_SCROLL_BAR_WIDTH B_V_SCROLL_BAR_WIDTH
#					u,m,o,y= b.source.Bounds()
#					boundos = (5.0, 5.0, (o - 5.0), (y-5.0))
#					b.source.SetTextRect(boundos)
#					u,m,o,y= b.translation.Bounds()
#					boundos = (5.0, 5.0, (o - 5.0), (y-5.0))
#					b.translation.SetTextRect(boundos)
				else:
					b.ResizeTo(k,l)
					print(self.editorslist[i].list.sv.Bounds())
					b.list.lv.ResizeTo(k-27,l-10)#-252
					b.list.sv.ResizeTo(k-23,l-6)#-248
					print b.list.sv.Bounds()
					b.scrollb.MoveTo(k-21,5)
					b.scrollb.ResizeTo(cv-zx,l-10) #-252########### No 16! This should be B_V_SCROLL_BAR_WIDTH
#					b.srctabview.MoveTo(5,l-243)
#					b.srctabview.ResizeTo(k-10,120)
#					#if len(b.listemsgid)>0:
#					#	for schedis in b.listemsgstr:
#					a,s,d,f = b.srctabview.Bounds()
#					print ("POBox: ",self.editorslist[i].Bounds())
#					print ("srctabview: ",b.srctabview.Bounds())
#					for schedis in b.listemsgid:
#						schedis.ResizeTo(d-5,f-33)
#						print ("box: ",schedis.Bounds())
#						schedis.src.ResizeTo(d-5,87)
#						print ("text box: ",schedis.src.Bounds())
#						schedis.src.SetTextRect((5,5,d-5,87))
#						print ("text rect: ", schedis.src.TextRect())
#						
##		self.listemsgstr.append(self.transbox)
##		self.transtablabels.append(BTab())
##		self.transtabview.AddTab(self.listemsgstr[0], self.transtablabels[0])
#
#					b.transtabview.MoveTo(5,l-120)
#					b.transtabview.ResizeTo(k-10,115)
#					a,s,d,f = b.transtabview.Bounds()
#					print ("POBox: ",self.editorslist[i].Bounds())
#					print ("transtabview: ",b.transtabview.Bounds())
##					i=len(b.listemsgstr)-1
##					while i>-1:
##						b.transtabview.RemoveTab(i)
##						i=i-1
##					i=len(b.listemsgstr)-1
##					p=0
##					while p<=i:
###						b.transtabview.AddTab(b.listemsgstr[p],b.transtablabels[p])
##						print "ho aggiunto", p
##						p=p+1
#					for schedis in b.listemsgstr:
#						schedis.ResizeTo(d-5,f-33)
##						print ("box: ",schedis.Bounds())
#						schedis.trnsl.MoveTo(0,0)
#						schedis.trnsl.ResizeTo(d-10,87)
##						print ("text box: ",schedis.trnsl.Bounds())
#						schedis.trnsl.SetTextRect((5,5,d-5,87))
##						print ("text rect: ", schedis.trnsl.TextRect())
					
			#return BWindow.FrameResized(self,x,y)


	def MessageReceived(self, msg):
	#B_UNMAPPED_KEY_DOWN
		if msg.what == B_MODIFIERS_CHANGED: #quando modificatore ctrl cambia stato
#			print "modifiers changed"
			value=msg.FindInt32("modifiers")
			self.sem.acquire()
			if value==self.modifiervalue or value==self.modifiervalue+8:
				self.modifier=True
			else:
				self.modifier=False
			self.sem.release()
			return
		elif msg.what == B_KEY_DOWN:	#on tab key pressed, focus on translation or translation of first item list of translations
			if msg.FindInt32('key')==38:
				run=True
				try:
					lung=len(self.listemsgstr)-1
					pp=0
					while lung>=pp:
						if self.listemsgstr[pp].trnsl.IsFocus():
							run=False
						pp=pp+1
					if run:
						if self.postabview.Selection()>-1:
							self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus()
						else:
							self.editorslist[self.postabview.Selection()].list.lv.Select(0)
				except:
					pass
			return

		elif msg.what == 295485:
			self.ofp.Show()
			return
		elif msg.what == 4:
			#ABOUT
			self.About = AboutWindow()
			self.About.Show()
			return
		
		elif msg.what == 41:
			#USER SETTINGS
			self.usersettings = ImpostazionsUtent()
			self.usersettings.Show()
			self.SetFlags(B_AVOID_FOCUS)
			return
		
		elif msg.what == 74:
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
				b.list.reload(self.poview,b.pofile,self.encoding)
			msg = BMessage(460551) 								#clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return
					
		elif msg.what == 75:
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
				b.list.reload(self.poview,b.pofile,self.encoding)
			msg = BMessage(460551)								#clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return

		elif msg.what == 76:
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
				b.list.reload(self.poview,b.pofile,self.encoding)
			msg = BMessage(460551)								#clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return
		
		elif msg.what == 77:
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
				b.list.reload(self.poview,b.pofile,self.encoding)
			msg = BMessage(460551)								#clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return

		elif msg.what == 130550: # change listview selection
			movetype=msg.FindInt8('movekind')
			if movetype == 0:
				#select one down
				if (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1) and (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()<self.editorslist[self.postabview.Selection()].list.lv.CountItems()):
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()+1)
					self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
			elif movetype == 1:
				#select one up
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>0 :
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()-1)
					self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
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
					
			elif  movetype == 4:
				#select next untranslated (or needing work) string
				next=True
				if (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1):
					spice = self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()
				else:
					self.editorslist[self.postabview.Selection()].list.lv.Select(0)
					spice=-1
				while next:
					if (spice+1)==self.editorslist[self.postabview.Selection()].list.lv.CountItems():
						spice=0
						state=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(0).state
						if state == 0 or state == 2:
							self.editorslist[self.postabview.Selection()].list.lv.Select(0)
							next=False
					else:
						state=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(spice+1).state
						if state == 0 or state == 2:
							self.editorslist[self.postabview.Selection()].list.lv.Select(spice+1)
							next=False
					spice=spice+1
				self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
			return

		elif msg.what == 305:
			#USER CREATOR WIZARD
			self.maacutent = MaacUtent(True)
			self.maacutent.Show()
			self.SetFlags(B_AVOID_FOCUS)
			return
			
		elif msg.what == 17893:
			bckppath = msg.FindString('bckppath')
			self.editorslist[self.postabview.Selection()].pofile.save(bckppath)
			print "salvo backup"
			return
			
		elif msg.what == 445380:
			#open procedure
			txtpath=msg.FindString("path")
			mimesuptbool = False
			mimesubtbool = False
			extbool = False
			mimeinstalled=False
			if True:
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
					if self.setencoding:
						try:
							self.pof = polib.pofile(txtpath,encoding=self.encoding)
							if mimeinstalled:
								say = BAlert('oops', "The file is ok, but there's no gettext mimetype installed in your system", 'Ok',None, None, None, 3)
								say.Go()
								tfr = self.postabview.Bounds()
								trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])
							self.loadPOfile(txtpath,trc,self.pof)
						except:
							test = compiletest(mimesuptbool,mimesubtbool,extbool)
							say = BAlert('oops', 'Failed to load: '+test, 'Ok',None, None, None, 3)
							say.Go()
					else:
						# reinsert commented lines
						#try:
							self.encoding="utf-8"
							self.pof = polib.pofile(txtpath,encoding=self.encoding)
							if mimeinstalled:
								say = BAlert('oops', "The file is ok, but there's no gettext mimetype installed in your system", 'Ok',None, None, None, 3)
								say.Go()
							tfr = self.postabview.Bounds()
							trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])
							self.loadPOfile(txtpath,trc,self.pof)
						#except:
						#	test = compiletest(mimesuptbool,mimesubtbool,extbool)
						#	say = BAlert('oops', 'Failed to load: '+test, 'Ok',None, None, None, 3)
						#	say.Go()
	
			#except:
			#	e = None
			#if e is None:
			#		pass
			return
			
		elif msg.what == 71:
			# mark unmark as fuzzy
			if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
				txttosearch=self.editorslist[self.postabview.Selection()].list.SelectedText()
				for entry in self.editorslist[self.postabview.Selection()].pofile:
					if entry.msgid.encode(self.encoding) == txttosearch:
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						else:
							entry.flags.append('fuzzy')
						bckpmsg=BMessage(17893)
						bckpmsg.AddString('bckppath',self.editorslist[self.postabview.Selection()].backupfile)
						BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save to backup file
						break
				self.editorslist[self.postabview.Selection()].list.reload(self.poview,self.editorslist[self.postabview.Selection()].pofile,self.encoding)
							
		elif msg.what == 460550:
			# selection from listview
			if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
				bounds = self.Bounds()
				l, t, r, b = bounds
				binds = self.background.Bounds()
				c,p,d,s = binds
				plygrnd1 = (5,b-268,r - d*1/4-5, s-120)
				altece = self.srctabview.TabHeight()
				tabrc = (3.0, 3.0, plygrnd1[2] - plygrnd1[0], plygrnd1[3] - plygrnd1[1]-altece)
				txttosearch=self.editorslist[self.postabview.Selection()].list.SelectedText()
				#entry = self.editorslist[self.postabview.Selection()].pofile.find(txttosearch)
				
				
				####### check for multiple occurencies ########
				count=0
				for entry in self.editorslist[self.postabview.Selection()].pofile:
					if entry.msgid.encode(self.encoding) == txttosearch:
						count = count +1
				if count > 1:
					print "multiple entries occurrencies function not implemented"
					
					
				for entry in self.editorslist[self.postabview.Selection()].pofile:
					if entry.msgid.encode(self.encoding) == txttosearch:
						alfa = (len(self.listemsgid)-1)
						if entry and not entry.msgid_plural:
							if alfa == 1:    #IF THERE'S A PLURAL, REMOVE IT
									self.srctabview.RemoveTab(1)
									self.listemsgid.pop(1)
									self.srctablabels.pop(1)
									self.srctabview.Hide()
									self.srctabview.Show()
							ww=len(self.listemsgstr)-1
							while ww>0:					#removes plural translation tabs
								self.transtabview.RemoveTab(ww)
								self.listemsgstr.pop(ww)
								self.transtablabels.pop(ww)
								self.transtabview.Hide()
								self.transtabview.Show()
								ww=ww-1
##### Removing tab 0 on translation tabview and renaming it as msgstr
							self.transtabview.RemoveTab(0)
							self.listemsgstr.pop(0)
							self.transtablabels.pop(0)
							self.transtabview.Hide()
							self.transtabview.Show()
							tabrc=(3,3,self.listemsgid[0].Bounds()[2],tabrc[3]-10)
							self.listemsgstr.append(trnsltabbox(tabrc,'msgstr',altece,self))
							self.transtablabels.append(BTab())
							self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
							self.transtabview.Hide()
							self.transtabview.Show()
#######################################################################
							self.listemsgid[0].src.SetText(entry.msgid.encode(self.encoding))
							self.listemsgstr[0].trnsl.SetPOReadText(entry.msgstr.encode(self.encoding))
############################### bugfix workaround? ####################
							self.transtabview.SetFocusTab(1,True)						#################  <----- needed to fix 
							self.transtabview.Select(1)									#################  <----- a bug, tab0 will not appear
							self.transtabview.Select(0)									#################  <----- so forcing a tabview update
#######################################################################
						if entry and entry.msgid_plural:
							beta=len(sorted(entry.msgstr_plural.keys()))
							tabrc=(3,3,self.listemsgid[0].Bounds()[2],tabrc[3]-10)
							if alfa ==1: 	#IF THERE'S A PLURAL, REMOVE IT
									self.srctabview.RemoveTab(1)
									self.listemsgid.pop(1)
									self.srctablabels.pop(1)
									self.srctabview.Hide()
									self.srctabview.Show()
							ww=len(self.listemsgstr)-1
							while ww>0: 				#removes plural translation tabs
								self.transtabview.RemoveTab(ww)
								self.listemsgstr.pop(ww)
								self.transtablabels.pop(ww)
								self.transtabview.Hide()
								self.transtabview.Show()
								ww=ww-1

							self.transtabview.RemoveTab(0)
							self.listemsgstr.pop(0)
							self.transtablabels.pop(0)
							self.transtabview.Hide()
							self.transtabview.Show()

							self.listemsgstr.append(trnsltabbox(tabrc,'msgstr[0]',altece,self))
							self.transtablabels.append(BTab())
							self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
							self.transtabview.Hide()
							self.transtabview.Show()
							self.listemsgid.append(srctabbox((3,3,self.listemsgid[0].Bounds()[2]+3,self.listemsgid[0].Bounds()[3]+3),'msgid_plural',altece))
							self.srctablabels.append(BTab())
							self.srctabview.AddTab(self.listemsgid[1], self.srctablabels[1])
							x=len(self.listemsgid)-1
							self.srctabview.SetFocusTab(x,True)
							self.srctabview.Select(x)
							self.srctabview.Select(0)
							self.listemsgid[0].src.SetText(entry.msgid.encode(self.encoding))
							self.listemsgid[1].src.SetText(entry.msgid_plural.encode(self.encoding))
							ww=0
							while ww<beta:
								self.transtablabels.append(BTab())
								if ww == 0:
									self.listemsgstr[0].trnsl.SetPOReadText(entry.msgstr_plural[0].encode(self.encoding))
									self.transtabview.SetFocusTab(x,True)
									self.transtabview.Select(x)
									self.transtabview.Select(0)
								else:
									asd=self.listemsgstr[0].trnsl.Bounds()
									tabrect=(3,3,asd[2]+6,asd[3]+6)
									self.listemsgstr.append(trnsltabbox(tabrect,'msgstr['+str(ww)+']',altece,self))
									self.listemsgstr[ww].trnsl.SetPOReadText(entry.msgstr_plural[ww].encode(self.encoding))
									self.transtabview.AddTab(self.listemsgstr[ww],self.transtablabels[ww])
								ww=ww+1
							 
					self.listemsgstr[0].trnsl.MakeFocus()
				
				############################ TODO: GO TO THE END OF THE TEXT #############################
				#num=self.editorslist[self.postabview.Selection()].translation.CountLines()
				#self.editorslist[self.postabview.Selection()].translation.GoToLine(num)
				#txtlen=self.editorslist[self.postabview.Selection()].translation.TextLenght()
#				pointer=self.editorslist[self.postabview.Selection()].translation.PointAt(len(self.editorslist[self.postabview.Selection()].translation.Text()))
#				print pointer[0]
#				self.editorslist[self.postabview.Selection()].translation.MovePenTo(pointer[0][0],pointer[0][1])
#				print self.editorslist[self.postabview.Selection()].translation.PenLocation()
				
			else:
			################################################## fix this ###########################################################################################################################################################
				self.editorslist[self.postabview.Selection()].source.SetText("")
				self.editorslist[self.postabview.Selection()].translation.SetPOReadText("")
#				self.editorslist[self.postabview.Selection()].translation.tosave=False
			return
				
		elif msg.what == 460551:
		################################################## fix this ###########################################################################################################################################################
			#### clears source textview text and translation specific textview parameters
			for v in self.editorslist:
				v.source.SetText("")
				v.translation.SetText("")
				v.translation.oldtext=""
				v.translation.oldtextloaded=False
				v.translation.tosave=False
			return

		elif msg.what ==  777:
			#Removing B_AVOID_FOCUS flag
			self.SetFlags(0)
			return
		else:
			BWindow.MessageReceived(self, msg)
			
	def  loadPOfile(self,pathtofile,bounds,pofile):
			########################## TODO ####################################
			##### check if .name.temp.po file exists and is more recent than name.po
			##### check for po compliance with user lang
			
			##### add a tab in the editor's tabview
			head, tail = os.path.split(pathtofile)
			##update self.poview
			self.editorslist.append(POEditorBBox(bounds,tail,pathtofile,pofile,self.poview,self.encoding))
			self.tabslabels.append(BTab())
			x=len(self.editorslist)-1
			self.postabview.AddTab(self.editorslist[x], self.tabslabels[x])
			self.postabview.SetFocusTab(x,True)
			self.postabview.Select(x)
			
	def QuitRequested(self):
		print "So long and thanks for all the fish"
		BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
		return 1

class HaiPOApp(BApplication.BApplication):

	def __init__(self):
		BApplication.BApplication.__init__(self, "application/x-vnd.HaiPO-Editor")


	def ReadyToRun(self):
		window((100,80,800,600))
		if len(sys.argv) > 1:
			try:
				for item in sys.argv:
					if item == sys.argv[0]:
						pass
					else:
						percors = item
						self.elaborate_path(os.path.abspath(percors))
			except:
				pass
		
	def RefsReceived(self, msg):
		#msg.PrintToStream()
		if msg.what == B_REFS_RECEIVED:
			i = 0
			while 1:
				try:
					e = msg.FindRef("refs", i)
					entryref = BEntry(e,True)
					percors = entryref.GetPath()
					self.txtpath= percors.Path()
					self.elaborate_path(self.txtpath)
				except:
					e = None
				if e is None:
					break
				i = i + 1

	def elaborate_path(self,percors):
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

HaiPO = HaiPOApp()
HaiPO.Run()
