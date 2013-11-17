global maindir
%maindir = '/mnt/datadrive/CILVR';
maindir = '/misc/vlgscratch2/FergusGroup/sercu';
maindata = sprintf('%s/youtube', maindir);

f_size=32;
framerate=8;

dir_list = dir(maindata);

for k = 1:length(dir_list)
    dir_name = dir_list(k).name;
    if (strfind(dir_name, '.') | strfind(dir_name,'_'))
        continue;
    end
    mov_list = dir(sprintf('%s/%s/*.mp4', maindata, dir_name));
    fprintf('Entering directory %s with %d movies \n', dir_name, length(mov_list))
    outdir = sprintf('%s/%s_%d_%d',maindata,dir_name,framerate,f_size);
    if ~isdir(outdir)
        mkdir(outdir)
    end
    for j = 1:length(mov_list) 
        in_path = sprintf('%s/%s/%s', maindata, dir_name, mov_list(j).name);
        name = mov_list(j).name;
        name = name(1:(strfind(name, '.') - 1));
        out_path=sprintf('%s/%s', outdir,name);
        mp4_to_mat(in_path, out_path,framerate,f_size);
    end
end
