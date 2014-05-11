import simplejson as json
import conf
import os
from os.path import join
import sys

subj = sys.argv[1]
vidid = sys.argv[2]
n = int(sys.argv[3])

thumb_info = json.load(open(join(conf.path.thumbs,subj,vidid,conf.fn.shots),'r'))
frame_info = json.load(open(join(conf.path.thumbs,subj,vidid,conf.fn.filter),'r'))['shots_pass']

assert(len(thumb_info) == len(frame_info))
Nshots = len(thumb_info)
assert(n < Nshots)
if frame_info[n] < 0:
    print -1
else:
    #print the thumb fn's
    for thumb in thumb_info[n]:
        print ((join(conf.path.thumbs,subj,vidid,conf.thumbs.fn) )\
                .format(vidid=vidid,num='%06d'%thumb['thumb_n']))



if False: # loading frames (full-sampled) instead of thumbs
    thumb_info = json.load(open(join(conf.path.thumbs,subj,vidid,conf.fn.shots),'r'))
    frame_info = json.load(open(join(conf.path.frames,subj,vidid,conf.fn.shots),'r'))
    assert(len(thumb_info) == len(frame_info))
    Nshots = len(thumb_info)
    assert(n < Nshots)
    # See if frame passed selection
    if frame_info[n] == [None, None]:
        print -1
    else:
        # print the full frame fn's
        for i in xrange(frame_info[n][0], frame_info[n][1]+1):
            print ((join(conf.path.frames,subj,vidid,conf.frames.fn) % i).format(vidid=vidid))
