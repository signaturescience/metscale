###Running unit tests
Currently we have individual tests for each rule in a workflow per file.
There is also test_all_workflows that will runs all the files in the workflow.
We can run all these files from the command line:
python test_all_workflows.py

There is also a docker file with a Centos OS to duplicate our clients environment 
docker build -t "centos" .


docker run --entrypoint "python" centos test_all_workflow.py
or
sudo docker run -it --privileged "centos" /bin/bash



Build and run a docker container:

docker run --privileged -it centos /bin/bash

cd ../workflows/
python download_offline_files.py --workflow test_files read_filtering assembly comparison

export SINGULARITY_BINDPATH="data:/tmp"

snakemake -p --verbose --cores --use-singularity comparison_output_heatmap_plots_reads_workflow

 

Build and run a singularity container:

Note that this builds a container that mounts via chroot and all the files in it are root:root.

Because of permission issues it may be necessary to execute the container as root to modify it(or maybe chown all of /metag).

sudo singularity build --sandbox centos.simg centos.def

singularity exec --writable centos.simg  mkdir /metag/metagenomics/workflows/data

sudo singularity shell --writable --bind data:/metag/metagenomics/workflows/data   centos.simg

. /metag/miniconda3/bin/activate metag

snakemake --use-singularity  --verbose -p --singularity-args "-H /" read_filtering_posttrim_workflow

Tried to create an image then build a sandbox from it. Getting some problems with snakemake not seeing singularity.
