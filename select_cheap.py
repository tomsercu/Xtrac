import numpy as np
import os
from os.path import isfile,isdir,join, expanduser
import scipy.io
import scipy.signal as sps
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib
import cv2
import smpl_find_obj
from smpl_find_obj import init_feature, filter_matches, explore_match
import cPickle as pickle
import datetime

class Selector:
    def __init__(self,path):
        """ Selector  """
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
        print "Load images"
        self.shots=[]
        for si,shot in enumerate(self.shots_info):
            nframes=len(shot)
            self.shots.append(np.zeros((nframes,x,y,3),dtype='uint8')) # allocate for speed
            for fi,frame in enumerate(shot):
                img=plt.imread(join(self.path,'frame_%05d.jpeg'%frame[3]))
                self.shots[si][fi,:,:,:]=img
                print ".",
        print ""


    def loadpickle(self):
        tmp=pickle.load(open(join(self.path,'info.pk'),'rb'))
        self.headers_info=tmp['headers']
        self.shots_info=tmp['shots']

    def showimg(self,i,j):
        plt.imshow(self.shots[i][j])
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
                plt.imshow(fr)
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

def show_with_keypts(img,kpts):
    plt.imshow(img)
    #plt.xlim(0,img.shape[0])
    #plt.ylim(0,img.shape[1])
    for kp in kpts:
        plt.plot(kp[0],kp[1],'.',color="#AAFFAA")

def compare_with_keypts(img1,kp1,mkp1, img2,kp2, mkp2):
    fig=plt.figure(figsize=(18,9))
    plt.subplot(121)
    ax1=plt.gca()
    show_with_keypts(img1,mkp1)
    plt.subplot(122)
    ax2=plt.gca()
    show_with_keypts(img2,mkp2)
    ## Draw matching lines
    # from http://stackoverflow.com/questions/17543359/drawing-lines-between-two-plots-in-matplotlib
    transFigure = fig.transFigure.inverted()
    for m1,m2 in zip(mkp1,mkp2):
        coord1 = transFigure.transform(ax1.transData.transform([m1[0],m1[1]]))
        coord2 = transFigure.transform(ax2.transData.transform([m2[0],m2[1]]))
        line = matplotlib.lines.Line2D((coord1[0],coord2[0]),(coord1[1],coord2[1]),transform=fig.transFigure)
        fig.lines.append(line)
    plt.show()

if __name__=="__main__":
    #base='/home/tom/'
    #frpath=join(base,'frames/Lions/jF5eDmDPUDk/')
    frpath='samplevids/jF5eDmDPUDk/'
    sel=Selector(frpath)
    show={}
    for shot in [5,8,10,11,17,18,19]:
        show[shot]=range(len(sel.shots[shot]))
    #sel.showgrid(show)
    #outpath=join(base,'Xtrac/Lions/jF5eDmDPUDk/')

    ## ACTUAL KEYPOINT EXTRACTION
    print "Get keypoint detector and matcher"
    feature_name='sift'
    detector,matcher=init_feature(feature_name)
    img1=sel.shots[10][1]
    img2=sel.shots[10][4]
    kp1,desc1 = detector.detectAndCompute(img1,None)
    kp2,desc2 = detector.detectAndCompute(img2,None)
    print 'img1 - %d features, img2 - %d features' % (len(kp1), len(kp2))
    raw_matches=matcher.knnMatch(desc1,trainDescriptors=desc2, k=2)
    mkp1,mkp2, pairs=filter_matches(kp1,kp2,raw_matches)
    H, status = cv2.findHomography(mkp1, mkp2, cv2.RANSAC, 5.0)
    print '%d / %d  inliers/matched' % (np.sum(status), len(status))
    vis = explore_match('Lions :)', img1, img2, pairs, status, H, convert=cv2.COLOR_RGB2BGR)
    # opens up a window
    cv2.waitKey()
    cv2.destroyAllWindows()


    print "Initialize test stuff"
    plt.ion()
