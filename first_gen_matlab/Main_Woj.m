% change properties of download to http://www.youtube.com/results?filters=hd%2C+long%2C+video&search_sort=video_view_count&search_query=national+geographic
% check if viewed more than 1000

% XXX: Send files to Tom !!!
% Sample from distant frames.
% get reference frames


% 1. Increase diversity
% 2. Iterate over i-frames
% 3. target of 1 mln of iamges
% 4. hadoop or whatever you prefer to make it fast
% 5. prevent from camera moving

addpath(genpath('.'));
global maindir
maindir = '/mnt/datadrive/CILVR/';
maindata = sprintf('%s/youtube', maindir);
dir_list = dir(maindata);
load('processed', 'processed');
f_size = 32;

for k = 1:length(dir_list)
    dir_name = dir_list(k).name;
    if (strfind(dir_name, '.'))
        continue;
    end
    mov_list = dir(sprintf('%s/%s', maindata, dir_name));
    for j = 1:length(mov_list)        
        if ((mov_list(j).isdir) || (mov_list(j).name(1) == '.'))
            continue
        end        
        name = mov_list(j).name;
        name = name(1:(strfind(name, '.') - 1));
        if (processed.isKey(name))
            continue;
        end
        file_path = sprintf('%s/%s/%s', maindata, dir_name, mov_list(j).name);
        try
            obj = VideoReader(file_path);
        catch
            continue;
        end
        fprintf('Processing %s\n', file_path);
        s = min(floor(60 * obj.FrameRate), floor(0.05 * obj.NumberOfFrames));
        e = max((obj.NumberOfFrames - floor(60 * obj.FrameRate)), floor(0.95 * obj.NumberOfFrames));
        r = floor(obj.FrameRate / 2);
        nr_frames = floor((e - s) / r) + 1;
        f_all = zeros(nr_frames, f_size * f_size * 3);
        for q = 1:nr_frames
            if (mod(q, 10) == 0)
                fprintf('%d / %d\n', q, nr_frames);                
            end
            indx = (q - 1) * r + s;
            tmp = extract_center(read(obj, indx), f_size);
            f_all(q, :) = tmp(:);
        end

        idx = 1;
        lend = 4;
        valid = ones(size(f_all, 1), 1);
        m = mean(f_all(:, :)')';
        valid(m < 0.1) = 0;
        valid(m > 0.9) = 0;
        f_all_full = reshape(f_all, [nr_frames, f_size, f_size, 3]);
        df_all_full = sum(squeeze(abs(f_all_full(:, 2:f_size, :, :) - f_all_full(:, 1:(f_size - 1), :, :))), 4);
        sizex = [10, 4, 1, 2, 5];
        sizey = [1, 4, 10, 5, 2];
        for i = 1:length(sizex)
            df_all_full_conv = convn(df_all_full, ones(1, sizex(i), sizey(i)), 'valid');
            valid(sum(df_all_full_conv(:, :) == 0, 2) > 0) = 0;        
        end
        valid = conv(valid, ones(lend, 1), 'valid');        
        
        continuous = zeros(size(f_all, 1) - 1, 1);
        df = f_all(2:end, :, :, :) - f_all(1:(end - 1), :, :, :);
        continuous(mean(abs(df(:, :))')' < 0.1) = 1;
        continuous = conv(continuous, ones(lend, 1), 'valid');
        discontinuos = zeros(size(f_all, 1) - 1, 1);
        dfn = abs(f_all(lend:end, :, :, :) - f_all(1:(end - lend + 1), :, :, :));
        dfn = reshape(dfn, [size(dfn, 1), f_size, f_size, 3]);
        dfn = sum(dfn, 4);
        dfn = dfn(:, :) ~= 0;
        discontinuos(sum(dfn, 2) > (0.995 * f_size * f_size)) = 1;
        for i = 1:length(continuous)            
            if ((valid(i) == lend) && (continuous(i) == lend) && (discontinuos(i) == 1))                
                save_image(reshape(f_all(i, :), [f_size, f_size, 3]), sprintf('%s/%s_%d_A', dir_name, name, idx), f_size);
                save_image(reshape(f_all(i + lend - 1, :), [f_size, f_size, 3]), sprintf('%s/%s_%d_B', dir_name, name, idx), f_size);                               
                idx = idx + 1;
            end
        end
        processed(name) = 1;
        save('processed', 'processed');
    end
end
