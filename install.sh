#!/bin/bash
echo "This will download and install several packages and components"
echo
pkgman install pip_python310, 
ret1=$?
echo
pkgman install haiku_pyapi_python310
ret2=$?
echo
pkgman install polib_python310
ret3=$?
echo
pkgman install pyenchant_python310
ret4=$?
echo
pkgman install hunspell
ret5=$?
echo "Please write your language code here (example1: en - example2: it)"
read text
if ! [$text == ""]
then
	pkgman install myspell_$text
	ret6=$?
else
	ret6=1
fi
echo
if [ -e HaiPO.py ]
then
	echo Copying files to system folder...
	[ ! -d /boot/home/config/non-packaged/data/HaiPO2 ] && mkdir /boot/home/config/non-packaged/data/HaiPO2
	cp HaiPO.py /boot/home/config/non-packaged/data/HaiPO2/
	ret7=$?
	if [ -e LauncherApp ]
	then
		echo Adding attributes and Installing LaunchApp
		addattr -t \'MSGG\' BEOS:FILE_TYPES text/x-gettext-translation LauncherApp
		addattr -t mime BEOS:APP_SIG application/x-vnd.dw-LauncherApp LauncherApp
		cp LauncherApp /boot/home/config/non-packaged/data/HaiPO2/
		if [ -f home-config-settings-mime_db-text.zip ]
		then
			echo Installing mime types...
			[ ! -d /boot/home/config/settings/mime_db/text/ ] && mkdir /boot/home/config/settings/mime_db/text
			cp home-config-settings-mime_db-text.zip /boot/home/config/settings/mime_db/text/
			cd /boot/home/config/settings/mime_db/text/
			unzip /boot/home/config/settings/mime_db/text/home-config-settings-mime_db-text.zip
			rm /boot/home/config/settings/mime_db/text/home-config-settings-mime_db-text.zip
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
	cp -R data /boot/home/config/non-packaged/data/HaiPO2
	ret9=$?
else
	echo Missing data directory and images
	ret9=1
fi
echo

if [ $ret2 -lt 1 ]
then
	echo Installation of Bethon OK
else
	echo Installation of Bethon FAILED
fi
if [ $ret3 -lt 1 ]
then
	echo Installation of pip_python OK
else
	echo Installation of pip_python FAILED
fi
if [ $ret4 -lt 1 ] 
then
        echo Installation of polib module OK
else
        echo Installation of polib module FAILED
fi
if [ $ret7 -lt 1 ] 
then
        echo Installation of HaiPO.py to system folder OK
else
        echo Installation of HaiPO.py to system folder FAILED
fi
if [ $ret8 -lt 1 ] 
then
        echo Installation to Deskbar menu OK
else
        echo Installation to Deskbar menu FAILED
fi
if [ $ret9 -lt 1 ] 
then
        echo Installation of app data to system folder OK
else
        echo Installation of app data to system folder FAILED
fi
