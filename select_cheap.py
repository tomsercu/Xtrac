import numpy as np
from os import listdir,mkdir
from os.path import isfile,isdir,join, expanduser
import shutil
import scipy.io
import scipy.signal as sps
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import Image
import matplotlib
import cv2
import smpl_find_obj
from smpl_find_obj import init_feature, filter_matches, explore_match
import cPickle as pickle
import datetime

#=================
#FILTER PARAMETERS
#=================
MIN_SHOT_LEN=3
MIN_REL_DIFF_FRAMES=0.02
MAX_REL_DIFF_FRAMES=0.4
MIN_BRIGHTNESS=10
MAX_BRIGHTNESS=200

#=================
# CLASS SELECTOR
#=================
class Selector:
    def __init__(self,path,vidid):
        """ Selector  """
        #path is folder with frames and info.
        assert(isdir(path) and isfile(join(path,'info.pk')))
        print "Opening selector for %s"%path
        self.path=path
        self.vidid=vidid
        self.loadpickle()
        # determine framesize
        img=mpimg.imread(join(self.path,'frame_%05d.jpeg'%self.shots_info[0][0]['frame_id_jpeg']))
        x,y,c=img.shape
        assert(c==3)
        self.x=x
        self.y=y
        print "{0} - Frames are {1}x{2}".format(self.vidid,x,y)
        self.shots=[]
        self.brightness=[]
        self.reldiffs=[]
        self.shots_pass=np.ones((self.Nshots))

    def loadimages(self):
        if len(self.shots)==self.Nshots:
            return False
        # Load images
        print "{0} - Load all shots".format(self.vidid)
        self.shots=[]
        for si,shot in enumerate(self.shots_info):
            if self.shots_pass[si]==0:
                self.shots.append(None)
                continue
            nframes=len(shot)
            self.shots.append(np.zeros((nframes,self.x,self.y,3),dtype='uint8')) # allocate for speed
            for fi,frame in enumerate(shot):
                img=plt.imread(join(self.path,'frame_%05d.jpeg'%frame['frame_id_jpeg']))
                self.shots[si][fi,:,:,:]=img
            #print ".",
        #print ""
        return True


    def loadpickle(self):
        self.shots_info=pickle.load(open(join(self.path,'info.pk'),'rb'))
        self.Nshots=len(self.shots_info)

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
        nogo=0
        passed=0
        failed=0
        for shotid in xrange(self.Nshots):
            if not self.shots_pass[shotid]==1:
                nogo+=1
                continue
            if len(self.shots_info[shotid])<MIN_SHOT_LEN:
                failed+=1
                self.shots_pass[shotid]=0
            else:
                passed+=1
        print "%s - Filter on shotlength: %.1f pct of shots passed (%d/%d, nogo=%d)"%(self.vidid, 100.0*passed/(passed+failed), passed,passed+failed, nogo)


    def filter_brightness(self):
        self.loadimages() # load images if not laoded yet
        self.calcbrightness()
        nogo=0
        passed=0
        toobright=0
        toodark=0
        for shotid in xrange(self.Nshots):
            if not self.shots_pass[shotid]==1:
                nogo+=1
                continue
            if np.min(self.brightness[shotid])<MIN_BRIGHTNESS:
                toodark+=1
                self.shots_pass[shotid]=0
            elif np.max(self.brightness[shotid])>MAX_BRIGHTNESS:
                toobright+=1
                self.shots_pass[shotid]=0
            else:
                passed+=1
        print "%s - Filter on brightness: %.1f pct of shots passed (%d/%d), %.1f too bright, %.1f too dark"%\
                (self.vidid, 100.0*passed/(passed+toobright+toodark), passed,passed+toobright+toodark, 100.0*toobright/(passed+toobright+toodark), 100.0*toodark/(passed+toobright+toodark))

    def filter_framediff(self):
        self.calcrelativediff()
        nogo=0
        passed=0
        toostatic=0
        toodynamic=0
        for shotid in xrange(self.Nshots):
            if not self.shots_pass[shotid]==1:
                nogo+=1
                continue
            if np.mean(self.reldiffs[shotid])<MIN_REL_DIFF_FRAMES:
                toostatic+=1
                self.shots_pass[shotid]=0
            elif np.mean(self.reldiffs[shotid])>MAX_REL_DIFF_FRAMES:
                toodynamic+=1
                self.shots_pass[shotid]=0
            else:
                passed+=1
        Nproc=self.Nshots-nogo
        print "%s - Filter on frame difference: %.1f pct of shots passed (%d/%d), %.1f too static, %.1f too dynamic"%\
                (self.vidid, 100.0*passed/Nproc, passed,Nproc, 100.0*toostatic/Nproc, 100.0*toodynamic/Nproc)

    def filter_unnatural(self):
        for shotid in xrange(self.Nshots):
            if not self.shots_pass[shotid]==1:
                continue
        pass #TODO

    def filter_frontobject(self):
        pass

    def calcbrightness(self):
        if len(self.brightness)>0:
            return
        self.brightness=[None]*self.Nshots
        # TODO weigh with grayscale-perception weights
        for shotid in np.where(self.shots_pass)[0]:
            shot=self.shots[shotid] # np array with shape (shotlen, x,y,3)
            self.brightness[shotid]=shot.reshape((shot.shape[0],-1)).mean(axis=1)

    def calcrelativediff(self):
        ## Calculate the difference between two frames and reweigh by the maximum of their brightness
        if len(self.reldiffs)>0:
            return False
        self.reldiffs=[None]*self.Nshots
        for shotid in np.where(self.shots_pass)[0]:
            shot=self.shots[shotid]
            #framediffs=shot[:-1,:,:,:]-shot[1:,:,:,:]
            framediffs=np.abs(shot[:-1,:,:,:].astype('int16') -shot[1:,:,:,:].astype('int16')).astype('uint8')
            self.reldiffs[shotid]=framediffs.reshape((framediffs.shape[0],-1)).mean(axis=1)
            maxbr=np.max(np.vstack((self.brightness[shotid][:-1],self.brightness[shotid][1:])),axis=0)
            self.reldiffs[shotid] /= maxbr

    def apply_filters_write(self,outdir):
        """ This is the core function that will apply all cheap filters and write
        the result to outdir, subdivided in folders per shot"""
        print "%s - Apply filters and export selected shots to %s"%(self.vidid,outdir)
        self.filter_shotlength()
        self.loadimages()
        self.filter_brightness()
        self.filter_framediff()
        ### SHOTS THAT PASSED
        print "%s - Export selected shots to %s"%(self.vidid,outdir)
        for shotid in xrange(self.Nshots):
            if not self.shots_pass[shotid]==1:
                print "X",
                continue
            for fid,frame in enumerate(self.shots_info[shotid]):
                fn=join(self.path,'frame_%05d.jpeg'%frame['frame_id_jpeg'])
                shutil.copy(fn,join(outdir,'shot_%04d_fr_%03d.jpeg'%(shotid,fid)))
            print ".",
        print ""



if __name__=="__main__":
    inpath=expanduser('~/cifar32_all')
    outpath=expanduser('~/cifar32_selected')
    for subj in listdir(inpath):
        Sinpath=join(inpath,subj)
        Soutpath=join(outpath,subj)
        if not isdir(Sinpath):
            continue
        vidlist=listdir(Sinpath)
        if not isdir(Soutpath) and len(vidlist)>0:
            print "Make directory %s"%Soutpath
            mkdir(Soutpath)
        print "Enter directory %s with %d videos"%(Sinpath,len(vidlist))
        for vidid in vidlist:
            Vinpath=join(Sinpath,vidid)
            if not isfile(join(Vinpath,'info.pk')):
                print "%s - No infofile found, skipping video"%vidid
                continue
            Voutpath=join(Soutpath,vidid)
            if isdir(Voutpath):
                if isfile(join(Voutpath,'started')):
                    print "%s - Movie is processed or busy, Skipping video"%vidid
                    continue
            else:
                mkdir(Voutpath)
            open(join(Voutpath,'started'),'wb').close()
            print "%s - cheapfilter video to discard bad shots"%vidid
            sel=Selector(Vinpath,vidid)
            sel.apply_filters_write(Voutpath)


    #frpath='samplevids/jF5eDmDPUDk/'
    #sel=Selector(frpath)
    #show={}
    #for shot in [5,8,10,11,17,18,19]:
        #show[shot]=range(len(sel.shots[shot]))

