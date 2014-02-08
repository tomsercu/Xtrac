

import conf
from os import listdir,mkdir
from os.path import isfile,isdir,join, expanduser, split
import sys
import random
import subprocess
import shlex
from subprocess import PIPE, Popen
import simplejson as json
import time

def dump_frames(subj, vidid):
    cmd = None

def run_mfile(mfile, silent=True):
    cmd  = conf.matlab
    cmd += ' -r "run(\'%s\');exit;"' % mfile
    if not silent: print cmd
    cmd = shlex.split(cmd)
    if not silent: print cmd
    # call subprocess
    if silent:
        proc  = Popen(cmd, stdout = PIPE, stderr = PIPE)
        stdo, stde = proc.communicate() # blocks but avoids pipe getting full
        return (proc.poll(), stdo, stde)
    else:
        proc  = Popen(cmd)
        code = proc.wait()
        return (code, None, None)

def write_launcher(shotnum, nstart, nstop, input_fn, output_dir):
    content = open('launcher_template.m','r').readlines()
    content = ''.join(content)
    content = content.format(**locals())
    #print locals().keys()
    open('launcher.m','w').write(content)


#mfile = join(conf.path.track, 'test_from_python(%s,%s)') % (10, 20)
# function call: xtrac_segment(input_fn, output_dir, shot_num, nstart, nstop)
#mfile = join(conf.path.track, 'xtrac_segment(%s,%s,%d,%d,%d)')
#shotnum = 16
#nstart = 1750
#nstop  = 1950
#input_fn = '/home/tom/frames/deer/v_lyOfZXKDU/v_lyOfZXKDU_00016_%8d.jpg'
#output_dir = '/home/tom/segment/deer/v_lyOfZXKDU'
#mfile = mfile % (input_fn, output_dir, shotnum, nstart, nstop)

#WRITE launcher.m FILE
#======================

#retcode, stdo, stde = run_mfile('launcher', False)



if __name__=="__main__" and len(sys.argv)==1:
    # Go through full directory structure and apply cheap filter
    inpath = conf.path.frames
    stack = []
    for subj in listdir(inpath):
        Sinpath=join(inpath,subj)
        if not isdir(Sinpath):
            continue
        Soutpath=join(conf.path.segment, subj)
        if not isdir(Soutpath):
            mkdir(Soutpath)
        vidlist=listdir(Sinpath)
        print "Enter directory %s with %d videos"%(Sinpath,len(vidlist))
        for vidid in vidlist:
            Vinpath = join(Sinpath,  vidid)
            Voutpath= join(Soutpath, vidid)
            stack.append((subj, vidid, Vinpath, Voutpath))
    random.shuffle(stack)
    for subj,vidid,Vinpath,Voutpath in stack:
        if not isfile(join(Vinpath, conf.fn.shots)):
            print "%s - No infofile found, skipping video"%vidid
            continue
        # check if frame path exist -- if this processing is done.
        if not isdir(Voutpath):
            mkdir(Voutpath)
        elif isfile(join(Voutpath, conf.fn.shots)) or isfile(join(Voutpath,'started_segmenting')):
            print "%s - Movie is processed or busy, Skipping video"%vidid
            continue
        open(join(Voutpath,'started_segmenting'),'wb').close()
        print "%s - subj: %s START SEGMENTING"%(vidid, subj)
            # todo load shotinfo file,
        shotinfo = json.load(open(join(Vinpath,conf.fn.shots), 'r'))
        input_fn = join(Vinpath,conf.frames.fn.format(vidid=vidid))
        for shotnum, (nstart, nstop) in enumerate(shotinfo):
            if nstart is None:
                continue # shot is discarded by cheap filtering
            try:
                print "%s - (%s) shot %d  - frames %d to %d => %d frames - start segmenting"%(vidid, subj,shotnum, nstart, nstop, nstop-nstart+1)
                write_launcher(shotnum, nstart, nstop, input_fn, Voutpath) # reads in shot info
                tic = time.time()
                retcode, stdo, stde = run_mfile('launcher', True)
                tac = time.time()
                if retcode != 0:
                    print "%s - error - shotnum %d nstart %d nstop %d -  segmenting failed with return code %d" % (vidid, shotnum, nstart, nstop, retcode)
                print "%s - (%s) shot %d  - frames %d to %d => %d frames - done in %.1f sec"%(vidid, subj,shotnum, nstart, nstop, nstop-nstart+1, tac-tic)
            except Exception as e:
                traceback.print_exc()
                pdb.set_trace()
                print "%s - error - python wrapper around segmenting failed with error:" % vidid
                print e
        print "%s - success - segmenting finished with return code %d" % (vidid, retcode)
        os.remove(join(Voutpath,'started_filtering')) # Will only be removed if ended nicely

