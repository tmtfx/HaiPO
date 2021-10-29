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
	from AppKit import B_QUIT_REQUESTED,B_KEY_UP,B_KEY_DOWN,B_MODIFIERS_CHANGED,B_UNMAPPED_KEY_DOWN,B_REFS_RECEIVED,B_SAVE_REQUESTED,B_CANCEL
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
	HiWhat = 32 #Doppioclick --> set as fuzzy
	Selmsgstr = 460550
#	SelezioneNotizia = 102

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
					item = MsgStrItem(entry.msgid,2,encoding)
					self.lv.AddItem(item)
			if arrayview[1]:
				for entry in pofile.untranslated_entries():
					item = MsgStrItem(entry.msgid,0,encoding)
					self.lv.AddItem(item)
			if arrayview[2]:
				for entry in pofile.translated_entries():
					item = MsgStrItem(entry.msgid,1,encoding)
					self.lv.AddItem(item)
			if arrayview[3]:
				for entry in pofile.obsolete():
					item = MsgStrItem(entry.msgid,3,encoding)
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

	def __init__(self, text,state,encoding):
		self.text = text.encode(encoding)  #it's in english should this be always utf-8
		self.state=state
		BListItem.__init__(self)

	def DrawItem(self, owner, frame,complete):
		if self.IsSelected() or complete:
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
		owner.SetHighColor(self.color)
		#if self.color == (200,0,0,0):
		#	self.font = be_bold_font
		#	owner.SetFont(self.font)
		#else:	
		#	self.font = be_plain_font
		#	owner.SetFont(self.font)
		owner.MovePenTo(frame[0],frame[3]-2)
		owner.DrawString(self.text)
		owner.SetLowColor((255,255,255,255))

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
		ochar=ord(char)
		if ochar in (B_DOWN_ARROW,B_UP_ARROW,B_TAB,B_PAGE_UP,B_PAGE_DOWN):
			self.superself.sem.acquire()
			value=self.superself.modifier #CTRL pressed
			self.superself.sem.release()
			kmesg=BMessage(130550)
			if ochar == B_DOWN_ARROW:
				if value:
					print "seleziono un elemento in giù"
					kmesg.AddInt8('movekind',0)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
			elif ochar == B_UP_ARROW:
				if value:
					print "seleziono un elemento in sù"
					kmesg.AddInt8('movekind',1)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
			elif ochar == B_PAGE_UP:
				if value:
					kmesg.AddInt8('movekind',2)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
					print "seleziono una pagina in sù"
			elif ochar == B_PAGE_DOWN:
				if value:
					kmesg.AddInt8('movekind',3)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
					print "seleziono una pagina in giù"
			if ochar == B_TAB:
				if not value:
					kmesg.AddInt8('movekind',4)
					BApplication.be_app.WindowAt(0).PostMessage(kmesg)
					print "passo al prossimo non tradotto oppure al sucessivo vedi tu"
			if ochar != B_TAB:
				return BTextView.KeyDown(self,char,bytes)
		elif ochar == B_ESCAPE: ######################## Restore to the saved string #####################
			#self.superself.list.lv.DeselectAll()
			#self.superself.source.SetText("")
			self.SetText(self.oldtext)
			#self.oldtext=""
			#self.oldtextloaded=False
			self.tosave=False
			return
		else:
			if self.superself.list.lv.CurrentSelection()>-1:
			#if self.superself.source.Text() != "":
				self.tosave=True  #### This says you should save the string before proceeding
				return BTextView.KeyDown(self,char,bytes)
		
	def SetPOReadText(self,text):
		self.oldtext=text
		self.oldtextloaded=True
		self.SetText(text)

class POEditorBBox(BBox):
	def __init__(self,frame,name,percors,pofileloaded,arrayview,encoding):
		self.pofile = pofileloaded
		self.modifier=False
		self.encoding=encoding
		ind=0
		datab=[]
		for entry in self.pofile:
				datab.append((ind,entry.msgid,entry.msgstr))
				ind=ind+1
		
		self.sem = threading.Semaphore()
		contor = frame
		a,s,d,f = contor
		BBox.__init__(self,(a,s,d-5,f-35),name,B_FOLLOW_ALL,B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)#frame
		contor=self.Bounds()
		l, t, r, b = contor
		self.list = ScrollView((5, 5, r -22, b-247), name+'_ScrollView')
		self.AddChild(self.list.topview())
		self.scrollb = BScrollBar((r -21,5,r-5,b-247),name+'_ScrollBar',self.list.listview(),0.0,float(len(datab)),B_VERTICAL)
		self.AddChild(self.scrollb)
		playground1 = (5,b-243,r -5, b-123)
		self.hsrc = playground1[3] - playground1[1]
		self.source = BTextView(playground1,name+'_source_BTextView',(5.0,5.0,playground1[2]-2,playground1[3]-2),B_FOLLOW_BOTTOM | B_FOLLOW_LEFT_RIGHT,B_WILL_DRAW|B_FRAME_EVENTS)
		self.source.MakeEditable(False)
		self.AddChild(self.source)
		playground2 = (5, b-120,r -5, b-5)
		self.htrans= playground2[3] - playground2[1]
		self.translation = EventTextView(self,playground2,name+'_translation_BTextView',(5.0,5.0,playground2[2]-2,playground2[3]-2),B_FOLLOW_BOTTOM | B_FOLLOW_LEFT_RIGHT,B_WILL_DRAW|B_FRAME_EVENTS)
		self.translation.MakeEditable(True)
		self.AddChild(self.translation)
		if arrayview[0]:
			for entry in self.pofile.fuzzy_entries():
				item = MsgStrItem(entry.msgid,2,encoding)
				self.list.lv.AddItem(item)
		if arrayview[1]:
			for entry in self.pofile.untranslated_entries():
				item = MsgStrItem(entry.msgid,0,encoding)
				self.list.lv.AddItem(item)
		if arrayview[2]:
			for entry in self.pofile.translated_entries():
				item = MsgStrItem(entry.msgid,1,encoding)
				self.list.lv.AddItem(item)
		if arrayview[3]:
			for entry in self.pofile.obsolete():
				item = MsgStrItem(entry.msgid,3,encoding)
				self.list.lv.AddItem(item)
#		else:
#			pass
	
#	def reloadlist(self,arrayview):
#		pass
		
#	def FrameResized(self,x,y):
#		z, w, c, v=self.Bounds()
##		self.ResizeTo(x,y)
#		self.list.topview().ResizeTo(x,v-self.hsrc-self.htrans-15)
		


class PoWindow(BWindow):
	Menus = (
		('File', ((295485, 'Open'), (2, 'Save'), (1, 'Close'), (5, 'Save as...'),(None, None),(B_QUIT_REQUESTED, 'Quit'))),
		('Translation', ((3, 'Copy from source'), (4,'Edit comment'), (70,'Done and next'), (71,'Mark as fuzzy'), (72, 'Previous'),(73,'Next'),(None, None), (6, 'Find'), (7, 'Replace'))),
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
		self.poview=[True,True,True,False]
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
		self.background = BBox((l, t + barheight, r, b), 'background', B_FOLLOW_ALL, B_WILL_DRAW|B_NAVIGABLE, B_NO_BORDER)
		self.AddChild(self.background)
		binds = self.background.Bounds()
		c,p,d,s = binds
		###### SAVE PANEL
		self.fp=BFilePanel(B_SAVE_PANEL) #BFilePanel.BFilePanel(B_SAVE_PANEL)
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
		self.lubox=BBox((d*3/4,2,d,s), 'leftunderbox', B_FOLLOW_TOP_BOTTOM|B_FOLLOW_RIGHT, B_WILL_DRAW|B_NAVIGABLE,B_FANCY_BORDER)# B_NO_BORDER)B_FOLLOW_ALL_SIDES // B_FOLLOW_RIGHT|B_FOLLOW_BOTTOM|B_FOLLOW_TOP//B_FOLLOW_TOP|B_FOLLOW_RIGHT
		self.background.AddChild(self.lubox)
		self.postabview = BTabView((5.0, 5.0, d*3/4-5, s-5), 'postabview',B_WIDTH_FROM_LABEL)#,B_WIDTH_FROM_LABEL,B_FOLLOW_ALL,B_NAVIGABLE)
		altece = self.postabview.TabHeight()
		tfr = (5.0, 5.0, d*3/4-5, s-5)#(10.0, 10.0, d-25, s - 5 - altece)
		self.trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])

		self.tabslabels=[]
		self.editorslist=[]
		
		self.background.AddChild(self.postabview)

		
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
					b.list.lv.ResizeTo(k-27,l-252)
					b.list.sv.ResizeTo(k-23,l-248)
					b.scrollb.MoveTo(k-21,5)
					b.scrollb.ResizeTo(cv-zx,l-252) ############ No 16! This should be B_V_SCROLL_BAR_WIDTH
					b.source.MoveTo(5,l-243)
					b.source.ResizeTo(k-10,120)
					u,m,o,y= b.source.Bounds()
					boundos = (5,5,o-5,y-5)
					b.source.SetTextRect(boundos)
					b.translation.MoveTo(5,l-120)
					b.translation.ResizeTo(k-10,115)
					u,m,o,y= b.translation.Bounds()
					boundos = (5.0, 5.0, (o - 5.0), (y-5.0))
					b.translation.SetTextRect(boundos)
		#BApplication.be_app.WindowAt(0).PostMessage(BMessage(130550))

	def MessageReceived(self, msg):
		if msg.what == B_MODIFIERS_CHANGED: #quando modificatore ctrl cambia stato
#			print "modifiers changed"
			value=msg.FindInt32("modifiers")
			print value
			self.editorslist[self.postabview.Selection()].sem.acquire()
			if value==self.modifiervalue or value==self.modifiervalue+8:
				self.editorslist[self.postabview.Selection()].modifier=True
			else:
				self.editorslist[self.postabview.Selection()].modifier=False
			self.editorslist[self.postabview.Selection()].sem.release()
			return
		if msg.what == B_KEY_DOWN:#Quando viene premuto il tasto tab
			if msg.FindInt32('key')==38:
				if not self.editorslist[self.postabview.Selection()].translation.IsFocus():
					print "mi focalizzo su lista"
					self.editorslist[self.postabview.Selection()].list.lv.MakeFocus()

		if msg.what == 295485:
			self.ofp.Show()
			return
		if msg.what == 4:
			#ABOUT
			self.About = AboutWindow()
			self.About.Show()
			return
		
		if msg.what == 41:
			#USER SETTINGS
			self.usersettings = ImpostazionsUtent()
			self.usersettings.Show()
			self.SetFlags(B_AVOID_FOCUS)
			return
		
		if msg.what == 74:
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
			msg = BMessage(460551) #clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return
					
		if msg.what == 75:
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
			msg = BMessage(460551) #clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return

		if msg.what == 76:
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
			msg = BMessage(460551) #clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return
		
		if msg.what == 77:
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
			msg = BMessage(460551) #clears TextViews
			BApplication.be_app.WindowAt(0).PostMessage(msg)
			return

		if msg.what == 130550: ################ unused for now
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
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.ItemFrame(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
				hitem=rectangular[3]-rectangular[1]
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.Bounds()
				hwhole=rectangular[3]-rectangular[1]
				page=int(hwhole//hitem)
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>(page-1) :
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()-page)
					self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
			elif movetype == 3:
				#select one page down
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.ItemFrame(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
				hitem=rectangular[3]-rectangular[1]
				rectangular=self.editorslist[self.postabview.Selection()].list.lv.Bounds()
				hwhole=rectangular[3]-rectangular[1]
				page=int(hwhole//hitem)
				if (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1) and (self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()<self.editorslist[self.postabview.Selection()].list.lv.CountItems()-page):
					self.editorslist[self.postabview.Selection()].list.lv.Select(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()+page)
					self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
			elif  movetype == 4:
				pass
#			i=self.postabview.Selection()
#			h,j,k,l = self.editorslist[i].Bounds()
#			for b in self.editorslist:
#				if b == self.editorslist[i]:
#					pass
#					#######################  do you need this?
##					z,x,c,v=b.list.sv.Bounds()
##					b.list.sv.ResizeTo(c,v)
##					b.list.lv.ResizeTo(c-20,v-20) #invece di numero fisso mettere larghezza scrollbars B_H_SCROLL_BAR_WIDTH B_V_SCROLL_BAR_WIDTH
##					u,m,o,y= b.source.Bounds()
##					boundos = (5.0, 5.0, (o - 5.0), (y-5.0))
##					b.source.SetTextRect(boundos)
##					u,m,o,y= b.translation.Bounds()
##					boundos = (5.0, 5.0, (o - 5.0), (y-5.0))
##					b.translation.SetTextRect(boundos)
#				else:
#					b.ResizeTo(k,l)
#					b.list.lv.ResizeTo(k-27,l-252)
#					b.list.sv.ResizeTo(k-23,l-248)
#					b.scrollb.MoveTo(k-21,5)
#					b.scrollb.ResizeTo(16,l-252) ############ No 16! This should be B_V_SCROLL_BAR_WIDTH
#					b.source.MoveTo(5,l-243)
#					b.source.ResizeTo(k-10,120)
#					u,m,o,y= b.source.Bounds()
#					boundos = (5,5,o-5,y-5)
#					b.source.SetTextRect(boundos)
#					b.translation.MoveTo(5,l-120)
#					b.translation.ResizeTo(k-10,115)
#					u,m,o,y= b.translation.Bounds()
#					boundos = (5.0, 5.0, (o - 5.0), (y-5.0))
#					b.translation.SetTextRect(boundos)
				
		if msg.what == 305:
			#USER CREATOR WIZARD
			self.maacutent = MaacUtent(True)
			self.maacutent.Show()
			self.SetFlags(B_AVOID_FOCUS)
			return
		
		if msg.what == 445380:
			#msg.PrintToStream()
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
			
		if msg.what == 460550:
			if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
				txttosearch=self.editorslist[self.postabview.Selection()].list.SelectedText()
				for entry in self.editorslist[self.postabview.Selection()].pofile:
					if entry.msgid.encode(self.encoding) == txttosearch:
						self.editorslist[self.postabview.Selection()].source.SetText(entry.msgid.encode(self.encoding))
						self.editorslist[self.postabview.Selection()].translation.SetPOReadText(entry.msgstr.encode(self.encoding))
				self.editorslist[self.postabview.Selection()].translation.MakeFocus()
				
				############################ TODO GO TO THE END OF THE TEXT #############################
				#num=self.editorslist[self.postabview.Selection()].translation.CountLines()
				#self.editorslist[self.postabview.Selection()].translation.GoToLine(num)
				#txtlen=self.editorslist[self.postabview.Selection()].translation.TextLenght()
#				pointer=self.editorslist[self.postabview.Selection()].translation.PointAt(len(self.editorslist[self.postabview.Selection()].translation.Text()))
#				print pointer[0]
#				self.editorslist[self.postabview.Selection()].translation.MovePenTo(pointer[0][0],pointer[0][1])
#				print self.editorslist[self.postabview.Selection()].translation.PenLocation()
				
			else:
				self.editorslist[self.postabview.Selection()].source.SetText("")
				self.editorslist[self.postabview.Selection()].translation.SetPOReadText("")
				
				
		if msg.what == 460551:
			#### clears source textview text and translation specific textview parameters
			for v in self.editorslist:
				v.source.SetText("")
				v.translation.SetText("")
				v.translation.oldtext=""
				v.translation.oldtextloaded=False
				v.translation.tosave=False

		if msg.what ==  777:
			#Removing B_AVOID_FOCUS flag
			self.SetFlags(0)
			return
			
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
