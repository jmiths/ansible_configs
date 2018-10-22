#!/bin/sh
#
# Copyright (C) 2013 Canonical Ltd
# Author: Gunnar Hjalmarsson <gunnarhj@ubuntu.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3 of the License.
#
# See http://www.gnu.org/copyleft/gpl.html the full text of the license.

# This script is run via autostart at the launch of a guest session.

export TEXTDOMAINDIR=/usr/share/locale-langpack
export TEXTDOMAIN=lightdm

# disable screen locking
gsettings set org.gnome.desktop.lockdown disable-lock-screen true

# info dialog about the temporary nature of a guest session
dialog_content () {
	TITLE=$(gettext 'IMPORTANT INFORMATION FOR GUEST USERS!')
	TEXT=$(gettext 'Please do not save important files to this laptop!\nGuest sessions do not keep their files and all data will be deleted as soon as you log out.\n\nIf you need access to your home directory, you can SSH through Tux.')
	para2=$(gettext 'To access your home directory, you can SSH through Tux.')
	test -w /var/guest-data && TEXT="$TEXT\n\n$para2"
}
test -f "$HOME"/.skip-guest-warning-dialog || {
	if [ "$KDE_FULL_SESSION" = true ] && [ -x /usr/bin/kdialog ]; then
		dialog_content
		TEXT_FILE="$HOME"/.guest-session-kdialog
		echo -n "$TEXT" > $TEXT_FILE
		{
			# Sleep to wait for the the info dialog to start.
			# This way the window will likely become focused.
			sleep $DIALOG_SLEEP
			kdialog --title "$TITLE" --textbox $TEXT_FILE 450 250
			rm -f $TEXT_FILE
		} &
	elif [ -x /usr/bin/zenity ]; then
		dialog_content
		{
			# Sleep to wait for the the info dialog to start.
			# This way the window will likely become focused.
			sleep $DIALOG_SLEEP
			zenity --warning --no-wrap --title="$TITLE" --text="$TEXT"
		} &
	fi
}

# run possible local startup commands
test -f /etc/guest-session/auto.sh && . /etc/guest-session/auto.sh
