#!/usr/lib/python
import urllib2
import re
import sys, os, subprocess
from os import listdir
from os.path import expanduser, isfile, join, isdir
import shutil
import cPickle as pickle
import datetime
import simplejson as json

# TODO detect doubles in selected queries!
#===============================================================================
# Parameters
#===============================================================================
outdir=expanduser('~/youtube')
Npersubj=50 # increase to download more per subject
maxpages=5
ytstring='http://www.youtube.com/results?filters=video%2C+long&'
#===============================================================================
# Load all queries
#===============================================================================
with open('cifar10.json','rU') as fh:
    queries=json.load(fh)
subjects=queries.keys()

#===============================================================================
# What did we already downlod
#===============================================================================
movielist = set(); # movies downloaded over all subdirs
def updatemovielist():
    global movielist, outdir
    for subj in listdir(outdir):
        spath=join(outdir,subj)
        if isdir(spath):
            for f in listdir(spath):
                if isfile(join(spath, f)):
                    if f[-4:]=='.mp4' or f[-4:]=='.flv':
                        movielist.add(f[0:-4])
#===============================================================================
# Generate directories if needed
#===============================================================================
for subj in subjects:
    spath=join(outdir,subj)
    if not os.path.exists(spath):
        print "Make dir %s"%spath
        os.mkdir(spath)


#===============================================================================
# Assemble videos to download, including movies we already have.
#===============================================================================
dlist={}
for subj in subjects:
    Nperquery=Npersubj/len(queries[subj])
    dlist[subj]={}
    print "Looking for subject %s"%subj
    for query in queries[subj]:
        dlist[subj][query]=[]
        enough=False
        p=0
        while (not enough and p<maxpages): # open new pages
            p+=1
            print "Subject %s, query:  %s page %d, downloading %d movies"%(subj,query,p, Nperquery)
            url=ytstring+'search_query=%s&page=%d' % (query.replace(' ','+'), p)
            response = urllib2.urlopen(url)
    #         response = urllib2.urlopen('http://www.youtube.com/results?search_query=discovery%20channel&page=' + str(i))
            html = response.read()
            for m in re.finditer('watch\?v=', html):
                tmp = html[(m.end() - 1):]
                endidx = tmp.find('"')
                if endidx > 15:
                    continue
                movie = tmp[1:endidx]
                dlist[subj][query].append(movie)
                if (len(dlist[subj][query]) == Nperquery):
                    enough=True
                    break

#===============================================================================
# Dump current download list for future reference (what queries suck)
#===============================================================================
now=datetime.datetime.now()
fn='dlist_%s.dlp' % now.strftime('%Y-%m-%d_%Hh%M')
pickle.dump(dlist, open(join(outdir,fn), 'wb'))
#===============================================================================
# Download videos
#===============================================================================
for subj in subjects:
    for q in queries[subj]:
        for movie in dlist[subj][q]:
            updatemovielist()
            if (movie not in movielist):
                movielist.add(movie)
                out=join(outdir,subj,movie+'.mp4')
                cli = 'youtube-dl -o %s --write-description --all-subs --write-info-json http://www.youtube.com/watch?v=%s'%(out,movie)
                print cli
                subprocess.call(cli, shell=True)
            else:
                print "%s -- Movie  is already downloaded, skip"%movie




