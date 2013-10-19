function save_image(img, name, f_size)        
    global maindir
    subdir = sprintf('%s/img_%d_%d', maindir, f_size, f_size);    
    finalname = sprintf('%s/%s.png', subdir, name);
    imwrite(img, finalname);
    fprintf('Saved %s\n', finalname);
end