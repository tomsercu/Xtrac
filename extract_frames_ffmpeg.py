import numpy as np
import subprocess
import os
from os.path import join,isdir,exists, expanduser, split
from os import listdir
import sys
import glob
#import cv2
import traceback
import simplejson as json
import conf

#wojdir= '/misc/vlgscratch2/FergusGroup/zaremba'
#cifar32=True
#viddir=expanduser('~/youtube')
#if cifar32:
    #framedir=expanduser('~/cifar32_all')
#else:
    #framedir=expanduser('~/thumbs')

#framerate=2
#scene_threshold=0.3 # see ffmpeg scene  selection
#fprefix='frame_'
#logfn='out.log'
#picklefn='info.pk'

# OR make thumbnails that preserve aspect ratio
#command='ffmpeg -i "%s" -vf select=\'gt(scene\,%.2f)+gte(t-prev_selected_t\,%.2f)\',scale=-1:80 -vsync 2 -f image2 "%s" -loglevel debug 2>&1 | grep "select:[^0]" > "%s"'

def parse_logfile(vidid, subj):
    p = join(conf.path.thumbs, subj, vidid)
    ffmpeg_log = join(p, conf.fn.ffmpeg_log)
    shots_fn   = join(p, conf.fn.shots)
    with open(ffmpeg_log,'r') as fh:
        lines=fh.readlines()
    nfiles = len(glob.glob(join(conf.path.thumbs, subj, vidid, '*.jpeg')))
    if len(lines) != nfiles:
        print "%s - Parsing ffmpeg log -- unexpected # loglines: %d, jpeg files: %d"%(vidid, len(lines), nfiles)
    shots=[] # contains list of shots
    shotid=-1
    for i,line in enumerate(lines):
        rel=line[str.find(line,'n:'):]
        if (rel==-1):
            print "%s - encountered bad line %d/%d in ffmpeg log, starts as: "%(vidid,i,len(lines),line[:40])
            continue
        info=[s for s in rel.split(' ') if s.count(':')==1]
        for k,v in [kv.split(':') for kv in info]:
            if k=='n': frame_id=int(float(v))
            if k=='t': t=float(v)
            if k=='scene':
                ffmpeg_scene=float(v)
                if ffmpeg_scene >= conf.shotdetect.threshold:
                    shotid+=1
                    shots.append([])
        # collected all info from line, add to frames list
        shots[shotid].append({'thumb_n':i+1,   # in thumb output jpeg files, not following movie
                              'n' : frame_id,  # in original movie
                              't':t,
                              'ffmpeg_scene':ffmpeg_scene})
        assert(os.path.exists(join(conf.path.thumbs, subj, vidid, conf.thumbs.fn.format(vidid=vidid, num='000001'))))
    if shots_fn is not None:
        json.dump(shots, open(shots_fn, 'w'), indent = 2)
    tb="%s - Extracted %d sample thumbnails, in %d shots. Movie time from %.1f to %.1f seconds."%(vidid,len(lines),shotid+1,shots[0][0]['t'],shots[-1][-1]['t'])
    tb+="\n%s - Succesfully parsed ffmpeg log to shot info and saved to %s"%(vidid,shots_fn)
    print tb
    return shots

def ffmpeg(subj, vidid):
    video = join(conf.path.video,  subj, vidid)
    if exists(video + '.mp4'): video = video + '.mp4'
    else: video = video + '.flv'
    out = join(conf.path.thumbs, subj, vidid)
    if (isdir(out)):
        if (exists(join(out,'started')) or len(glob.glob(join(out, conf.thumbs.fn.format(vidid=vidid, num='*'))))>0):
            print "%s - Skipping video"%vidid
            return -1
    else:
        os.mkdir(out)
    with open(join(out,'started'), 'wb') as fh:
        fh.write('busy')
    print "%s - Subprocess ffmpeg to extract frames, writing to %s"%(vidid,'/'.join(out.split('/')[-4:]))
    thumb_fn = join(out, conf.thumbs.fn.format(vidid = vidid, num = '%06d'))
    # FFMPEG COMMAND
    command =  'ffmpeg -i "%s" ' % video
    command += '-vf select=\'gt(scene\,%.2f)' % (conf.shotdetect.threshold)
    command += '+gte(t-prev_selected_t\,%.2f)\',' % (1.0 / conf.thumbs.framerate)
    command += 'scale=%d:%d' % (conf.thumbs.w, conf.thumbs.h)
    if conf.thumbs.crop is not None:
        command += ',crop=%d:%d' % (crop, crop)
    command += ' -vsync 2 -f image2 "%s" ' % thumb_fn
    command += ' -loglevel debug 2>&1 | grep "select:[^0]" > "%s"' % join(out, conf.fn.ffmpeg_log)
    #Run ffmpeg
    #===============
    result=subprocess.call(command,shell=True)

    if (result==0):
        print "%s - Finished extracting frames, start making overview."%vidid
    else:
        print "%s - ffmpeg returned  unsuccesful with code %d."%(vidid,result)
        with open(join(out,'command.log'),'w') as fh:
            fh.write(command+'\n')
        print "%s - Wrote failing command to %s."%(vidid,join(out,'command.log'))
    return result



if __name__=="__main__" and len(sys.argv)==1:
    nprocessed=1 # how many processed in last cycle
    while nprocessed>0:
        print "==========="
        print "START CYCLE"
        print "==========="
        nprocessed=0
        for subj in listdir(conf.path.video):
            spath=join(conf.path.video,subj)
            spath_th=join(conf.path.thumbs,subj)
            if not isdir (spath):
                continue
            vidlist=glob.glob(join(spath,'*.flv'))
            vidlist.extend(glob.glob(join(spath,'*.mp4')))
            if not isdir(spath_th) and len(vidlist)>0:
                print "Make directory %s"%spath_th
                os.mkdir(spath_th)
            print "Entered directory %s with %d videos"%(spath,len(vidlist))
            for vidpath in vidlist:
                vidid=os.path.split(vidpath)[1].split('.')[0]
                # SUBPROCESS FFMPEG
                result = ffmpeg(subj, vidid)
                if result == 0:
                    nprocessed += 1
                else:
                    continue
                # START compiling output log to shot info
                try:
                    shot_info = parse_logfile(vidid, subj)
                    tb = ""
                except:
                    tb="%s - Error occured during parsing of ffmpeg output to scene info \n"%vidid
                    tb+=traceback.format_exc()
                finally:
                    print tb
        print "================================="
        print "END CYCLE--- %d videos processed" % nprocessed
        print "================================="


if __name__=="__main__" and len(sys.argv)==2:
    # Load one specific video
    vidid=sys.argv[1]
    vidpath=glob.glob(join(conf.path.video, '*', vidid+'.mp4'))
    vidpath.extend(glob.glob(join(conf.path.video, '*', vidid+'.flv')))
    if (len(vidpath)!=1):
        raise Exception('I found %d vids: %s'%(len(vidpath), str(vidpath)))
    vidpath=vidpath[0]
    subj = split(split(vidpath)[0])[1]
    print "Found %s in subject %s" % (vidid, subj)
    result = ffmpeg(subj, vidid)
    print "FFMPEG result: %d" % result
    if result == 0:
        shot_info = parse_logfile(vidid, subj)

