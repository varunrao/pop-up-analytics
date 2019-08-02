#!/bin/bash

set -e

while [ ! -f /etc/livy/conf/livy.conf ]
do
    sleep 5
done

# Enable Livy
sudo sed -i 's/^# livy.repl.enable-hive-context/livy.repl.enable-hive-context true/' /etc/livy/conf/livy.conf

# Restart Livy
sudo restart livy-server

