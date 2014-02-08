cleaner = onCleanup(@() exit);
shotnum=0;
nstart=1;
nstop=187;
input_fn='/home/tom/frames/automobile/NnqJXHlChoM/NnqJXHlChoM_%08d.jpg';
output_dir='/home/tom/segment/automobile/NnqJXHlChoM';
cd ../region_proposals/
segmentation = xtrac_segment(input_fn, output_dir, shotnum, nstart, nstop);
exit;

