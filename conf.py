
from os.path import join, expanduser
import datetime

### PATHS
class path:
    video = expanduser('~/youtube')
    thumbs = expanduser('~/thumbs')   # sparse small thumbs -- small part of frames
    frames = expanduser('~/frames')   # frames for tracking -- all frames
    track  = '../region_proposals'
    output = expanduser('~/cifar32')  # actual selections

class fn:
    shots = 'shots.json'
    ffmpeg_log= 'ffmpeg.log'
    filter = 'filtered.json'


### DOWNLOADS
class down:
    Npersubj = 50 # number of downloads per subject
    maxpages = 5  # number of pages per query
    queryfile = 'cifar10.json'
    ytstring = 'http://www.youtube.com/results?filters=video%2C+long&'
    ids_fn = join(path.video, 'down_ids_%s.json' % datetime.datetime.now().strftime('%Y-%m-%d_%Hh%M'))

### FFMPEG PROCESSING AND SHOT DETECTION
class shotdetect:
    threshold = 0.3 # see ffmpeg scene selectio

class thumbs:
    w = -1
    h = 32
    framerate = 2
    crop = None  # None or w:h eg crop = 32:32
    fn = '{vidid}_{num}.jpg'

### CHEAP FILTERING
class filt:
    min_shot_len = 3
    min_rel_diff_frames = 0.02
    max_rel_diff_frames = 0.9
    min_brightness = 80
    min_bright_area = 0.15
    max_brightness = 170
    min_dark_area  = 0.15

class frames:
    w = -1
    h = 100
    fn = '{vidid}_{shot:05d}-%08d.jpg'

### TRACKING
matlab = 'optirun /usr/local/bin/matlab -nodesktop -nosplash'
class tracking:
    w = 100
    h = -1
    class fast:
        min = 50
        num = 20

