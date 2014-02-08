cleaner = onCleanup(@() exit);
shotnum={shotnum};
nstart={nstart};
nstop={nstop};
input_fn='{input_fn}';
output_dir='{output_dir}';
cd ../region_proposals/
segmentation = xtrac_segment(input_fn, output_dir, shotnum, nstart, nstop);
exit;

