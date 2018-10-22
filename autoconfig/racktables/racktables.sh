#!/bin/bash
echo -n "Racktables Password: "
read -s Password
./racktables/powerman.py $USER $Password
./racktables/cereal.py $USER $Password
