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
import conf

# TODO detect doubles in selected queries!

#===============================================================================
# What did we already downlod
#===============================================================================
movielist = set(); # movies downloaded over all subdirs

def updatemovielist():
    global movielist
    for subj in listdir(conf.path.video):
        spath=join(conf.path.video, subj)
        if isdir(spath):
            for f in listdir(spath):
                if isfile(join(spath, f)):
                    if '.mp4.info.json' in f or '.flv.info.json' in f:
                        vidid = f[0:-14]
                        movielist.add(vidid)

def get_video_ids(write = True):
    global movielist
    #===============================================================================
    # Load all queries
    #===============================================================================
    with open(conf.down.queryfile,'rU') as fh:
        queries=json.load(fh)
    subjects=queries.keys()

    #===============================================================================
    # Assemble videos to download, including movies we already have.
    #===============================================================================
    down_ids={}
    for subj in subjects:
        down_ids[subj]={}
        print "Looking for subject %s"%subj
        for query in queries[subj]:
            Npages = int(queries[subj][query]) # get number from dict
            down_ids[subj][query]=[]
            enough=False
            for p in range(1, Npages+1):
                print "Subject %s, query:  %s page %d/%d"%(subj,query,p,Npages)
                url = conf.down.ytstring+'search_query=%s&page=%d' % (query.replace(' ','+'), p)
                response = urllib2.urlopen(url)
        #         response = urllib2.urlopen('http://www.youtube.com/results?search_query=discovery%20channel&page=' + str(i))
                html = response.read()
                for m in re.finditer('watch\?v=', html):
                    tmp = html[(m.end() - 1):]
                    endidx = tmp.find('"')
                    if endidx > 15:
                        continue
                    vidid= tmp[1:endidx]
                    down_ids[subj][query].append(vidid)
    if write:
        # Write video id download list
        json.dump(down_ids, open(conf.down.ids_fn, 'w'), indent = 2, sort_keys = True)
    return down_ids

def download(down_ids):
    global movielist
    """ Use subprocess youtube-dl to download videos.
    expects down_ids to be a dictionary with subjects/categories as keys,
    per subject a dictionary with quries as keys,
    per query a list of video ids."""

    #===============================================================================
    # Make directories if needed
    #===============================================================================
    subjects = down_ids.keys()
    for subj in subjects:
        spath=join(conf.path.video, subj)
        if not os.path.exists(spath):
            print "Make dir %s"%spath
            os.mkdir(spath)

    #===============================================================================
    # Download videos
    #===============================================================================
    for subj in subjects:
        queries = down_ids[subj].keys()
        for q in queries:
            for vidid in down_ids[subj][q]:
                updatemovielist() # account for parallel execution
                if (vidid not in movielist):
                    movielist.add(vidid)
                    out=join(conf.path.video, subj, vidid)
                    # DOWNLOAD INFO
                    cli = 'youtube-dl -o %s --all-subs --write-info-json --skip-download http://www.youtube.com/watch?v=%s'%(out+'.mp4', vidid)
                    print '%s -- download:  %s ' % (vidid, cli)
                    subprocess.call(cli, shell=True)
                    # do checks
                    info = json.load(open(out+'.info.json','r'))
                    if int(info['duration'] < conf.down.min_len):
                        print "%s -- SKIP Movie  is shorter than %d sec" % (vidid, conf.down.min_len)
                        continue
                    if 'interview' in info['stitle'].lower():
                        print "%s -- SKIP Movie probably contains interview" % vidid
                        continue
                    if int(info['view_count']) < conf.down.min_views:
                        print "%s -- SKIP Movie, only %d views" % ( vidid, int(info['view_count']))
                        continue
                    # download movie itself
                    cli = 'youtube-dl -o %s --all-subs --write-info-json http://www.youtube.com/watch?v=%s'%(out+'.mp4', vidid)
                    print '%s -- download:  %s ' % (vidid, cli)
                    subprocess.call(cli, shell=True)
                else:
                    print "%s -- SKIP Movie  is already downloaded" % vidid


if __name__ == "__main__":
    down_ids = get_video_ids()
    download(down_ids)


