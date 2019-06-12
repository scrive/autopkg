#!/usr/bin/env bash

##############################################################################
# This script is designed to return the 'version number' of GDFS.            #
# Will return 'version number' or 'not installed'                            #
##############################################################################
RESULT="Not Installed"

if [ -d "/Applications/Google Drive File Stream.app" ]; then
  RESULT=$(/usr/bin/defaults read /Applications/"Google Drive File Stream.app"/Contents/Info.plist CFBundleVersion)
fi

/bin/echo "<result>$RESULT</result>"
