

import conf
from os.path import join
import subprocess
import shlex
from subprocess import PIPE, Popen

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

retcode, stdo, stde = run_mfile('launcher', False)
