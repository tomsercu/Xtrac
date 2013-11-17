import numpy as np
import subprocess
import os
from os.path import join,isdir
from os import listdir
import glob
#import cv2
import traceback
import cPickle as pickle

maindir = '/mnt/datadrive/CILVR'
#maindir = '/misc/vlgscratch2/FergusGroup/sercu'
viddir=join(maindir,'youtube')
framedir=join(maindir,'frames')

framerate=2
scene_threshold=0.3 # see ffmpeg scene  selection
fprefix='frame_'
logfn='out.log'
picklefn='info.pk'

command='ffmpeg -i "%s" -vf select=\'gt(scene\,%.2f)+gte(t-prev_selected_t\,%.2f)\' -vsync 2 -f image2 "%s" -loglevel debug 2>&1 | grep "select:[^0]" > "%s"'
# thiss command needs: (inpfile,scene_threshold,frameskip,outdir/frame,outdir/log.txt)

for subj in listdir(viddir):
    spath=join(viddir,subj)
    spathO=join(framedir,subj)
    if not isdir (spath):
        continue
    vidlist=glob.glob(join(spath,'*.mp4'))
    if not isdir(spathO) and len(vidlist)>0:
        print "Make directory %s"%spathO
        os.mkdir(spathO)
    print "Entered directory %s with %d videos"%(spath,len(vidlist))
    for vidpath in vidlist:
        vidid=os.path.split(vidpath)[1].split('.')[0]
        #Todo go into framedir, check if frames exist and keyframes exists then continue. Otherwise mkdir and execute command.
        out=join(spathO,vidid)
        if (isdir(out)):
            if (len(glob.glob(join(out,'frame*.jpeg')))>0):
                pass #continue
        else:
            os.mkdir(out)
        print "Starting to extract frames for id=%s, dumping to %s"%(vidid,out)
        outframes=join(out,fprefix+'%05d.jpeg')
        thiscommand=command%(vidpath,scene_threshold, 1./framerate, outframes,join(out,logfn))
        result=subprocess.call(thiscommand,shell=True)
        if (result==0):
            print "Finished extracting frames for %s, start making overview."%vidid
        else:
            print "ERROR IN EXTRACTIN FROM %s"%vidid
        # START compiling output log to shot info
        try:
            with open(join(out,logfn),'r') as fh:
                lines=fh.readlines()
            assert(len(lines)==len(glob.glob(join(out,'*.jpeg')))) # todo catch this
            headers=['frame_id','shotid','fn','out_id','t','ffmpeg_scene']
            shots=[] # contains list of shots
            shotid=-1
            for i,line in enumerate(lines):
                rel=line[str.find(line,'n:'):]
                info=[s for s in rel.split(' ') if s.count(':')==1]
                for k,v in [kv.split(':') for kv in info]:
                    if k=='n': frame_id=int(float(v))
                    if k=='t': t=float(v)
                    if k=='scene':
                        ffmpeg_scene=float(v)
                        if ffmpeg_scene>=scene_threshold: 
                            shotid+=1
                            shots.append([])
                # collected all info from line, add to frames list
                shots[shotid].append([frame_id,shotid,outframes%(i+1),i+1,t,ffmpeg_scene])
                assert(os.path.exists(shots[-1][-1][2]))
            picklefile=join(out,picklefn)
            pickle.dump({'headers':headers,'shots':shots}, open(picklefile,'wb'))
        except:
            tb=traceback.format_exc()
        else:
            tb="Succesfully compiled info and dumped to %s"%picklefile
            tb+="\nExtracted %d frames, in %d shots. Time from %.1f to %.1f seconds."%(len(lines),shotid+1,shots[0][0][4],shots[-1][-1][4])
        finally:
            print tb

