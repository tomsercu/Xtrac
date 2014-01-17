
from os.path import join, expanduser

### PATHS
class path:
    video = expanduser('~/youtube ')
    thumbs = expanduser('~/thumbs')   # sparse small thumbs -- small part of frames
    frames = expanduser('~/frames')   # frames for tracking -- all frames
    output = expanduser('~/cifar32')  # actual selections

### DOWNLOADS
class down:
    Npersubj = 50 # number of downloads per subject
    maxpages = 5  # number of pages per query
    queryfile = 'cifar10.json'

### FFMPEG PROCESSING AND SHOT DETECTION
class shotdetect:
    threshold = 0.3 # see ffmpeg scene selectio
    ffmpeg_log_fn = 'out.log'
    shots_fn = 'shots.json'

class thumbs:
    w = -1
    h = 32
    fn= 'thumb_%06d.jpg'

### CHEAP FILTERING
class filter:
    min_shot_len = 3
    min_rel_diff_frames = 0.02
    max_rel_diff_frames = 0.9
    min_brightness = 80
    min_bright_area = 0.15
    max_brightness = 170
    min_dark_area  = 0.15

### TRACKING
class tracking:
    w = 100
    h = -1
    class fast:
        min = 50
        num = 20
