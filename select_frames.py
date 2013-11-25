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
        # Load images
        self.shots=[]
        for i,shot in enumerate(self.shots_info):
            self.shots.append([])
            for j,frame in enumerate(shot):
                img=cv2.imread(frame[2])
                self.shots[i].append(img)


    def loadpickle(self):
        tmp=pickle.load(open(join(self.path,'info.pk'),'rb'))
        self.headers_info=tmp['headers']
        self.shots_info=tmp['shots']

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

if __name__=="__main__":
    path='/home/ts2387/frames/Bears/txED4ByjtCU/'
    sel=Selector(path)
