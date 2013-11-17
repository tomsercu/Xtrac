#!/bin/bash
python transform_frames_shots.py 2>&1 | tee ./log_extraction/$1
