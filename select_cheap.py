import numpy as np
import os
from os import listdir,mkdir
from os.path import isfile,isdir,join, expanduser, split
import random
import sys
import shutil
import scipy.io
import scipy.signal as sps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import Image
#import cv2
#import smpl_find_obj
#from smpl_find_obj import init_feature, filter_matches, explore_match
import datetime
import simplejson as json
import glob
import time
from util import full_extent
import  conf
import subprocess
import traceback
import pdb


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
    def __init__(self,subj,vidid):
        """ Selector  """
        print "%s - Opening selector for %s"%(vidid, vidid)
        #path is folder with frames and info.
        path = join(conf.path.thumbs, subj, vidid)
        self.path=path
        assert(isdir(path) and isfile(join(path, conf.fn.shots)))
        self.outpath = join(conf.path.frames, subj, vidid)
        self.subj = subj
        self.vidid=vidid
        self.thumb_fn = join(self.path,
                              conf.thumbs.fn.format(vidid = vidid,num = '%06d'))
        self.filtered=False
        self.load_shots_info()
        # determine framesize
        img=mpimg.imread(self.thumb_fn % self.shots_info[0][0]['thumb_n'])
        x,y,c=img.shape
        assert(c==3)
        self.x=x
        self.y=y
        print "{0} - Frames are {1}x{2}".format(self.vidid,self.x,self.y)
        self.shots = []
        self.gray = []
        self.brightness=[]
        self.reldiffs=[]
        #if self.filtered: # if there has been a filtering before
            #print "Loaded filtering results, ready to display or do second filter"
        #else:
        global filter_ids
        self.shots_pass=np.ones((self.Nshots))
        self.Npass = 0
        self.filter_ids=filter_ids

    def pr(self, msg):
        print "%s - %s" % (self.vidid, msg)

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
                img=plt.imread(self.thumb_fn % frame['thumb_n'])
                self.shots[si][fi,:,:,:]=img
            #print ".",
        #print ""
        return True

    def load_shots_info(self):
        self.shots_info=json.load(open(join(self.path, conf.fn.shots),'rU'))
        self.Nshots=len(self.shots_info)
        #if isfile(join(self.path,'filtered.json')):
            #try:
                #self.filtered=True
                #tmp=json.load(open(join(self.path,'filtered.json'),'rU'))
                #self.shots_pass=np.array(tmp['shots_pass'])
                #self.filter_ids=tmp['filter_ids']
            #except Exception as e:
                #print "Could not load filtered.json file: %s" % str(e)
                #self.filtered=False

    def save_results(self):
        if not self.filtered:
            print "Not filtered yet: nothing written, apply filters first"
            return
        # TOdo update for per-thumb filter
        dic={'shots_pass':list(self.shots_pass) , 'filter_ids':filter_ids}
        json.dump(dic, open(join(self.path,'filtered.json'),'w'))
        # TODO save grid to visualize different filters results
        print ("%s - Dump filters overviews: " % self.vidid),
        for f in filter_ids:
            if f == 'short': continue # not worth showing
            fn = join(self.path, 'filter_%s.jpg' % f)
            self.show_filter_sample(f, fn)
            print ("%s, " % f),
        print ""

    def ffmpeg(self):
        #logfn = join(self.outpath, conf.fn.ffmpeg_log)
        vidid = self.vidid
        vidpath = join(conf.path.video, self.subj, self.vidid+'.mp4')
        if not isfile(vidpath): vidpath = join(conf.path.video, self.subj, self.vidid+'.flv')
        cmd  = ('ffmpeg -i "{vidpath}" '
                #'-vf select=\'gte(n\,{nstart})*lte(n\,{nstop})\','
                '-vf select=\'{filt}\','
                'scale={w}:{h} -vsync \'vfr\' '
                '-f image2 "%s"')
        cmd = cmd % join(self.outpath, conf.frames.fn)
        #print cmd
        shotinfo = [(None, None) for shot in xrange(self.Nshots)]
        Nframes = 0
        filt = []
        for shot in xrange(self.Nshots):
            if not self.shots_pass[shot]==1:
                continue
            nstart = self.shots_info[shot][0]['n']
            try: nstop  = self.shots_info[shot+1][0]['n'] - 1
            except: nstop = self.shots_info[shot][-1]['n'] # last shot
            delta = nstop - nstart +1
            filt.append('gte(n\,{nstart})*lte(n\,{nstop})'.format(**locals()))
            shotinfo[shot] = (Nframes + 1, Nframes + delta)
            Nframes += delta
        filt = '+'.join(filt)
        w = conf.frames.w
        h = conf.frames.h
        cmd_now = cmd.format(**locals())
        # RUN FFMPEG, in SILENCE
        tic = time.time()
        result = subprocess.call(cmd_now, shell=True, stdout = open(os.devnull, 'wb'), stderr = open(os.devnull, 'wb'))
        tac = time.time()
        if (result==0):
            #self.pr("shot %d - %d frames extracted from %d to %d. Elapsed time %.2f sec"\
                    #% (shot, nstop-nstart, nstart, nstop, tac-tic))
            #shotinfo[shot] = (nstart, nstop)
            self.pr('Succesfully extracted %d shots into %d frames. Elapsed time %.2f sec'\
                    % (self.Npass, Nframes, tac-tic))
        else:
            #self.pr("ffmpeg returned unsuccesful: shot %d frames from %d to %d." % (shot, nstart, nstop))
            self.pr("ffmpeg returned unsuccesful")
            self.pr("return code = %d"%result)
        with open(join(self.outpath,'command.log'),'w') as fh:
            fh.write(cmd_now + '\n')
        print "%s - Wrote command to %s."%(vidid,join(self.outpath,'command.log'))
            #Nfails +=1
        # Write overview json file, with nstart and nstop in original video
        with open( join(self.outpath, conf.fn.shots), 'w') as fh:
            json.dump(shotinfo, fh)
        return result

    def showimg(self,i,j):
        plt.imshow(self.shots[i][j])
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

    def showgrid(self, frames, tile=(20,30), fn = None, title = None, colors=None):
        rows=tile[0]
        cols=tile[1]
        fig=plt.figure(figsize=(18,12))
        #fig, axes = plt.subplots(rows,cols)
        #fig.set_size_inches((18,12))
        # http://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python
        #figManager = plt.get_current_fig_manager()
        #figManager.window.showMaximized()
        axes=[]
        if title is not None:
            plt.suptitle(title)
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
            #if i%cols==0:
                #print ""
            #print ('%d'%i),
        #print ""
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
        #print "Save or show"
        if fn is not None:
            plt.savefig(fn)
        else:
            plt.show()
        plt.close(fig)

    def show_filter_sample(self,filt='pass', fn = None, tile=(16,20),frames_per_shot=5 ):
        """Show a grid of shots with frames that have been filtered out
        by filter."""
        frames=[]
        Nshots = tile[0] * (tile[1] / frames_per_shot)
        # show results of each filter
        shot_ids=np.where(self.shots_pass==filter_ids[filt])[0]
        np.random.shuffle(shot_ids)
        #print "Filter %s: %s" % (filt, str(shot_ids))
        for sid in shot_ids[:Nshots]:
            s=self.shots[sid]
            if s is None: # img not loaded
                print "Want to show shot id %d but it's not loaded :( this shouldn't really happen" % sid
                continue
            rate = max([1, len(s)/frames_per_shot])
            for i in range(frames_per_shot):
                frameid = rate * i
                #print "frameid %d of %d total in shot %d" % (frameid, len(s), sid)
                if frameid < len(s):
                    frames.append((sid,frameid))
                else:
                    frames.append(None)
        self.showgrid(frames, tile, fn, "Filter = %s"%filt)

    def filter_shotlength(self):
        nogo= 0
        passed=0
        failed=0
        for shotid in xrange(self.Nshots):
            if not self.shots_pass[shotid]==1:
                nogo+=1
                continue
            if len(self.shots_info[shotid])<conf.filt.min_shot_len:
                failed+=1
                self.shots_pass[shotid]=filter_ids['short']
            else:
                passed+=1
        print "%s - Filter on shotlength: %.1f pct of shots passed (%d/%d, nogo=%d)"%(self.vidid, 100.0*passed/(passed+failed), passed,passed+failed, nogo)

    def filter_brightness(self):
        self.loadimages() # load images if not laoded yet
        self.calcbrightness() # weighted grayscales
        nogo=0
        passed=0
        toobright=0
        toodark=0
        for shotid in xrange(self.Nshots):
            #already filtered
            #----------------------------
            if not self.shots_pass[shotid]==1:
                nogo+=1
                continue
            # too many dark pixels
            shot = self.gray[shotid]
            darkpixels = (shot < conf.filt.min_brightness).sum(axis = 2).sum(axis = 1)
            if np.sum(darkpixels > conf.filt.max_dark_area * self.x * self.y) > 0:# now: if any thumb is too dark -> discard
                toodark+=1
                self.shots_pass[shotid]=filter_ids['dark']
                continue
            # too many bright
            brightpixels = (shot > conf.filt.max_brightness).sum(axis = 2).sum(axis = 1)
            if np.sum(brightpixels > conf.filt.max_bright_area * self.x * self.y) > 0:
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
            if np.mean(self.reldiffs[shotid])<conf.filt.min_rel_diff_frames:
                toostatic+=1
                self.shots_pass[shotid]=filter_ids['static']
            #elif np.mean(self.reldiffs[shotid])>conf.filt.max_rel_diff_frames:
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
        if len(self.gray)>0:
            return
        self.gray=[None]*self.Nshots
        self.brightness = [None] * self.Nshots
        for shotid in xrange(len(self.shots)):
            if self.shots[shotid] is None: continue
            shot=self.shots[shotid].copy() # np array with shape (shotlen, x,y,3)
            # weight with grayscale-perception before averaging
            shot[:,:,:,0] *= 0.2126 # R
            shot[:,:,:,1] *= 0.7152 # G
            shot[:,:,:,2] *= 0.0722 # B
            self.gray[shotid] = shot.sum(axis=3)
            self.brightness[shotid] = self.gray[shotid].mean(axis = 2).mean(axis = 1)

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
        self.Npass=np.sum(sel.shots_pass==1)
        print "%s - Filter results: %.1f pct of shots passed tests (%d / %d )" \
                % (vidid, 100.*self.Npass/self.Nshots, self.Npass, self.Nshots)



if __name__=="__main__" and len(sys.argv)==1:
    # Go through full directory structure and apply cheap filter
    inpath = conf.path.thumbs
    stack = []
    for subj in listdir(inpath):
        Sinpath=join(inpath,subj)
        if not isdir(Sinpath):
            continue
        Soutpath=join(conf.path.frames, subj)
        if not isdir(Soutpath):
            mkdir(Soutpath)
        vidlist=listdir(Sinpath)
        print "Enter directory %s with %d videos"%(Sinpath,len(vidlist))
        for vidid in vidlist:
            Vinpath = join(Sinpath,vidid)
            Voutpath= join(conf.path.frames, subj, vidid)
            stack.append((subj, vidid, Vinpath, Voutpath))
    random.shuffle(stack)
    for subj,vidid,Vinpath,Voutpath in stack:
        if not isfile(join(Vinpath, conf.fn.shots)):
            print "%s - No infofile found, skipping video"%vidid
            continue
        # check if frame path exist -- if this processing is done.
        if not isdir(Voutpath):
            mkdir(Voutpath)
        elif isfile(join(Voutpath, conf.fn.shots)) or isfile(join(Voutpath,'started_filtering')):
            print "%s - Movie is processed or busy, Skipping video"%vidid
            continue

        open(join(Voutpath,'started_filtering'),'wb').close()
        print "%s - subj: %s START FILTERING"%(vidid, subj)
        try:
            sel=Selector(subj, vidid)
            sel.apply_filters_write()
            sel.save_results()
            sel.ffmpeg()
            os.remove(join(Voutpath,'started_filtering')) # Will only be removed if ended nicely
        except Exception as e:
            traceback.print_exc()
            pdb.set_trace()
            print "%s - filtering failed with error:" % vidid
            print e


if __name__=="__main__" and len(sys.argv)==2:
    # Load one specific video
    vidid=sys.argv[1]
    vidpath=glob.glob(join(conf.path.thumbs,'*',vidid))
    if (len(vidpath)!=1):
        raise Exception('I found %d vids: %s'%(len(vidpath), str(vidpath)))
    vidpath=vidpath[0]
    subj = split(split(vidpath)[0])[1]
    print "Load selector for video %s, in subj %s"%(vidpath, subj)
    sel=Selector(subj, vidid)
    sel.apply_filters_write()
    sel.save_results()
    #sel.ffmpeg()
