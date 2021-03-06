function [ mov ] = mp4_to_mat( inpath, outpath, framerate, f_size )
% mp4_to_mat Transformsm video to redcued-size center-cut out matrix
% [t,x,y,rgb]
%   Dumps it to out.mat and returns.
    %% Get movie name and open video reader
    if (exist(strcat(outpath,'.mat'),'file'))
        fprintf('.mat file already exists:  %s.mat\n',outpath)
        mov=[];
        return;
    end
    if (exist(strcat(outpath,'.busy'),'file'))
        fprintf('Transformation already busy for %s\n',outpath)
        mov=[];
        return;
    end
    fclose(fopen(strcat(outpath,'.busy'), 'w'));
    try
        fprintf('Opening video reader for %s\n',inpath)
        obj = VideoReader(inpath);
    catch ME
        fprintf('ERROR could not read video in %s \n',inpath);
        ME.stack
        return;
    end
    %% Process frames
    fprintf('Processing %s\n', inpath);
    s = min(floor(60 * obj.FrameRate), floor(0.05 * obj.NumberOfFrames)); % Start of video
    e = max((obj.NumberOfFrames - floor(60 * obj.FrameRate)), floor(0.95 * obj.NumberOfFrames)); % End of vid
    r = floor(obj.FrameRate / framerate);
    nr_frames = floor((e - s) / r) + 1;
    f_all = zeros(nr_frames, f_size * f_size * 3);
    for q = 1:nr_frames
        if (mod(q, 100) == 0)
            fprintf('%d / %d\n', q, nr_frames);                
        end
        indx = (q - 1) * r + s;
        tmp = extract_center(read(obj, indx), f_size);
        f_all(q, :) = tmp(:);
    end
    mov = reshape(f_all, [nr_frames, f_size, f_size, 3]);
    save(outpath,'mov','framerate','f_size');
    delete(strcat(outpath,'.busy'));
end

