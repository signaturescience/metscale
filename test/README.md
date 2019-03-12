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
sudo singularity build --sandbox ubuntu.simg ubuntu.def
sudo singularity exec --writable ubuntu.simg  mkdir /metag/metagenomics/workflows/data
sudo singularity shell --writable --bind data:/metag/metagenomics/workflows/data   ubuntu.simg
snakemake --use-singularity  --verbose -p --singularity-args "-H /" read_filtering_posttrim_workflow