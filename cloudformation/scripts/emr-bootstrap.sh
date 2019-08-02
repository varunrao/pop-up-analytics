#!/bin/bash
sudo pip install boto3;
sudo pip install jip;
sudo pip install mleap;
(cd /home/hadoop && /usr/local/bin/jip install ml.combust.mleap:mleap-spark_2.11:0.9.0)
