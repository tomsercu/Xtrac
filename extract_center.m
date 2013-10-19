function img = extract_center(img, f_size)
    s1 = min(size(img, 1), size(img, 2));
    s2 = max(size(img, 1), size(img, 2));
    r1 = (ceil((s2 - s1) / 2)) : (floor((s2 + s1) / 2));
    r2 = 1:s1;
    if (size(img, 1) < size(img, 2))
        img = img(r2, r1, :);
    else
        img = img(r1, r2, :);
    end   
    img = imresize(img, [f_size, f_size]);    
    img = double(img);
    img = img / 255;
end