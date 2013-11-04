#!/usr/lib/python
import urllib2
import re
import sys, os, subprocess
from os import listdir
from os.path import isfile, join, isdir
import shutil
import cPickle as pickle
import datetime

#===============================================================================
# Parameters
#===============================================================================
#outdir='/mnt/datadrive/CILVR/youtube'
outdir='/misc/vlgscratch2/FergusGroup/sercu/youtube/'
subjects=['Bears', 'Lions', 'Giraffe']
appendices=['documentary','national geographic', 'wildlife', 'attenborough']
Nperquery=20 # increase to download more per subject
maxpages=5
ytstring='http://www.youtube.com/results?filters=hd%2C+long%2C+video&'
#===============================================================================
# Make all queries
#===============================================================================
queries={}
for subj in subjects:
    queries[subj] = ['%s %s'%(subj,app) for app in appendices]

#===============================================================================
# What did we already downlod 
#===============================================================================
movielist = set(); # movies downloaded over all subdirs
for subj in subjects:
    spath=join(outdir,subj)
    if isdir(spath):
        for f in listdir(spath):
            if isfile(join(spath, f)):
                movielist.add(f[0:-4])
    elif not os.path.exists(spath):
        print "Make dir %s"%spath
        os.mkdir(spath)


#===============================================================================
# Assemble videos to download 
#===============================================================================
dlist={}
for subj in subjects:
    dlist[subj]={}
    print "Looking for subject %s"%subj
    for query in queries[subj]:
        dlist[subj][query]=[]
        enough=False
        p=0
        while (not enough and p<maxpages): # open new pages
            p+=1
            print "Subject %s, query:  %s page %d"%(subj,query,p)
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
                if (movie not in movielist):
                    dlist[subj][query].append(movie)
                    movielist.add(movie)
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
            out=join(outdir,subj,movie+'.mp4')
            cli = 'youtube-dl -o %s --write-description --all-subs --write-info-json http://www.youtube.com/watch?v=%s'%(out,movie)
            print cli
            subprocess.call(cli, shell=True)
                            


