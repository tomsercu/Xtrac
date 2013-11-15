
import numpy as np
import scipy.io
import scipy.signal as sps
import matplotlib.pyplot as plt

class Extractor:
    def __init__(self,path):
        self.path=path
        tmp=scipy.io.loadmat(path)
        self.d=tmp['mov']
        if 'framerate' in tmp:
            self.framerate=tmp['framerate']
        else:
            self.framerate=2
#         if 'cuts' in tmp:
#             self.cuts=tmp['cuts']
#         else:
        self.cuts=None
        self.intensities=None
        self.ds=None
        
        
    def showimg(self,i):
        plt.imshow(self.d[i,:,:]);
        plt.show()
     
    def showgrid(self,inds):
        rows=len(inds)
        cols=max( [len(inds[i]) for i in range(len(inds))])
        i=0
        plt.figure(figsize=(20,12))
        for r,shot in enumerate(inds):
            print ('shot %d:'%r),
            for fr in shot:
                i+=1
                plt.subplot(rows,cols,i)
                plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
                print ('%d,'%fr),
                plt.imshow(self.d[fr])
                plt.axis('off')
            i=cols*r
            print('')
        plt.show()
        
    def mask_unnatural(self):
#         TODO: pythonize this code
#         df_all_full = sum(squeeze(abs(f_all_full(:, 2:f_size, :, :) - f_all_full(:, 1:(f_size - 1), :, :))), 4);
#         sizex = [10, 4, 1, 2, 5];
#         sizey = [1, 4, 10, 5, 2];
#         for i = 1:length(sizex)
#             df_all_full_conv = convn(df_all_full, ones(1, sizex(i), sizey(i)), 'valid');
#             valid(sum(df_all_full_conv(:, :) == 0, 2) > 0) = 0;
#         end
#         valid = conv(valid, ones(lend, 1), 'valid');
        
        if self.cuts is not None or self.intensities is not None or self.ds is not None:
            print "Dont mask after other operations!!!"
            return
        f_dx=np.sum( abs(self.d[:,1:]-self.d[:,:-1]) ,axis=3) # shift x, sum over colors
        sizex = [10, 4, 1, 2, 5]
        sizey = [1, 4, 10, 5, 2]
        for x,y in zip(sizex,sizey):
            filt=np.ones((1,x,y)) 
            f_conv=sps.fftconvolve(f_dx,filt,'valid')
            np.where(f_conv==0)
            
    
    def detectcuts (self):
        # Generate intensities, lowpassed
        self.intensities=np.sum(np.sum(np.sum(np.abs(self.d),axis=3),axis=2),axis=1)
        filt=sps.hamming( max(9, 3*self.framerate ))
        filt=filt/np.sum(filt)
        self.int_lp=sps.fftconvolve(self.intensities,filt,'same')
        # Euclidian distance between frames, in time.
        ds=np.abs(self.d[1:]-self.d[:-1])
        ds=np.sum(np.sum(np.sum(ds,axis=3),axis=2),axis=1)
        self.ds=ds/self.int_lp[1:]
        self.cuts=np.argsort(self.ds)[-120:]
        self.cuts=self.cuts[::-1]+1
        self.cuts.sort()
    
    def showshots (self,shots=12,nframes=16):
        cutind=[np.random.randint(0,len(self.cuts)-1) for i in range(shots)]
        frames=[]
        for i in cutind:
            fstart=self.cuts[i]
            fend=self.cuts[i+1]-1
            if fend-fstart<nframes:
                frames.append(range(fstart,fend+1))
            else:
                shot=[fstart-1,]
                r=(fend-fstart)/nframes+1 # round up
                shot.extend(range(fstart,fend,r))
                shot.extend([fend,fend+1])
                frames.append(shot)
        self.showgrid(frames)
        return frames
    
    def showcuts (self,which=None,num=10):
        if which is None:
            cutind=[self.cuts[np.random.randint(0,len(self.cuts))] for i in range(num)]
        elif which=='last':
            cutind=self.cuts[-num:]
        else:
            cutind=self.cuts[:num]
        grid=[ [i-1,i,i+1] for i in cutind]
        print(grid)
        self.showgrid(grid)

ex=Extractor('/home/tom/youtube/Bears/4msUhLnQtn0.mat')

ex.detectcuts()

frames=ex.showshots()
