#!/usr/bin/env bash

# Load the environment variables
source ../config/env/.env.demo

# With this we choose the wine profile (folder)
export WINEPREFIX=$WINE_HOME
DISPLAY=:10.0

# 30 second delay to give time to the graphical environment
sleep 30

# Run the Wine program in the background and redirect the output
xvfb-run -a $WINE_PATH $MT_TERMINAL_EXE
