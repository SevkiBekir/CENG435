#!/bin/bash

sudo route add -host 10.10.1.1 gw 10.10.1.2

sudo route add -host 10.10.2.2 gw 10.10.2.1

route -n


