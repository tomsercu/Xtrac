from os.path import isfile, join, isdir
from os import listdir
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import Image
import conf
import numpy as np

N = 32
w = 57
h = 32
W = w*N
H = h*N


for subj in listdir(conf.path.thumbs):
    spath = join(conf.path.thumbs, subj)
    if not isdir(spath): continue
    for vidid in listdir(spath):
        if not isdir(join(spath,vidid)): continue
        flist = glob.glob(join(spath,vidid,'*.jpg'))
        if len(flist) < 10: continue
        print "%s - found %d frames" % (vidid, len(flist))
        im = np.zeros((H,W,3), dtype='uint8')
        i = 0
        for di in np.linspace(0,len(flist)-1, N**2):
            x,y = divmod(i,N)
            tmp = mpimg.imread(flist[int(di)])
            th = min(h,tmp.shape[0])
            tw = min(w,tmp.shape[1])
            im[x*h:x*h+th, y*w:y*w+tw, :] = tmp[:th, :tw, :]
            i+=1
        im2 = Image.fromarray(im)
        im2.save(join(spath,'grid_%s.jpg' % vidid))
        #plt.figure(figsize=(20,14))
        #plt.imshow(im)
        #plt.axis('off')
        #plt.savefig(join(spath,'grid_%s.jpg' % vidid))
        #plt.close()
