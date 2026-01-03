#!/bin/bash
echo "This will download and install several packages and components"
echo
pkgman install pip_python310 
ret1=$?
echo
pkgman install haiku_pyapi_python310
ret2=$?
echo
pkgman install pyenchant_python310
ret4=$?
echo
pkgman install hunspell
ret5=$?
echo "Please write your language code here (example1: en - example2: it)"
read text
if ! [ -z "$text" ]
then
	pkgman install myspell_$text
	ret6=$?
else
	ret6=1
fi
echo
if [ -e HaiPO.py ]
then
	if [ -e data/HaiPO.hvif ]; then
		addattr -t \'VICN\' BEOS:ICON -f data/HaiPO.hvif HaiPO.py
	fi
	echo Copying files to system folder...
	[ ! -d /boot/home/config/non-packaged/data/HaiPO2 ] && mkdir /boot/home/config/non-packaged/data/HaiPO2
	cp HaiPO.py /boot/home/config/non-packaged/data/HaiPO2/
	ret7=$?
	if [ -e user_LaunchHaiPO.zip ]
	then
		#echo Adding attributes and Installing LaunchApp
		#addattr -t \'MSGG\' BEOS:FILE_TYPES text/x-gettext-translation LauncherApp
		#addattr -t mime BEOS:APP_SIG application/x-vnd.dw-LauncherApp LauncherApp
		unzip user_LaunchHaiPO.zip
		cp LaunchHaiPO /boot/home/config/non-packaged/data/HaiPO2/
		mv LaunchHaiPO /boot/home/config/non-packaged/bin
		if [ -f x-gettext-translation.zip ]
		then
			echo Installing mime types...
			[ ! -d /boot/home/config/settings/mime_db/ ] && mkdir /boot/home/config/settings/mime_db/
			cp x-gettext-translation.zip /boot/home/config/settings/mime_db/
			cd /boot/home/config/settings/mime_db/
			unzip /boot/home/config/settings/mime_db/x-gettext-translation.zip
			rm /boot/home/config/settings/mime_db/x-gettext-translation.zip
			cd -
		fi
	fi
	[ ! -f /boot/home/config/non-packaged/bin/HaiPO ] && ln -s /boot/home/config/non-packaged/data/HaiPO2/HaiPO.py /boot/home/config/non-packaged/bin/HaiPO
	[ ! -d /boot/home/config/settings/deskbar/menu/Applications/ ] && mkdir /boot/home/config/settings/deskbar/menu/Applications/
	[ ! -f /boot/home/config/settings/deskbar/menu/Applications/HaiPO ] && ln -s /boot/home/config/non-packaged/bin/HaiPO /boot/home/config/settings/deskbar/menu/Applications/HaiPO
	ret8=$?
else
	echo "Main program missing"
	ret7=1
	ret8=1
fi
echo
DIRECTORY=`pwd`/data
if [ -d $DIRECTORY  ]
then
	cp -R data/locale /boot/home/config/non-packaged/data/HaiPO2
	cp data/HaiPO.png /boot/home/config/non-packaged/data/HaiPO2
	cp data/plural_forms.txt /boot/home/config/non-packaged/data/HaiPO2
	cp -R data/help /boot/home/config/non-packaged/data/HaiPO2
	cp -a translate /boot/home/config/non-packaged/data/HaiPO2
	cp -a deep_translator /boot/home/config/non-packaged/data/HaiPO2
	cp -a Levenshtein /boot/home/config/non-packaged/data/HaiPO2
	cp -a rapidfuzz /boot/home/config/non-packaged/data/HaiPO2
	cp -a polib /boot/home/config/non-packaged/data/HaiPO2
	ret9=$?
else
	echo Missing data directory and images
	ret9=1
fi
echo

pkgman install babel_python310
ret10=$?
pkgman install lxml_python310
ret12=$?
pkgman install gettext
ret14=$?


if [ $ret1 -lt 1 ]
then
	echo "Installation of pip for python310 OK"
else
	echo "Installation of pip for python310 FAILED"
fi
if [ $ret2 -lt 1 ]
then
	echo "Installation of Haiku PyAPI for python310 OK"
else
	echo "Installation of Haiku PyAPI for python310 FAILED"
fi
if [ $ret4 -lt 1 ] 
then
        echo "Installation of pyenchant for python310 OK"
else
        echo "Installation of pyenchant for python310 FAILED"
fi
if [ $ret5 -lt 1 ] 
then
        echo "Installation of hunspell OK"
else
        echo "Installation of hunspell FAILED"
fi
if [ $ret6 -lt 1 ] 
then
        echo "Installation of myspell dictionary OK"
else
        echo "Installation of myspell dictionary FAILED"
fi
if [ $ret7 -lt 1 ] 
then
        echo "Installation of HaiPO.py to user non-packaged data folder OK"
else
        echo "Installation of HaiPO.py to user non-packaged data folder FAILED"
fi
if [ $ret8 -lt 1 ] 
then
        echo "Installation to Deskbar menu OK"
else
        echo "Installation to Deskbar menu FAILED"
fi
if [ $ret9 -lt 1 ] 
then
        echo "Installation of app data to user non-packaged data folder OK"
else
        echo "Installation of app data to user non-packaged data folder FAILED"
fi
if [ $ret10 -lt 1 ]
then
	echo "Installation of babel for python310 OK"
else
	echo "Installation of babel for python310 FAILED"
fi
if [ $ret12 -lt 1 ]
then
	echo "Installation of lxml for python310 OK"
else
	echo "Installation of lxml for python310 FAILED"
fi
if [ $ret14 -lt 1 ]
then
	echo "Installation of gettext OK"
else
	echo "Installation of gettext FAILED"
fi

