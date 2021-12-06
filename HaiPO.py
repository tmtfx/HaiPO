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


#******************************************************
#
# Notes: implementare X-generator
# TODO check posettings vs user settings
#
#******************************************************

import os,sys,ConfigParser,struct,re,thread,datetime,time,threading

version='HaiPO 0.3 alpha'
(appname,ver,state)=version.split(' ')

jes = False

#try:
#	import uptime
#except:
#	print "Your python environment has no uptime module"
#	jes = True

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
	from BMimeType import BMimeType
	from BCheckBox import BCheckBox
	from BView import BView
	import BEntry
	from BFilePanel import BFilePanel
	from BEntry import BEntry
	from BScrollBar import BScrollBar
	from InterfaceKit import B_PAGE_UP,B_PAGE_DOWN,B_TAB,B_ESCAPE,B_DOWN_ARROW,B_UP_ARROW,B_V_SCROLL_BAR_WIDTH,B_FULL_UPDATE_ON_RESIZE,B_VERTICAL,B_FOLLOW_ALL,B_FOLLOW_TOP,B_FOLLOW_LEFT,B_FOLLOW_RIGHT,B_WIDTH_FROM_LABEL,B_TRIANGLE_THUMB,B_BLOCK_THUMB,B_FLOATING_WINDOW,B_DOCUMENT_WINDOW,B_TITLED_WINDOW,B_WILL_DRAW,B_NAVIGABLE,B_FRAME_EVENTS,B_ALIGN_CENTER,B_ALIGN_RIGHT,B_FOLLOW_ALL_SIDES,B_MODAL_WINDOW,B_FOLLOW_TOP_BOTTOM,B_FOLLOW_BOTTOM,B_FOLLOW_LEFT_RIGHT,B_SINGLE_SELECTION_LIST,B_NOT_RESIZABLE,B_NOT_ZOOMABLE,B_PLAIN_BORDER,B_FANCY_BORDER,B_NO_BORDER,B_ITEMS_IN_COLUMN,B_AVOID_FOCUS
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
	def __init__(self,frame,name,lang,team,pemail,temail,default):
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
		self.default = BCheckBox((20, 5*h + 101, r - 50, 6*h + 119),'chkdef','Active user',BMessage(150380))
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
				print "rimosso"
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
			smesg=BMessage(17893)
			smesg.AddInt8('savetype',2)
			smesg.AddInt8('indexroot',self.indexroot)
			smesg.AddString('bckppath',BApplication.be_app.WindowAt(0).editorslist[self.indexroot].backupfile)
			BApplication.be_app.WindowAt(0).PostMessage(smesg)


			#entry = self.pofile.metadata_as_entry()
			#print entry.msgstr
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
		self.encoding=BApplication.be_app.WindowAt(0).encoding
		


	def MessageReceived(self, msg):
	
		if msg.what == 5348:
			if self.looktv.Text() != "":
				lista=BApplication.be_app.WindowAt(0).editorslist[BApplication.be_app.WindowAt(0).postabview.Selection()].list.lv
				total=lista.CountItems()
				indaco=lista.CurrentSelection()
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
									lista.Select(now)
									messace=BMessage(963741)
									#messace.AddInt32('inizi',ret)
									#messace.AddInt32('fin',tl)
									#messace.AddInt8('index',0)
									BApplication.be_app.WindowAt(0).PostMessage(messace)

									################################## TODO: evidenziare testo #################################
									break
								ret = item.msgids[1].encode(self.encoding).find(self.looktv.Text())
								if ret >-1:
									lista.Select(now)
									messace=BMessage(963741)
									#messace.AddInt32('inizi',ret)
									#messace.AddInt32('fin',tl)
									#messace.AddInt8('index',1)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									################################## TODO: evidenziare testo #################################
									break
							else:
								ret = item.msgids.encode(self.encoding).find(self.looktv.Text())
								if ret >-1:    #Text().find(self.looktv.Text())>-1:
									lista.Select(now)
									messace=BMessage(963741)
									#messace.AddInt32('inizi',ret)
									#messace.AddInt32('fin',tl)
									#messace.AddInt8('index',0)
									BApplication.be_app.WindowAt(0).PostMessage(messace)
									################################## TODO: evidenziare testo #################################
									break
					
						else:
							item = lista.ItemAt(now)
							if item.hasplural:
								if item.msgids[0].encode(self.encoding).lower().find(self.looktv.Text().lower())>-1:
									lista.Select(now)
									BApplication.be_app.WindowAt(0).PostMessage(BMessage(963741))
									################################## TODO: evidenziare testo #################################
									break
								if item.msgids[1].encode(self.encoding).lower().find(self.looktv.Text().lower())>-1:
									lista.Select(now)
									BApplication.be_app.WindowAt(0).PostMessage(BMessage(963741))
									################################## TODO: evidenziare testo #################################
									break
							else:
								if item.msgids.encode(self.encoding).lower().find(self.looktv.Text().lower())>-1:
									lista.Select(now)
									BApplication.be_app.WindowAt(0).PostMessage(BMessage(963741))
									################################## TODO: evidenziare testo #################################
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
		self.encoding=BApplication.be_app.WindowAt(0).encoding
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
			self.arrayview=BApplication.be_app.WindowAt(0).poview
			datab=[]
			if self.arrayview[0]:
				for entry in self.pof.fuzzy_entries():
					value=[]
					if entry and entry.msgid_plural:
						bubu=len(entry.msgstr_plural)
						y=0
						while y<bubu:
							txt=entry.msgstr_plural[y].encode(self.encoding)
							value.append(txt)
							y+=1
					else:
						txt=entry.msgstr.encode(self.encoding)
						value.append(txt)
					datab.append(value)
			if self.arrayview[1]:
				for entry in self.pof.untranslated_entries():
					value=[]
					if entry and entry.msgid_plural:
						bubu=len(entry.msgstr_plural)
						y=0
						while y<bubu:
							txt=entry.msgstr_plural[y].encode(self.encoding)
							value.append(txt)
							y+=1
					else:
						txt=entry.msgstr.encode(self.encoding)
						value.append(txt)
					datab.append(value)
			if self.arrayview[2]:
				for entry in self.pof.translated_entries():
					value=[]
					if entry and entry.msgid_plural:
						bubu=len(entry.msgstr_plural)
						y=0
						while y<bubu:
							txt=entry.msgstr_plural[y].encode(self.encoding)
							value.append(txt)
							y+=1
					else:
						txt=entry.msgstr.encode(self.encoding)
						value.append(txt)
					datab.append(value)
			if self.arrayview[3]:
				for entry in self.pof.obsolete_entries():
					value=[]
					if entry and entry.msgid_plural:
						bubu=len(entry.msgstr_plural)
						y=0
						while y<bubu:
							txt=entry.msgstr_plural[y].encode(self.encoding)
							value.append(txt)
							y+=1
					else:
						txt=entry.msgstr.encode(self.encoding)
						value.append(txt)
					datab.append(value)
					
			total=lista.CountItems()
			indaco=lista.CurrentSelection()
			applydelta=float(indaco-self.pb.CurrentValue())
			deltamsg=BMessage(7047)
			deltamsg.AddFloat('delta',applydelta)
			BApplication.be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
			max = total
			now = indaco
			lastvalue=now
			partial = False
			partiali = False
			loopa =True
			while loopa:
				now+=1
				if now < total:
						delta=float(now-lastvalue)
						deltamsg=BMessage(7047)
						deltamsg.AddFloat('delta',delta)
						BApplication.be_app.WindowAt(self.thiswindow).PostMessage(deltamsg)
						lastvalue=now
						values=datab[now]
						orb = len(values)
						if self.casesens.Value():
							if orb>1:
								for items in values:
									if items.find(self.looktv.Text())>-1:
										lista.Select(now)################################ todo: switch transtabview se sul plurale ##############
										BApplication.be_app.WindowAt(0).PostMessage(BMessage(963741)) ############################ TODO: evidenziare testo #################
										break
							else:
								if values[0].find(self.looktv.Text())>-1:
									lista.Select(now)
									BApplication.be_app.WindowAt(0).PostMessage(BMessage(963741)) ############################ TODO: evidenziare testo #################
									break
						else:
							if orb>1:
								for items in values:
									if items.lower().find(self.looktv.Text().lower())>-1:
										lista.Select(now)################################ todo: switch transtabview se sul plurale ##############
										BApplication.be_app.WindowAt(0).PostMessage(BMessage(963741)) ############################ TODO: evidenziare testo #################
										break
							else:
								if values[0].lower().find(self.looktv.Text().lower())>-1:
									lista.Select(now)
									BApplication.be_app.WindowAt(0).PostMessage(BMessage(963741)) ############################ TODO: evidenziare testo #################
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

		elif msg.what == 7047:
			addfloat=msg.FindFloat('delta')
			self.pb.Update(addfloat)
		
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
	kWindowFrame = (50, 50, 600, 750)
	kButtonFrame = (395, 661, 546, 696)
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
		stuff = '\n\t\t\t\t\t\t\t\t\t'+appname+'\n\n\t\t\t\t\t\t\t\t\t\t\t\tA simple PO editor\n\t\t\t\t\t\t\t\t\t\t\t\tfor Haiku, version '+ver+' '+state+'\n\t\t\t\t\t\t\t\t\t\t\t\tcodename "Pobeda"\n\n\t\t\t\t\t\t\t\t\t\t\t\tby Fabio Tomat\n\t\t\t\t\t\t\t\t\t\t\t\te-mail:\n\t\t\t\t\t\t\t\t\t\t\t\tf.t.public@gmail.com\n\n\n\n\n\nMIT LICENSE\nCopyright © 2021 Fabio Tomat\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'
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
		if self.item.occurrency:
			bckpmsg=BMessage(17892)
			bckpmsg.AddInt32('OID',self.item.occurvalue)
		else:
			bckpmsg=BMessage(17893)
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
		return BListView.MouseDown(self,point)


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
						item = MsgStrItem(msgids,msgstrs,comments,context,2,encoding,True)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
						else:
							item.SetOccurrency(False)						
					else:
						if entry.comment:
							comments=entry.comment
						else:
							comments = ""
						if entry.msgctxt:
							context = entry.msgctxt
						else:
							context = ""
						item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,2,encoding,False)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
							print "valore di associazione",value
						else:
							item.SetOccurrency(False)						
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
						item = MsgStrItem(msgids,msgstrs,comments,context,0,encoding,True)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
						else:
							item.SetOccurrency(False)						
					else:
						if entry.comment:
							comments=entry.comment
						else:
							comments = ""
						if entry.msgctxt:
							context = entry.msgctxt
						else:
							context = ""
						item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,0,encoding,False)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
						else:
							item.SetOccurrency(False)						
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
						item = MsgStrItem(msgids,msgstrs,comments,context,1,encoding,True)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
						else:
							item.SetOccurrency(False)						
					else:
						if entry.comment:
							comments=entry.comment
						else:
							comments = ""
						if entry.msgctxt:
							context = entry.msgctxt
						else:
							context = ""
						item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,1,encoding,False)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
						else:
							item.SetOccurrency(False)
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
						item = MsgStrItem(msgids,msgstrs,comments,context,3,encoding,True)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
						else:
							item.SetOccurrency(False)
					else:
						if entry.comment:
							comments=entry.comment
						else:
							comments = ""
						if entry.msgctxt:
							context = entry.msgctxt
						else:
							context = ""
						item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,3,encoding,False)
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
						conto=0
						for ent in pofile:
							if ent.msgid == entry.msgid:
								conto+=1
						if conto > 1:
							item.SetOccurrency(True)
							value=len(self.occumemo)
							self.occumemo.append((entry.msgid,value))
							item.SetOccurrencyID(value)
						else:
							item.SetOccurrency(False)							
					self.lv.AddItem(item)
			

		
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
	tosave=False
	txttosave=""	# nel lungo termine eliminare
	txttosavepl=[]  # nel lungo termine eliminare
	dragcheck=False
	comments=""
	context=""

	
	def __init__(self, msgids,msgstrs,comments,context,state,encoding,plural):
		if plural:
			self.text = msgids[0].encode(encoding)  #it's in english should this always be utf-8?
		else:
			self.text = msgids.encode(encoding)
		self.comments = comments
		self.context = context
		self.msgids = msgids
		self.msgstrs = msgstrs
		self.state = state
		self.hasplural = plural
		self.occurrency=False
		self.occurvalue=0
		self.previous=False
		self.previousmsgs=[]
		self.tcomment=""
		self.linenum=None
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
		#should I? return BListItem.DrawItem(self, owner, frame,complete)
		
	def SetOccurrencyID(self,value):
		self.occurvalue=value
	
	def SetLineNum(self,value):
		self.linenum=value
		
	def SetOccurrency(self,bool):
		self.occurrency=bool
		
	def SetPreviousMsgs(self,msgs):
		self.previousmsgs.append(msgs)
	
	def SetPrevious(self,bool):
		self.previous=bool

	def SetTranslatorComment(self,tcomment):
		self.tcomment=tcomment
		
	def Text(self):
		return self.text
		
class temporizedcheck:
	def run(self,oldtext):
			self.event.wait(1)
			#print "this is the old text",oldtext
			#print "mando messaggio 112118"

class EventTextView(BTextView):
	def __init__(self,superself,frame,name,textRect,resizingMode,flags):
		self.superself=superself
		self.oldtext=""
		self.oldtextloaded=False
		self.tosave=False
		BTextView.__init__(self,frame,name,textRect,resizingMode,flags)
		self.mousemsg=struct.unpack('!l', '_MMV')[0]
		self.dragmsg=struct.unpack('!l', 'MIME')[0]
		self.dragndrop = False
		self.event= threading.Event()
		
	def Save(self):
		cursel=self.superself.editorslist[self.superself.postabview.Selection()]
		thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
		thisBlistitem.tosave=True
		tabs=len(self.superself.listemsgstr)-1
		if thisBlistitem.occurrency:
			bckpmsg=BMessage(17892)
			bckpmsg.AddInt32('OID',thisBlistitem.occurvalue)
		else:
			bckpmsg=BMessage(17893)
		bckpmsg.AddInt8('savetype',1)
		bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
		bckpmsg.AddInt8('plurals',tabs)
		bckpmsg.AddInt32('tabview',self.superself.postabview.Selection())
		if tabs == 0:
			thisBlistitem.txttosave=self.Text()
			thisBlistitem.msgstrs=self.Text().decode(self.superself.encoding)
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
			print "salvo solo singolare"
		else:
			print "provo a salvare tutto"
			thisBlistitem.txttosavepl=[]
			thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
			thisBlistitem.msgstrs=[]
			thisBlistitem.msgstrs.append(self.superself.listemsgstr[0].trnsl.Text().decode(self.superself.encoding))
			bckpmsg.AddString('translation',thisBlistitem.txttosave)
			cox=1
			while cox < tabs+1:
				thisBlistitem.msgstrs.append(self.superself.listemsgstr[cox].trnsl.Text().decode(self.superself.encoding))
				thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
				bckpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgstr[cox].trnsl.Text())
				cox+=1
		bckpmsg.AddString('bckppath',cursel.backupfile)
		BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)  #save backup file
		#ocio a questa riga qui sotto
		#self.superself.infoprogress.SetText(str(cursel.pofile.percent_translated())) #reinsert if something doesn't work properly but it should write in 17892/3

	def checklater(self,name,oldtext,cursel,indexBlistitem):
			mes=BMessage(112118)
			mes.AddInt8('cursel',cursel)
			mes.AddInt32('indexBlistitem',indexBlistitem)
			mes.AddString('oldtext',oldtext)
			self.event.wait(0.1)
			BApplication.be_app.WindowAt(0).PostMessage(mes)

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
		print "mouse up normale"
		self.superself.drop.release()
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
		
		####################### TODO   controllo ortografia ##############################
		try:
			ochar=ord(char)
			if ochar in (B_DOWN_ARROW,B_UP_ARROW,B_TAB,B_PAGE_UP,B_PAGE_DOWN):
				self.superself.sem.acquire()
				value=self.superself.modifier #CTRL pressed
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
				elif ochar == B_TAB:
					if not value:
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
					return BTextView.KeyDown(self,char,bytes)
				if ochar != B_TAB: # needed to pass up/down keys to textview	
					return BTextView.KeyDown(self,char,bytes)
					
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
				return
			else:
				if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
					if ochar == 115:					#CTRL+SHIF+S
						self.superself.sem.acquire()
						value=self.superself.shortcut #CTRL SHIFT pressed
						self.superself.sem.release()
						if value:
							cursel=self.superself.editorslist[self.superself.postabview.Selection()]
							thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
							thisBlistitem.tosave=True
							tabs=len(self.superself.listemsgstr)-1
							bckpmsg=BMessage(17893)
							bckpmsg.AddInt8('savetype',1)
							bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
							bckpmsg.AddInt8('plurals',tabs)
							bckpmsg.AddInt32('tabview',self.superself.postabview.Selection())
							if tabs == 0:
								thisBlistitem.txttosave=thisBlistitem.text.decode(self.superself.encoding)
								bckpmsg.AddString('translation',thisBlistitem.txttosave)
								print "salvo solo singolare"
							else:
								print "provo a salvare tutto"
								thisBlistitem.txttosavepl=[]
								thisBlistitem.txttosave=self.superself.listemsgid[0].src.Text()
								bckpmsg.AddString('translation',thisBlistitem.txttosave)
								cox=1
								while cox < tabs+1:
									thisBlistitem.txttosavepl.append(self.superself.listemsgid[1].src.Text())
									bckpmsg.AddString('translationpl'+str(cox-1),self.superself.listemsgid[1].src.Text())
									cox+=1
							bckpmsg.AddString('bckppath',cursel.backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
							kmesg=BMessage(130550)
							kmesg.AddInt8('movekind',0)
							BApplication.be_app.WindowAt(0).PostMessage(kmesg)
							return

					print "carattere normale inserito"
					BTextView.KeyDown(self,char,bytes)
					if self.oldtext != self.Text():
						thisBlistitem=self.superself.editorslist[self.superself.postabview.Selection()].list.lv.ItemAt(self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection())
						thisBlistitem.tosave=True
						tabs=len(self.superself.listemsgstr)-1
						if tabs == 0:
							thisBlistitem.txttosave=self.Text()
						if tabs == 0:
							thisBlistitem.txttosavepl=[]
							thisBlistitem.txttosave=self.superself.listemsgstr[0].trnsl.Text()
							cox=1
							while cox < tabs+1:
								thisBlistitem.txttosavepl.append(self.superself.listemsgstr[cox].trnsl.Text())
								cox+=1
						self.tosave=True  # This says you should save the string before proceeding the same for blistitem.tosave doublecheck
					return
		except:
			if self.superself.editorslist[self.superself.postabview.Selection()].list.lv.CurrentSelection()>-1:
				print "carattere particolare inserito"
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
		
class srctabbox(BBox):
	def __init__(self,playground1,name,altece):
		self.name = name
		BBox.__init__(self,(0,0,playground1[2]-playground1[0],playground1[3]-playground1[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.hsrc = playground1[3] - playground1[1] - altece 
		self.src = BTextView((playground1[0],playground1[1],playground1[2]-playground1[0],playground1[3]-playground1[1]),name+'_source_BTextView',(5.0,5.0,playground1[2]-5,playground1[3]-5),B_FOLLOW_ALL,B_WILL_DRAW|B_FRAME_EVENTS)
		self.src.MakeEditable(False)
		self.AddChild(self.src)
class trnsltabbox(BBox):
	def __init__(self,playground2,name,altece,superself):
		self.name = name
		BBox.__init__(self,(0,0,playground2[2]-playground2[0],playground2[3]-playground2[1]),name,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		self.trnsl = EventTextView(superself,(playground2[0],playground2[1],playground2[2]-playground2[0]-20,playground2[3]-playground2[1]),name+'_translation_BTextView',(5.0,5.0,playground2[2]-5,playground2[3]-5),B_FOLLOW_ALL,B_WILL_DRAW|B_FRAME_EVENTS)
		self.trnsl.MakeEditable(True)
		self.AddChild(self.trnsl)
		bi,bu,bo,ba = playground2
		self.scrollbtrans=BScrollBar((bo -21,1,bo-5,ba-5),name+'_ScrollBar',self.trnsl,0.0,0.0,B_VERTICAL)
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
		bckpmsg=BMessage(17893)
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
	def __init__(self,frame,name,percors,pofileloaded,arrayview,encoding):
		self.pofile = pofileloaded
#		print self.pofile.header
		self.name = name
		self.encoding=encoding
		self.filen, self.file_ext = os.path.splitext(percors)
		self.backupfile= self.filen+".temp"+self.file_ext
		self.orderedmetadata=self.pofile.ordered_metadata()
		self.fp=BFilePanel(B_SAVE_PANEL)
		pathorig,nameorig=os.path.split(percors)
		self.fp.SetPanelDirectory(pathorig)
		self.fp.SetSaveText(nameorig)

#		if file_ext=='.po':
#			self.typefile=0
#		elif file_ext=='.mo':
#			self.typefile=1
#		elif file_ext=='.gmo':
#			self.typefile=2
#		elif file_ext=='.pot':
#			
		
		ind=0
		for entry in self.pofile:
				ind=ind+1
		
		contor = frame
		a,s,d,f = contor
		BBox.__init__(self,(a,s,d-5,f-35),name,B_FOLLOW_ALL,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW | B_FRAME_EVENTS,B_FANCY_BORDER)
		contor=self.Bounds()
		l, t, r, b = contor
		self.list = ScrollView((5, 5, r -22, b-5), name+'_ScrollView')
		self.AddChild(self.list.topview())
		self.scrollb = BScrollBar((r -21,5,r-5,b-5),name+'_ScrollBar',self.list.listview(),0.0,float(ind),B_VERTICAL)#len(datab)
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
					item = MsgStrItem(msgids,msgstrs,comments,context,2,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
				else:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
							context = entry.msgctxt
					else:
							context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,2,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
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
					item = MsgStrItem(msgids,msgstrs,comments,context,0,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
				else:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
							context = entry.msgctxt
					else:
							context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,0,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
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
					item = MsgStrItem(msgids,msgstrs,comments,context,1,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
				else:
					if entry.comment:
						comments=entry.comment
					else:
						comments = ""
					if entry.msgctxt:
							context = entry.msgctxt
					else:
							context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,1,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
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
					item = MsgStrItem(msgids,msgstrs,comments,context,3,encoding,True)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
				else:
					if entry.comment:
						comments = entry.comment
					else:
						comments = ""
					if entry.msgctxt:
							context = entry.msgctxt
					else:
							context = ""
					item = MsgStrItem(entry.msgid,entry.msgstr,comments,context,3,encoding,False)
					if entry.tcomment:
						item.SetTranslatorComment(entry.tcomment)
					if entry.previous_msgid:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid",entry.previous_msgid.encode(self.encoding)))
					if entry.previous_msgid_plural:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgid_plural",entry.previous_msgid_plural))
					if entry.previous_msgctxt:
						item.SetPrevious(True)
						item.SetPreviousMsgs(("msgctxt",entry.previous_msgctxt.encode(self.encoding)))
					item.SetLineNum(entry.linenum)
					conto=0
					for ent in self.pofile:
						if ent.msgid == entry.msgid:
							conto+=1
							if conto >1:
								break
					if conto > 1:
						item.SetOccurrency(True)
						value=len(self.occumemo)
						self.occumemo.append((entry.msgid,value))
						item.SetOccurrencyID(value)
					else:
						item.SetOccurrency(False)
				self.list.lv.AddItem(item)
		
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
		return BTabView.MouseDown(self,point)

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
		return BTabView.MouseDown(self,point)

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
							bckpmsg=BMessage(17893)
							bckpmsg.AddInt8('savetype',1)
							bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
							bckpmsg.AddInt8('plurals',tabs)
							bckpmsg.AddInt32('tabview',self.Selection())
							if tabs == 0:
								thisBlistitem.txttosave=self.superself.listemsgstr[self.superself.transtabview.Selection()].trnsl.Text()
								bckpmsg.AddString('translation',thisBlistitem.txttosave)
								print "salvo solo singolare"
							else:
								print "provo a salvare tutto"
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
						self.superself.transtabview.Select(1)									############# bug fix
						self.superself.transtabview.Select(0)
						idlen=len(self.superself.listemsgid)
						x=0
						while x!=idlen:
							self.superself.listemsgid[x].src.SetText("")
							x+=1
						#################### BUG ?##################
						self.superself.srctabview.Select(1)
						self.superself.srctabview.Select(0)
			gg=gg+1
		
		return BTabView.MouseDown(self,point)

		

class PoWindow(BWindow):
	Menus = (
		('File', ((295485, 'Open'), (2, 'Save'), (1, 'Close'), (5, 'Save as...'),(None, None),(B_QUIT_REQUESTED, 'Quit'))),
		('Translation', ((3, 'Copy from source'), (4,'Edit comment'), (70,'Done and next'), (71,'Mark/Unmark fuzzy'), (72, 'Previous w/o saving'),(73,'Next w/o saving'),(None, None), (6, 'Find source'), (7, 'Find/Replace translation'))),
		('View', ((74,'Fuzzy'), (75, 'Untranslated'),(76,'Translated'),(77, 'Obsolete'))),
		('Settings', ((41, 'User settings'), (42, 'Po properties'), (43, 'Po header'))),
		('About', ((8, 'Help'),(None, None),(9, 'About')))
		)
	def __init__(self, frame):
		selectionmenu=0
		BWindow.__init__(self, frame, 'Simple PO editor for Haiku!', B_TITLED_WINDOW,0)
		bounds = self.Bounds()
		self.bar = BMenuBar(bounds, 'Bar')
		x, barheight = self.bar.GetPreferredSize()
		self.modifier=False
		self.poview=[True,True,True,False]
		self.drop = threading.Semaphore()
		self.sem = threading.Semaphore()
		self.shortcut=False
		global confile
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

		
		self.background.AddChild(self.lubox)
		self.postabview = postabview(self,(5.0, 5.0, d*3/4-5, b-barheight-245), 'postabview',B_WIDTH_FROM_LABEL)

		altece = self.postabview.TabHeight()
		tfr = (5.0, 5.0, d*3/4-5, s-5)
		self.trc = (0.0, 0.0, tfr[2] - tfr[0], tfr[3] - tfr[1])

		self.tabslabels=[]
		self.editorslist=[]
		
		self.background.AddChild(self.postabview)



		playground1 = (5,b-268,r - d*1/4-5, s-120)
		self.srctabview = sourcetabview(playground1, 'sourcetabview',B_WIDTH_FROM_LABEL,B_FOLLOW_BOTTOM|B_FOLLOW_LEFT_RIGHT,B_FULL_UPDATE_ON_RESIZE |B_WILL_DRAW|B_FRAME_EVENTS,self)

		altece = self.srctabview.TabHeight()
		tabrc = (3.0, 3.0, playground1[2] - playground1[0], playground1[3] - playground1[1]-altece)
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

####### TOODO: send a B_END(value 4) keypress when itemselected on listview


	def MessageReceived(self, msg):
#		print "This is a system message?", msg.IsSystem()
		if msg.what == B_MODIFIERS_CHANGED: #quando modificatore ctrl cambia stato
			value=msg.FindInt32("modifiers")
			self.sem.acquire()
			print value
			if value==self.modifiervalue or value==self.modifiervalue+8 or value ==self.modifiervalue+32 or value ==self.modifiervalue+40:
				#print "ctrl premuto self.modifier diventa true"
				self.modifier=True
				self.shortcut = False
			elif value == self.modifiervalue+4357 or value==self.modifiervalue+265 or value==self.modifiervalue+289 or value == self.modifiervalue+297:
				#print "ctrl maiusc premuto self.shortcut diventa true"
				self.shortcut = True
				self.modifier = False
			else:
				#print "self.modifier e self.shortcut diventano false"
				self.modifier=False
				self.shortcut=False
			self.sem.release()
			return
#		elif msg.what == B_UNMAPPED_KEY_DOWN:
#			msg.PrintToStream()
		elif msg.what == B_KEY_DOWN:	#on tab key pressed, focus on translation or translation of first item list of translations
			key=msg.FindInt32('key')
			if key==38: #tab key
				lung = len(self.editorslist)
				if lung > 0:
					if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
						self.listemsgstr[self.transtabview.Selection()].trnsl.MakeFocus()
					else:
						self.editorslist[self.postabview.Selection()].list.lv.Select(0)
						self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()

			elif key == 61: # s key
				if self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()>-1:
					self.sem.acquire()
					print "ok mando messaggio"
					if self.shortcut:
						BApplication.be_app.WindowAt(0).PostMessage(3)
					else:
						pass
					self.sem.release()
			return

		elif msg.what == 295485:
			self.ofp.Show()
			return
			
		elif msg.what == 1:
			# Close opened file
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
					self.listemsgid[0].src.SetText("")
					self.srctabview.Select(1)
					self.srctabview.Select(0)
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
					self.listemsgid[0].src.SetText("")
					self.srctabview.Select(1)
					self.srctabview.Select(0)
			self.postabview.RemoveTab(whichrem)
			self.tabslabels.pop(whichrem)
			self.editorslist.pop(whichrem)
			
			
		elif msg.what == 2:
			# Save current file
			try:
				Config.read(confile)
				defname=ConfigSectionMap("Users")['default']
			except:
				defname=self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']
			now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
			savepath=self.editorslist[self.postabview.Selection()].filen+self.editorslist[self.postabview.Selection()].file_ext
			self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']=defname
			self.editorslist[self.postabview.Selection()].pofile.metadata['PO-Revision-Date']=now
			self.editorslist[self.postabview.Selection()].pofile.metadata['X-Editor']=version
			self.editorslist[self.postabview.Selection()].pofile.save(savepath)
			
			
		elif msg.what == 3:
			#copy from source
			print "copio da sorgente"
			cursel=self.editorslist[self.postabview.Selection()]
			thisBlistitem=cursel.list.lv.ItemAt(cursel.list.lv.CurrentSelection())
			thisBlistitem.tosave=True
			tabs=len(self.listemsgstr)-1
			if thisBlistitem.occurrency:
				bckpmsg=BMessage(17892)
				bckpmsg.AddInt32('OID',thisBlistitem.occurvalue)
			else:
				bckpmsg=BMessage(17893)
			bckpmsg.AddInt8('savetype',1)
			bckpmsg.AddInt32('tvindex',cursel.list.lv.CurrentSelection())
			bckpmsg.AddInt8('plurals',tabs)
			bckpmsg.AddInt32('tabview',self.postabview.Selection())
			if tabs == 0:   #->      if not thisBlistitem.hasplural:                         <-------------------------- or this?
				thisBlistitem.txttosave=thisBlistitem.text.decode(self.encoding)
				thisBlistitem.msgstrs=thisBlistitem.txttosave
				bckpmsg.AddString('translation',thisBlistitem.txttosave)
			else:
				thisBlistitem.txttosavepl=[]
				thisBlistitem.txttosave=self.listemsgid[0].src.Text().decode(self.encoding)
				thisBlistitem.msgstrs=[]
				thisBlistitem.msgstrs.append(thisBlistitem.txttosave)
				bckpmsg.AddString('translation',thisBlistitem.txttosave)
				cox=1
				while cox < tabs+1:
					thisBlistitem.msgstrs.append(self.listemsgid[1].src.Text().decode(self.encoding))
					thisBlistitem.txttosavepl.append(self.listemsgid[1].src.Text().decode(self.encoding))
					bckpmsg.AddString('translationpl'+str(cox-1),self.listemsgid[1].src.Text())    #<------- check for decode(self.encoding)
					cox+=1
			bckpmsg.AddString('bckppath',cursel.backupfile)
			BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)

			kmesg=BMessage(130550)
			kmesg.AddInt8('movekind',0)
			BApplication.be_app.WindowAt(0).PostMessage(kmesg)
			return
		
		elif msg.what == 5:
			# Save as
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
			self.Findsrc = Findsource()
			self.Findsrc.Show()
		
		elif msg.what == 7:
			# Find/Replace translation
			self.FindReptrnsl = FindRepTrans()
			self.FindReptrnsl.Show()
		
		elif msg.what == 9:
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
		
		elif msg.what == 32:
			indextab=self.postabview.Selection()
			cursel=self.editorslist[indextab]
			listsel=cursel.list.lv.CurrentSelection()
			
			thisBlistitem=cursel.list.lv.ItemAt(listsel)
			self.tcommentdialog=TranslatorComment(listsel,indextab,thisBlistitem,self.encoding)
			self.tcommentdialog.Show()
			
		elif msg.what == 42:
			# PO metadata
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
		
		elif msg.what == 43:
			#Po header
			tmp = self.postabview.Selection()
			self.HeaderWindow = HeaderWindow(tmp,self.editorslist[tmp].pofile,self.encoding)
			self.HeaderWindow.Show()

		elif msg.what == 70:
			# Done and next
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
				if thisBlistitem.occurrency:
					bckpmsg=BMessage(17892)
					bckpmsg.AddInt32('OID',thisBlistitem.occurvalue)
				else:
					bckpmsg=BMessage(17893)
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
			thistranslEdit=self.listemsgstr[self.transtabview.Selection()].trnsl
			if thistranslEdit.tosave:
				thisBlistitem=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
				thisBlistitem.tosave=False
				thisBlistitem.txttosave=""
			kmesg=BMessage(130550)
			kmesg.AddInt8('movekind',0)
			BApplication.be_app.WindowAt(0).PostMessage(kmesg)
		
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
			return

		elif msg.what == 130550: # change listview selection
			movetype=msg.FindInt8('movekind')
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
				###
			thisBlistitem=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection())
			try:
				if thisBlistitem.tosave: #it happens when something SOMEHOW has not been saved
					print("testo da salvare (this shouldn\'t happen)",thisBlistitem.txttosave)
			except:
				pass
			return

		elif msg.what == 305:
			#USER CREATOR WIZARD
			self.maacutent = MaacUtent(True)
			self.maacutent.Show()
			self.SetFlags(B_AVOID_FOCUS)
			return
			
		elif msg.what == 112118:
			#launch a delayed check
			oldtext=msg.FindString('oldtext')
			cursel=msg.FindInt8('cursel')
			indexBlistitem=msg.FindInt32('indexBlistitem')
			tabs=len(self.listemsgstr)-1
			if cursel == self.postabview.Selection():
				tmp=self.editorslist[cursel]
				if indexBlistitem == tmp.list.lv.CurrentSelection():
					if self.listemsgstr[self.transtabview.Selection()].trnsl.oldtext != self.listemsgstr[self.transtabview.Selection()].trnsl.Text():  ### o è meglio controllare nel caso di plurale tutti gli eventtextview?
						self.listemsgstr[self.transtabview.Selection()].trnsl.tosave=True
		
		elif msg.what == 17892:
			#same as 17893 for multiple occurrencies
			try:
				Config.read(confile)
				defname=ConfigSectionMap("Users")['default']
			except:
				defname=self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']
			now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M+0000')
			# save to backup and update the blistitem
			OID=msg.FindInt32('OID')
			bckppath = msg.FindString('bckppath')
			savetype = msg.FindInt8('savetype')
			if savetype == 0: #simple save used for fuzzy state and metadata change
				self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']=defname
				self.editorslist[self.postabview.Selection()].pofile.metadata['PO-Revision-Date']=now
				self.editorslist[self.postabview.Selection()].pofile.metadata['X-Editor']=version
				self.editorslist[self.postabview.Selection()].pofile.save(bckppath)
				return
			elif savetype == 1:
				self.pofile=self.editorslist[self.postabview.Selection()].pofile
				occurem=[]
				if self.poview[0]:
					for entry in self.pofile.fuzzy_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
				if self.poview[1]:
					for entry in self.pofile.untranslated_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
				if self.poview[2]:
					for entry in self.pofile.translated_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
				if self.poview[3]:
					for entry in self.pofile.obsolete_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
			
				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('translation')
				tabbi=msg.FindInt8('plurals')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				entry = self.workonthisentry
				if entry and entry.msgid_plural:
						y=0
						textsavepl=[]
						entry.msgstr_plural[0] = textsave.decode(self.encoding)
						while y < tabbi:
							varname='translationpl'+str(y) ######################################### check! stry(y) or  y+1???????? plurale
							intended=msg.FindString(varname)
							textsavepl.append(intended) #useless???
							y+=1
							entry.msgstr_plural[y]=intended.decode(self.encoding)
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						if entry.previous_msgid:
							entry.previous_msgid=None
						if entry.previous_msgid_plural:
							entry.previous_msgid_plural=None
						if entry.previous_msgctxt:
							entry.previous_msgctxt=None

				elif entry and not entry.msgid_plural:
						entry.msgstr = textsave.decode(self.encoding)
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
				scheda.pofile.save(bckppath)
				scheda.list.lv.ItemAt(tvindex).state=1
				scheda.list.lv.ItemAt(tvindex).tosave=False
				self.editorslist[intscheda].list.lv.ItemAt(tvindex).txttosave=""
				self.editorslist[intscheda].list.lv.ItemAt(tvindex).txttosavepl=[]
				return
			elif savetype == 2: ############ No need on multiple occurrencies
				#save of metadata
				indexroot=msg.FindInt8('indexroot')
				self.editorslist[indexroot].pofile.metadata['Last-Translator']=defname # metadata saved from po settings
				self.editorslist[indexroot].pofile.metadata['PO-Revision-Date']=now
				self.editorslist[indexroot].pofile.metadata['X-Editor']=version
				self.editorslist[indexroot].pofile.save(bckppath)
				return
			elif savetype == 3:
				self.pofile=self.editorslist[self.postabview.Selection()].pofile
				occurem=[]
				if self.poview[0]:
					for entry in self.pofile.fuzzy_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
				if self.poview[1]:
					for entry in self.pofile.untranslated_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
				if self.poview[2]:
					for entry in self.pofile.translated_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
				if self.poview[3]:
					for entry in self.pofile.obsolete_entries():
						if entry and entry.msgid_plural:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
						else:
							conto=0
							for ent in self.pofile:
								if ent.msgid == entry.msgid:
									conto+=1
							if conto > 1:
									value=len(occurem)
									occurem.append((entry.msgid,value))
									if value == OID:
										self.workonthisentry=entry
				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('tcomment')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				entry = self.workonthisentry
				### non passava di qui
				entry.tcomment=textsave
				scheda.pofile.metadata['Last-Translator']=defname
				scheda.pofile.metadata['PO-Revision-Date']=now
				scheda.pofile.metadata['X-Editor']=version
				scheda.pofile.save(bckppath)
				self.postabview.Select(intscheda)
				scheda.list.lv.DeselectAll()
				scheda.list.lv.Select(tvindex)
				return

			self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated()))
			return
		elif msg.what == 17893:
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
				self.editorslist[self.postabview.Selection()].pofile.metadata['Last-Translator']=defname
				self.editorslist[self.postabview.Selection()].pofile.metadata['PO-Revision-Date']=now
				self.editorslist[self.postabview.Selection()].pofile.metadata['X-Editor']=version
				self.editorslist[self.postabview.Selection()].pofile.save(bckppath)
				return
			elif savetype == 1:
				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('translation')
				tabbi=msg.FindInt8('plurals')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				entry = scheda.pofile.find(scheda.list.lv.ItemAt(tvindex).Text().decode(self.encoding))
				if entry and entry.msgid_plural:
						y=0
						textsavepl=[]
						entry.msgstr_plural[0] = textsave.decode(self.encoding)
						while y < tabbi:
							varname='translationpl'+str(y)                                               ########################### give me one more eye?
							intended=msg.FindString(varname)
							textsavepl.append(intended) #useless???
							y+=1
							entry.msgstr_plural[y]=intended.decode(self.encoding)
						if 'fuzzy' in entry.flags:
							entry.flags.remove('fuzzy')
						if entry.previous_msgid:
							entry.previous_msgid=None
						if entry.previous_msgid_plural:
							entry.previous_msgid_plural=None
						if entry.previous_msgctxt:
							entry.previous_msgctxt=None						

				elif entry and not entry.msgid_plural:
						entry.msgstr = textsave.decode(self.encoding)
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
				scheda.pofile.save(bckppath)
				scheda.list.lv.ItemAt(tvindex).state=1
				scheda.list.lv.ItemAt(tvindex).tosave=False
				self.editorslist[intscheda].list.lv.ItemAt(tvindex).txttosave=""
				self.editorslist[intscheda].list.lv.ItemAt(tvindex).txttosavepl=[]
				return
			elif savetype == 2:
				#save of metadata
				indexroot=msg.FindInt8('indexroot')
				self.editorslist[indexroot].pofile.metadata['Last-Translator']=defname # metadata saved from po settings
				self.editorslist[indexroot].pofile.metadata['PO-Revision-Date']=now
				self.editorslist[indexroot].pofile.metadata['X-Editor']=version
				self.editorslist[indexroot].pofile.save(bckppath)
				return
			elif savetype == 3:
				tvindex=msg.FindInt32('tvindex')
				textsave=msg.FindString('tcomment')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				entry = scheda.pofile.find(scheda.list.lv.ItemAt(tvindex).Text().decode(self.encoding))
				entry.tcomment=textsave
				scheda.pofile.metadata['Last-Translator']=defname
				scheda.pofile.metadata['PO-Revision-Date']=now
				scheda.pofile.metadata['X-Editor']=version
				scheda.pofile.save(bckppath)
				self.postabview.Select(intscheda)
				scheda.list.lv.DeselectAll()
				scheda.list.lv.Select(tvindex)
				return
			elif savetype == 4:
				textsave=msg.FindString('header')
				intscheda=msg.FindInt32('tabview')
				scheda=self.editorslist[intscheda]
				scheda.pofile.header=textsave
				scheda.pofile.metadata['Last-Translator']=defname
				scheda.pofile.metadata['PO-Revision-Date']=now
				scheda.pofile.metadata['X-Editor']=version
				scheda.pofile.save(bckppath)
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
				if self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()).occurrency:
					pofi=self.editorslist[self.postabview.Selection()].pofile
					txttosearch=self.editorslist[self.postabview.Selection()].list.SelectedText().decode(self.encoding)
					OID=self.editorslist[self.postabview.Selection()].list.lv.ItemAt(self.editorslist[self.postabview.Selection()].list.lv.CurrentSelection()).occurvalue
					occurem=[]
					if self.poview[0]:
						for entry in pofi.fuzzy_entries():
							if entry and entry.msgid_plural:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
							else:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
					if self.poview[1]:
						for entry in pofi.untranslated_entries():
							if entry and entry.msgid_plural:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
							else:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
					if self.poview[2]:
						for entry in pofi.translated_entries():
							if entry and entry.msgid_plural:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
							else:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
					if self.poview[3]:
						for entry in pofi.obsolete_entries():
							if entry and entry.msgid_plural:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
							else:
								conto=0
								for ent in pofi:
									if ent.msgid == entry.msgid:
										conto+=1
								if conto > 1:
										value=len(occurem)
										occurem.append((entry.msgid,value))
										if value == OID:
											self.workonthisentry=entry
					if 'fuzzy' in self.workonthisentry.flags:
						self.workonthisentry.flags.remove('fuzzy')
						if self.workonthisentry.previous_msgid:
							self.workonthisentry.previous_msgid=None
						if self.workonthisentry.previous_msgid_plural:
							self.workonthisentry.previous_msgid_plural=None
						if self.workonthisentry.previous_msgctxt:
							self.workonthisentry.previous_msgctxt=None
					else:
						self.workonthisentry.flags.append('fuzzy')
					bckpmsg=BMessage(17893)
					bckpmsg.AddInt8('savetype',0)
					bckpmsg.AddString('bckppath',self.editorslist[self.postabview.Selection()].backupfile)
					BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
				else:
					txttosearch=self.editorslist[self.postabview.Selection()].list.SelectedText()
					for entry in self.editorslist[self.postabview.Selection()].pofile:
						if entry.msgid.encode(self.encoding) == txttosearch:
							if 'fuzzy' in entry.flags:
								entry.flags.remove('fuzzy')
								if entry.previous_msgid:
									entry.previous_msgid=None
								if entry.previous_msgid_plural:
									entry.previous_msgid_plural=None
								if entry.previous_msgctxt:
									entry.previous_msgctxt=None
							else:
								entry.flags.append('fuzzy')
							bckpmsg=BMessage(17893)
							bckpmsg.AddInt8('savetype',0)
							bckpmsg.AddString('bckppath',self.editorslist[self.postabview.Selection()].backupfile)
							BApplication.be_app.WindowAt(0).PostMessage(bckpmsg)
							break
				self.editorslist[self.postabview.Selection()].list.reload(self.poview,self.editorslist[self.postabview.Selection()].pofile,self.encoding)
		

		if msg.what == 54173:
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
			
		elif msg.what == 460550:
			# selection from listview
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
				
				txttosearch=self.editorslist[self.postabview.Selection()].list.SelectedText()
				
				#######  check for multiple occurencies just for debug ########
				count=0
				for entry in self.editorslist[self.postabview.Selection()].pofile:
					if entry.msgid.encode(self.encoding) == txttosearch:
						count = count +1
						if count > 1:
							print "multiple occurrencies for this entry msgid"
							break
				################################################################
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
							self.listemsgid[0].src.SetText(item.msgids[0].encode(self.encoding))
							self.listemsgid[1].src.SetText(item.msgids[1].encode(self.encoding))
							ww=0
							while ww<beta:
								self.transtablabels.append(BTab())
								if ww == 0:
									self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs[0].encode(self.encoding))
									self.transtabview.SetFocusTab(x,True)
									self.transtabview.Select(x)
									self.transtabview.Select(0)
								else:
									self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr['+str(ww)+']',altece,self))
									self.listemsgstr[ww].trnsl.SetPOReadText(item.msgstrs[ww].encode(self.encoding))
									self.transtabview.AddTab(self.listemsgstr[ww],self.transtablabels[ww])
								ww=ww+1
				else:
							self.Nichilize()
							self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
							self.transtablabels.append(BTab())
							self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
#######################################################################
							self.listemsgid[0].src.SetText(item.msgids.encode(self.encoding))
							self.listemsgstr[0].trnsl.SetPOReadText(item.msgstrs.encode(self.encoding))
############################### bugfix workaround? ####################						 
							self.transtabview.Select(1)									#################  <----- needed to fix
							self.transtabview.Select(0)									#################  <----- a bug, tab0 will not appear
							self.srctabview.Select(1)									#################  <----- so forcing a tabview update
							self.srctabview.Select(0)
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

				
				############################ TODO: GO TO THE END OF THE TEXT #############################
				#num=self.editorslist[self.postabview.Selection()].translation.CountLines()
				#self.editorslist[self.postabview.Selection()].translation.GoToLine(num)
				
				#txtlen=self.listemsgstr[self.transtabview.Selection()].trnsl.TextLength()
				#print self.listemsgstr[self.transtabview.Selection()].trnsl.OffsetAt(txtlen)
				#self.listemsgstr[self.transtabview.Selection()].trnsl.ScrollToOffset(txtlen-1)
				
#				pointer=self.editorslist[self.postabview.Selection()].translation.PointAt(len(self.editorslist[self.postabview.Selection()].translation.Text()))
#				print pointer[0]
#				self.editorslist[self.postabview.Selection()].translation.MovePenTo(pointer[0][0],pointer[0][1])
#				print self.editorslist[self.postabview.Selection()].translation.PenLocation()
				
			else:
				self.Nichilize()				
				self.listemsgstr.append(trnsltabbox(tabrc2,'msgstr',altece,self))
				self.transtablabels.append(BTab())
				self.transtabview.AddTab(self.listemsgstr[0],self.transtablabels[0])
				################### BUG? ###################
				self.transtabview.Select(1)									#################  <----- needed to fix a bug
				self.transtabview.Select(0)
				#############################################
#				
				self.listemsgid[0].src.SetText("")
			return


		elif msg.what ==  777:
			#Removing B_AVOID_FOCUS flag
			self.SetFlags(0)
			return
		elif msg.what == 963741:
			self.editorslist[self.postabview.Selection()].list.lv.ScrollToSelection()
			#inizi=msg.FindInt32('inizi')
			#fin=msg.FindInt32('fin')
			#indolor=msg.FindInt8('index')
			#self.listemsgid[indolor].src.MakeFocus(True)
			#self.listemsgid[indolor].src.Select(inizi,fin)
			
			
			return
		else:
			BWindow.MessageReceived(self, msg)
			
	def  loadPOfile(self,pathtofile,bounds,pofile):
			########################## TODO ####################################
			##### check if .name.temp.po file exists and is more recent than name.po
			##### check for po compliance with user lang
			
			# add a tab in the editor's tabview
			head, tail = os.path.split(pathtofile)
			startTime = time.time()
			self.editorslist.append(POEditorBBox(bounds,tail,pathtofile,pofile,self.poview,self.encoding))
			executionTime = (time.time() - startTime)
			print('Execution time in seconds: ' + str(executionTime))
			self.tabslabels.append(BTab())
			x=len(self.editorslist)-1
			self.postabview.AddTab(self.editorslist[x], self.tabslabels[x])
			self.postabview.SetFocusTab(x,True)
			self.postabview.Select(x)
			self.infoprogress.SetText(str(self.editorslist[self.postabview.Selection()].pofile.percent_translated()))
			
			
	def QuitRequested(self):
		print "So long and thanks for all the fish"
		BApplication.be_app.PostMessage(B_QUIT_REQUESTED)
		return 1

class HaiPOApp(BApplication.BApplication):

	def __init__(self):
		BApplication.BApplication.__init__(self, "application/x-vnd.HaiPO-Editor")


	def ReadyToRun(self):
		window((100,80,960,720))
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
				
	def MessageReceived(self, msg):
		if msg.what == B_SAVE_REQUESTED:
			e = msg.FindString("name")
			messaggio = BMessage(54173)
			messaggio.AddString("name",e)
			BApplication.be_app.WindowAt(0).PostMessage(messaggio)
			return

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
