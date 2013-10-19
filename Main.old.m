path ='/mnt/datadrive/CILVR/yt_data/';
name = 'G6PbCte9xpE';
obj = VideoReader(sprintf('%s%s.mp4', path,name));
start = -1;
idx = 1;
width = 200;
height = 200;
i = floor(5 * obj.FrameRate);
fprintf('Opened %s, Number of frames %d',name, obj.NumberOfFrames)
while (i < obj.NumberOfFrames)
    i = i + floor(obj.FrameRate / 8); 
    f1_idx = i - floor(obj.FrameRate / 4);
    f1 = extract_center(read(obj, f1_idx));
    df = diff(f1);
    if ((mean(f1(:)) < 25) || (mean(f1(:)) > 225))
        start = -1;      
        i = i + 2 * floor(obj.FrameRate);
        continue;
    end
    if (start == -1)
        start = f1_idx;
    end
    f2 = extract_center(read(obj, i));
    if ((mean(f2(:)) < 50) || (mean(f2(:)) > 200))
        continue;
    end    
    if ((mean(abs(f1(:) - f2(:))) < 30) && (mean(abs(f1(:) - f2(:))) > 7)) && (length(abs(f1(:) - f2(:)) > 2) > 0.9 * length(f1(:)))
        if ((i - start) > (1 * obj.FrameRate))
            save_image(f1, sprintf('%s%s_%d_A', path, name, idx), width, height);
            save_image(f2, sprintf('%s%s_%d_B', path, name, idx), width, height)
            fprintf('Saved %s idx = %d\n', name, idx);
            idx = idx + 1;
            start = -1;
        end
    else
        start = -1;
    end    
end


