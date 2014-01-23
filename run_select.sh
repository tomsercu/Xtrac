#!/bin/bash
stdbuf -oL /usr/local/pkg/python/2.7/bin/python select_cheap.py 2>&1 | tee ./log_selection/$1
