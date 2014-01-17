

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


mfile = join(conf.path.track, 'test_from_python(%s,%s)') % (10, 20)
retcode, stdo, stde = run_mfile(mfile, False)
