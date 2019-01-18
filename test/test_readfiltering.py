import unittest
import os
import contextlib
import subprocess
import sys



class TestReadFiltering(unittest.TestCase):
    '''
        Test the read filtering workflows: read_filtering_pretrim_workflow and read_filtering_posttrim_workflow
        We test by checking if the correct files are created at the end of the workflow.
        Replace cores with the number of cores to run
    '''

    
    def setUp(self):
        os.chdir("../workflows/")
        os.environ['SINGULARITY_BINDPATH'] = "data:/tmp"
       
    def test_1_read_filtering_pretrim_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_pretrim_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_fastqc.zip")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_2_reads_fastqc.zip")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
 
    def test_2_read_filtering_posttrim_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_posttrim_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_trim2_1.fq.gz")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_trim2_2.fq.gz")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_trim30_1.fq.gz")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_trim30_2.fq.gz")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) )
        
    def test_3_read_filtering_multiqc_workflow(self):
        snakemake_command = "snakemake -q --core=6 --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_multiqc_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd() 
        filename = os.path.join(dirname, "data/SRR606249_subset10_fastqc_multiqc_report.html")
        self.assertTrue(os.path.isfile(filename)   
  
if __name__ == '__main__':
    unittest.main()
