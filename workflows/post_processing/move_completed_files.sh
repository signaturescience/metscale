#!/bin/bash

#script to move finished samples and outputs to subdir
echo "Beginning move operation"
input_dir=$1

if [ ! -d $input_dir ]; then
	mkdir $input_dir
fi
shift
for f in "$@"
do
	echo "Moving $f"
	short_file=${f#*/}
	mv $f $input_dir/$short_file
done
echo "Done move operation"