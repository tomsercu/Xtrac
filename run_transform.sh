#!/bin/bash
stdbuf -oL python extract_frames_ffmpeg.py 2>&1 | tee ./log_extraction/$1
