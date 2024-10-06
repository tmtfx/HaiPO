#!/bin/bash
echo "This will download and install several packages and components"
echo
pkgman install pip_python310 
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
	if [ -e LaunchHaiPO.zip ]
	then
		#echo Adding attributes and Installing LaunchApp
		#addattr -t \'MSGG\' BEOS:FILE_TYPES text/x-gettext-translation LauncherApp
		#addattr -t mime BEOS:APP_SIG application/x-vnd.dw-LauncherApp LauncherApp
		unzip LaunchHaiPO.zip
		cp LauncherApp /boot/home/config/non-packaged/data/HaiPO2/
		mv LaunchHaiPO /boot/home/config/non-packaged/bin
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

pkgman install babel_python310
ret10=$?
pkgman install cmake / cmake_86
ret11=$?
pkgman install lxml_python310
ret12=$?
pkgman install sphinx_python310
ret13=$?
pkgman install gettext
ret14=$?

pip3 install rapidfuzz
ret15=$?
if [ ! $ret15 -lt 1 ]
then
	tar -xvzf rapidfuzz-3.9.7.tar.gz
	cd rapidfuzz-3.9.7
	python3 setup.py install
	ret15=$?
	cd -
fi
pip install scikit-build
ret16=$?
patch /boot/system/non-packaged/lib/python3.10/site-packages/skbuild/platform_specifics/platform_factory.py skbuild.patch
ret17=$?
pip install translate-toolkit
ret18=$?
if [ -e Levenshtein-0.25.1.tar.gz]; then
	tar -xvzf Levenshtein-0.25.1.tar.gz
	cd Levenshtein-0.25.1
	python3 setup.py install
	ret19=$?
	cd -
fi

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
if [ $ret3 -lt 1 ] 
then
        echo "Installation of polib module OK"
else
        echo "Installation of polib module FAILED"
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
if [ $ret11 -lt 1 ]
then
	echo "Installation of cmake OK"
else
	echo "Installation of cmake FAILED"
fi
if [ $ret12 -lt 1 ]
then
	echo "Installation of lxml for python310 OK"
else
	echo "Installation of lxml for python310 FAILED"
fi
if [ $ret13 -lt 1 ]
then
	echo "Installation of sphinx for python310 OK"
else
	echo "Installation of sphinx for python310 FAILED"
fi
if [ $ret14 -lt 1 ]
then
	echo "Installation of gettext OK"
else
	echo "Installation of gettext FAILED"
fi
if [ $ret15 -lt 1 ]
then
	echo "Installation of rapidfuzz for python OK"
else
	echo "Installation of rapidfuzz for python FAILED"
fi
if [ $ret16 -lt 1 ]
then
	echo "Installation of scikit-build for python OK"
else
	echo "Installation of scikit-build for python FAILED"
fi
if [ $ret17 -lt 1 ]
then
	echo "Installation of patch applied for scikit-build OK"
else
	echo "Installation of patch applied for scikit-build FAILED"
fi
if [ $ret18 -lt 1 ]
then
	echo "Installation of translate-toolkit for python OK"
else
	echo "Installation of translate-toolkit for python FAILED"
fi
if [ $ret19 -lt 1 ]
then
	echo "Installation of Levenshtein for python OK"
else
	echo "Installation of Levenshtein for python FAILED"
fi

