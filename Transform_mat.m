global maindir
maindir = '/mnt/datadrive/CILVR';
maindata = sprintf('%s/youtube', maindir);

f_size=64;

dir_list = dir(maindata);

for k = 1:length(dir_list)
    dir_name = dir_list(k).name;
    if (strfind(dir_name, '.'))
        continue;
    end
    mov_list = dir(sprintf('%s/%s/*.mp4', maindata, dir_name));
    fprintf('Entering directory %s with %d movies \n', dir_name, length(mov_list))
    for j = 1:length(mov_list) 
        file_path = sprintf('%s/%s/%s', maindata, dir_name, mov_list(j).name);
        name = mov_list(j).name;
        name = name(1:(strfind(name, '.') - 1));
        out_path=sprintf('%s/%s/%s', maindata, dir_name, name);
        mp4_to_mat(file_path, out_path,f_size);
    end
end