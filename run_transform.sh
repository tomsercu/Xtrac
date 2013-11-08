#!/bin/bash
matlab -nodisplay -singleCompThread <Transform_mat.m 2>&1 | tee ./transform_output/$1
