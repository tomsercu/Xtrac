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
        print "Opening selector for %s"%path
        self.path=path
        self.loadpickle()
        # determine framesize
        img=cv2.imread(self.shots_info[0][0][2])
        x,y,c=img.shape
        assert(c==3)
        self.x=x
        self.y=y
        print "Frames are {0}x{1}".format(x,y)
        # Load images
        print "Load images",
        self.shots=[]
        for si,shot in enumerate(self.shots_info):
            nframes=len(shot)
            self.shots.append(np.zeros((nframes,x,y,3))) # allocate for speed
            for fi,frame in enumerate(shot):
                img=cv2.imread(frame[2])
                self.shots[si][fi,:,:,:]=img
                print ".",


    def loadpickle(self):
        tmp=pickle.load(open(join(self.path,'info.pk'),'rb'))
        self.headers_info=tmp['headers']
        self.shots_info=tmp['shots']

    def showimg(self,i,j):
        plt.imshow(self.shots[i][j]);
        plt.show()

    def showgrid(self,inds={}):
        """ inds contains dict with key: shotid, vals: frameids. """
        rows=len(inds)
        cols=max( [len(inds[k]) for k in inds])
        i=0
        plt.figure(figsize=(20,12))
        for si in enumerate(inds):
            print ('shot %d:'%si),
            for fi in inds[si]:
                fr=self.shots[si][fi]
                i+=1
                plt.subplot(rows,cols,i)
                plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
                print ('%d,'%fr),
                plt.imshow(self.d[fr])
                plt.axis('off')
            i=cols*r
            print('')
        plt.show()

    def filter_shotlength(self):
        pass

    def filter_unnatural(self):
        pass

    def filter_brightness(self):
        pass

    def filter_frontobject(self):
        pass

if __name__=="__main__":
    path='/home/tom/frames/Bears/EgcVTNgOkV4/'
    sel=Selector(path)
