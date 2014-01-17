import numpy as np
from os import listdir,mkdir
from os.path import isfile,isdir,join, expanduser
import sys
import shutil
import scipy.io
import scipy.signal as sps
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import Image
import matplotlib
#import cv2
#import smpl_find_obj
#from smpl_find_obj import init_feature, filter_matches, explore_match
import cPickle as pickle
import datetime
import simplejson as json
import glob
from util import full_extent

#=================
#FILTER PARAMETERS
#=================
MIN_SHOT_LEN=3
MIN_REL_DIFF_FRAMES=0.02
MAX_REL_DIFF_FRAMES=0.4
MIN_BRIGHTNESS=47
MAX_BRIGHTNESS=185

#FILTER IDS
#==========
filter_ids={
'pass':1,
'short':-1,
'bright':-2,
'dark':-3,
'static':-4,
'dynamic':-5,
'unnatural':-6,
}
filter_colors={
'pass':'g',
'short':'r',
'bright':'y',
'dark':'k',
'static':'b',
'dynamic':'r',
'unnatural':'c',
}

#=================
# CLASS SELECTOR
#=================
class Selector:
    def __init__(self,path,vidid):
        """ Selector  """
        #path is folder with frames and info.
        assert(isdir(path) and isfile(join(path,'info.pk')))
        print "%s - Opening selector for %s"%(vidid,path)
        self.path=path
        self.vidid=vidid
        self.filtered=False
        self.loadpickle()
        # determine framesize
        img=mpimg.imread(join(self.path,'frame_%05d.jpeg'%self.shots_info[0][0]['frame_id_jpeg']))
        x,y,c=img.shape
        assert(c==3)
        self.x=x
        self.y=y
        print "{0} - Frames are {1}x{2}".format(self.vidid,self.x,self.y)
        self.shots=[]
        self.brightness=[]
        self.reldiffs=[]
        if self.filtered: # if there has been a filtering before
            print "Loaded filtering results, ready to display or do second filter"
        else:
            global filter_ids
            self.shots_pass=np.ones((self.Nshots))
            self.filter_ids=filter_ids

    def loadimages(self, all=False):
        if len(self.shots)==self.Nshots:
            return False
        # Load images
        print "{0} - Load all shots".format(self.vidid)
        self.shots=[]
        for si,shot in enumerate(self.shots_info):
            if self.shots_pass[si]<=0 and not all:
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
        if isfile(join(self.path,'filtered.json')):
            try:
                self.filtered=True
                tmp=json.load(open(join(self.path,'filtered.json'),'rU'))
                self.shots_pass=np.array(tmp['shots_pass'])
                self.filter_ids=tmp['filter_ids']
            except Exception as e:
                print "Could not load filtered.json file: %s" % str(e)
                self.filtered=False

    def dumpfiltered(self):
        if not self.filtered:
            print "No pickle written, apply filters first"
        else:
            dic={'shots_pass':list(self.shots_pass) , 'filter_ids':filter_ids}
            json.dump(dic, open(join(self.path,'filtered.json'),'w'))

    def showimg(self,i,j):
        plt.imshow(self.shots[i][j])
        plt.show()

    def showgrid(self, frames, tile=(20,30),colors=None):
        assert(len(frames)==tile[0]*tile[1])
        rows=tile[0]
        cols=tile[1]
        fig=plt.figure(figsize=(18,12))
        #fig, axes = plt.subplots(rows,cols)
        #fig.set_size_inches((18,12))
        # http://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python
        #figManager = plt.get_current_fig_manager()
        #figManager.window.showMaximized()
        axes=[]
        for i,fr_id in enumerate(frames):
            if type(fr_id)==np.ndarray:
                fr=fr_id
            elif type(fr_id)==tuple: # shot id, frame id
                fr=self.shots[fr_id[0]][fr_id[1]]
            else:
                fr=None
                axes.append(None)
                continue
            ax=plt.subplot(rows,cols,i+1)
            axes.append(ax)
            plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
            plt.imshow(fr)
            plt.axis('off')
            if i%cols==0:
                print ""
            print ('%d'%i),
        print ""

        if colors is not None:
            print "Coloring background"
            from matplotlib.transforms import Bbox
            from matplotlib.patches import Rectangle
            #axes=axes.flatten()
            colors.insert(0,(0,'')) # add starting point for rectangles
            for ci in range(1,len(colors)):
                istart = colors[ci-1][0]
                iend   = colors[ci][0]
                extent = Bbox.union([full_extent(ax) for ax in axes[istart:iend] if ax is not None])
                #extent=Bbox.union(axes[istart:iend])
                extent = extent.transformed(fig.transFigure.inverted())
                # We can now make the rectangle in figure coords using the "transform" kwarg.
                rect = Rectangle([extent.xmin, extent.ymin], extent.width, extent.height,
                                         facecolor=colors[ci][1] ,edgecolor='none', zorder=-1,
                                                          transform=fig.transFigure)
                fig.patches.append(rect)
        print "Save and show"
        plt.savefig('grid.png')
        plt.show()

    def showshots(self,inds={}):
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

    def show_filter_sample(self,filter_show=['pass'], tile=(16,21),frames_per_shot=3):
        """Show a grid of shots with filter codes in filter_show,
        and number of frames in tile."""
        self.loadimages(all=True)
        #Nframes=tile[0]*tile[1]
        rows_per_filter=[tile[0]/len(filter_show)]*len(filter_show)
        rows_per_filter[0]=tile[0]-np.sum(rows_per_filter[1:])
        Nframes=np.cumsum(rows_per_filter)*tile[1]
        print Nframes
        frames=[]
        colors=[]
        # show results of each filter
        for i,filterid in enumerate(filter_show):
            shot_ids=np.where(sel.shots_pass==filter_ids[filterid])[0]
            np.random.shuffle(shot_ids)
            for sid in shot_ids:
                s=self.shots[sid]
                if s is None:
                    continue
                for frameid in range(0,len(s),len(s)/frames_per_shot):
                    frames.append((sid,frameid))
                    if len(frames)==Nframes[i]: break
                if len(frames)==Nframes[i]: break
            # pad
            if len(frames)<Nframes[i]:
                npad=(Nframes[i]-len(frames))
                print "Pad %d, filter id = %s, npad=%d"%(i,filterid,npad)
                frames.extend([None]*npad)
            # save colors
            colors.append((len(frames),filter_colors[filterid]))
        self.showgrid(frames,tile,colors)
        #self.showgrid(frames,tile,None)
        #return frames

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
                self.shots_pass[shotid]=filter_ids['short']
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
            if np.mean(self.brightness[shotid])<MIN_BRIGHTNESS:
                toodark+=1
                self.shots_pass[shotid]=filter_ids['dark']
            elif np.mean(self.brightness[shotid])>MAX_BRIGHTNESS:
                toobright+=1
                self.shots_pass[shotid]=filter_ids['bright']
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
                self.shots_pass[shotid]=filter_ids['static']
            #elif np.mean(self.reldiffs[shotid])>MAX_REL_DIFF_FRAMES:
                #toodynamic+=1
                #self.shots_pass[shotid]=filter_ids['dynamic']
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

    def filter_faces(self):
        pass

    def filter_frontobject(self):
        pass

    def calcbrightness(self):
        if len(self.brightness)>0:
            return
        self.brightness=[None]*self.Nshots
        # TODO weigh with grayscale-perception weights
        for shotid in xrange(len(self.shots)):
            shot=self.shots[shotid] # np array with shape (shotlen, x,y,3)
            if shot is None: continue
            self.brightness[shotid]=shot.reshape((shot.shape[0],-1)).mean(axis=1)
        self.brightnessmean=[]
        for ar in self.brightness:
            if ar is None:
                self.brightnessmean.append(None)
            else:
                self.brightnessmean.append(np.mean(ar))
        self.brightnessmean=np.array(self.brightnessmean)

    def calcrelativediff(self):
        ## Calculate the difference between two frames and reweigh by the maximum of their brightness
        if len(self.reldiffs)>0:
            return False
        self.reldiffs=[None]*self.Nshots
        for shotid in np.where(self.shots_pass == 1)[0]:
            shot=self.shots[shotid]
            #framediffs=shot[:-1,:,:,:]-shot[1:,:,:,:]
            framediffs=np.abs(shot[:-1,:,:,:].astype('int16') -shot[1:,:,:,:].astype('int16')).astype('uint8')
            self.reldiffs[shotid]=framediffs.reshape((framediffs.shape[0],-1)).mean(axis=1)
            maxbr=np.max(np.vstack((self.brightness[shotid][:-1],self.brightness[shotid][1:])),axis=0)
            self.reldiffs[shotid] /= maxbr

    def apply_filters_write(self):
        """ This is the core function that will apply all cheap filters and
        save the results in internal array self.shots_pass"""
        print "%s - Apply filters"%(self.vidid)
        # clean shots_pass
        self.shots_pass=np.ones((self.Nshots))
        # apply filters
        self.filter_shotlength()
        self.loadimages()
        self.filter_brightness()
        self.filter_framediff()
        self.filter_unnatural()
        self.filter_faces()
        ## SET filtered parameter and print info
        self.filtered=True
        Npass=np.sum(sel.shots_pass==1)
        print "%s - Filter results: %.1f pct of shots passed tests (%d / %d )" % (vidid, 100.*Npass/self.Nshots, Npass, self.Nshots)



if __name__=="__main__" and len(sys.argv)==1:
    # Go through full directory structure and apply cheap filter
    inpath=expanduser('~/cifar32_all')
    for subj in listdir(inpath):
        Sinpath=join(inpath,subj)
        if not isdir(Sinpath):
            continue
        vidlist=listdir(Sinpath)
        print "Enter directory %s with %d videos"%(Sinpath,len(vidlist))
        for vidid in vidlist:
            Vinpath=join(Sinpath,vidid)
            if not isfile(join(Vinpath,'info.pk')):
                print "%s - No infofile found, skipping video"%vidid
                continue
            if isfile(join(Vinpath,'filtered.json')) or isfile(join(Vinpath,'started_filtering')):
                print "%s - Movie is processed or busy, Skipping video"%vidid
                continue
            open(join(Vinpath,'started_filtering'),'wb').close()
            print "%s - cheapfilter video to discard bad shots"%vidid
            sel=Selector(Vinpath,vidid)
            sel.apply_filters_write()
            sel.dumpfiltered()

if __name__=="__main__" and len(sys.argv)==2:
    # Load one specific video
    inpath=expanduser('~/cifar32_all')
    vidid=sys.argv[1]
    vidpath=glob.glob(join(inpath,'*',vidid))
    if (len(vidpath)!=1):
        raise Exception('I found %d vids: %s'%(len(vidpath), str(vidpath)))
    vidpath=vidpath[0]
    print "Load selector for video at %s"%vidpath
    sel=Selector(vidpath,vidid)
    if not sel.filtered:
        sel.apply_filters_write()
        sel.dumpfiltered()
    ## VISUALIZE
    sel.show_filter_sample(['pass','bright','dark','static'])
    # check darks manually
    darks=np.where(sel.shots_pass==filter_ids['dark'])[0]
    inds={}
    for d in darks[:16]:
        inds[d]=range(len(sel.shots[d]))
    sel.showshots(inds)

    #frpath='samplevids/jF5eDmDPUDk/'
    #sel=Selector(frpath)
    #show={}
    #for shot in [5,8,10,11,17,18,19]:
        #show[shot]=range(len(sel.shots[shot]))

