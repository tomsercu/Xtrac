import numpy as np
import os
from os.path import isfile,isdir,join
import scipy.io
import scipy.signal as sps
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
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
        img=mpimg.imread(join(self.path,'frame_%05d.jpeg'%self.shots_info[0][0][3]))
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
            self.shots.append(np.zeros((nframes,x,y,3),dtype='uint8')) # allocate for speed
            for fi,frame in enumerate(shot):
                img=plt.imread(join(self.path,'frame_%05d.jpeg'%frame[3]))
                self.shots[si][fi,:,:,:]=img
                print ".",


    def loadpickle(self):
        tmp=pickle.load(open(join(self.path,'info.pk'),'rb'))
        self.headers_info=tmp['headers']
        self.shots_info=tmp['shots']

    def showimg(self,i,j):
        plt.imshow(self.shots[i][j],origin='lower');
        plt.show()

    def showgrid(self,inds={}):
        """ inds contains dict with key: shotid, vals: frameids. """
        rows=len(inds)
        cols=max( [len(inds[k]) for k in inds])
        i=0
        r=0
        plt.figure(figsize=(20,12))
        for si in inds:
            r+=1
            print ('shot %d, shot length %d, showing %d frames'%(si,len(self.shots[si]),len(inds[si]))),
            for fi in inds[si]:
                fr=self.shots[si][fi,:,:,:]
                i+=1
                plt.subplot(rows,cols,i)
                plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
                print ('%d,'%fi),
                plt.imshow(fr,origin='lower')
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
    #base='/home/tom/'
    #frpath=join(base,'frames/Lions/jF5eDmDPUDk/')
    frpath='samples/jF5eDmDPUDk/'
    sel=Selector(frpath)
    #show={4:range(8), 5:range(5), 6:range(8)}
    show={4:range(8), 5:range(5), 6:range(8), 7:range(9), 8:range(8), 9:range(9), 10:range(5), 11:range(5)}
    sel.showgrid(show)
    #outpath=join(base,'Xtrac/Lions/jF5eDmDPUDk/')
    # bullshit test
