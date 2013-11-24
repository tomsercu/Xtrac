import numpy as np
import os
from os.path import isfile,isdir,join
import scipy.io
import scipy.signal as sps
import matplotlib.pyplot as plt
import cv2
import cPickle as pickle
import datetime

class Selector:
    def __init__(self,path):
        #path is folder with frames and info.
        assert(isdir(path) and isfile(join(path,'info.pk')))
        self.path=path
        self.loadpickle()
        self.data=


    def loadpickle(self):
        tmp=pickle.load(open(join(self.path,'info.pk'),'rb'))
        self.headers=tmp['headers']
        self.shotinfo=tmp['shots']

    def showimg(self,sid,fid):
        pass

    def filter_shotlength(self):
        pass

    def filter_unnatural(self):
        pass

    def filter_brightness(self):
        pass

    def filter_frontobject(self):
        pass
