Xtrac
=====

Introduction 
==
The goal of the Xtrac project is to generate a large unsupervised dataset of images by extracting frames from youtube videos.
This project folder contains all scripts used to generate 

Structure of scripts
==
The pipeline so far consists of a series of python scripts.
The pipeline is folder-based, and assumes following folders in your path:
+ ~/youtube 

+ generate\_queries.py manually generates the json file containing the subjects (eg the CIFAR10 classes), with each subject having multiple queries.
+ download.py Reads the .json 

Dependencies
==
Python 2.7 with matplotlib, PIL
OpenCV 2 with python bindings
ffmpeg (>=1.2.1), needs the "scene" filter
youtube-dl
