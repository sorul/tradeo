#!/bin/bash

# Load the environment variables
source ../config/env/.env.demo

ps -ef | grep $MT_TERMINAL_EXE | grep -v grep | awk '{print $2}' | /usr/bin/sudo xargs kill -9