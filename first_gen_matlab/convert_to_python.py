import numpy as np
from scipy import misc
import cPickle
import os
import os.path
import cPickle

data_class = np.ndarray(shape=(32 * 32 * 3, 50000), dtype=np.uint8)
labels_class = list()
for i in range(1, 6):
  fo = open('data_batch_%d' % i, 'rb')
  dict = cPickle.load(fo)
  data_class[:, (i - 1) * 10000 : (i * 10000)] = dict['data'][:, :]
  labels_class[(i - 1) * 10000 : (i * 10000)] = dict['labels']

data_class = data_class.reshape(32 * 32 * 3 * 2, 50000 / 2)

# Double check if order of data in my arrays is correct.

batch_size = 10000
maxsize = 50000

data = np.ndarray(shape=(32 * 32 * 3, maxsize), dtype=np.uint8)
names = np.ndarray(shape=(maxsize), dtype=np.dtype('a25'))
labels = list()

d='/Users/wojto/img_32_32'
idx = 0
class_idx = 0
for o in os.listdir(d): 
  o2 = os.path.join(d,o)
  if os.path.isdir(o2):
    for o3 in os.listdir(o2): 
      o4 = os.path.join(o2,o3)
      if (os.path.isfile(o4)) & (o3.find('.png') > 0):
        try:  	
          l = misc.imread(o4)
          data[:, idx] = np.reshape(l, 32 * 32 * 3)
          names[idx] = o3[0:-4]
          labels.append(-1)
          idx += 1
        except:   
          print 'Exception\n'     
          if idx % 2 == 1:
            idx -= 1
        print o4
        if (idx - 1) % 2 == 0:
          assert(names[idx - 1][-1] == 'A')
        else:
          assert(names[idx - 1][-1] == 'B')               

data = data[:, 0:idx]
data = data.reshape(32 * 32 * 3 * 2, idx / 2)
names = names[0:idx]



with open('/Users/wojto/convnet/extract_frames/data_frames', 'wb') as fp:
  cPickle.dump(data, fp)
  cPickle.dump(names, fp)
  cPickle.dump(labels, fp)

