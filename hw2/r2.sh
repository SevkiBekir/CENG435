#!/bin/bash


sudo route add -host 10.10.4.2 gw 10.10.4.1
sudo route add -host 10.10.3.1 gw 10.10.3.2

route -n


