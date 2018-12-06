import unittest
import os
import subprocess


class TestReadFiltering(unittest.TestCase):
    '''
        Test the read filtering workflows: read_filtering_pretrim_workflow and read_filtering_posttrim_workflow
        We test by checking if the correct files are created at the end of the workflow.
    '''
#     @classmethod
#     def setUpClass(cls):
#         os.chdir("../workflows/")
#         subprocess.run('export SINGULARITY_BINDPATH="data:/tmp"')
    
    def setUp(self):
        os.chdir("../workflows/")
        SING_PATH = 'export SINGULARITY_BINDPATH="data:/tmp"' 
        subprocess.run([SING_PATH], shell=True)
        
    def test_read_filtering_pretrim_workflow(self):
        snakemake_command = "snakemake -p --verbose --core=6 --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_pretrim_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_1_reads_fastqc.zip")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_2_reads_fastqc.zip")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
        
    def test_read_filtering_posttrim_workflow(self):
        snakemake_command = "snakemake -p --verbose --core=6 --use-singularity --configfile=../test/test_readfilt_workflow.json read_filtering_posttrim_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SRR606249_subset10_2.trim30_fastqc.zip")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10_1.trim30_fastqc.zip")
        filename_3 = os.path.join(dirname, "data/SRR606249_subset10_2.trim2_fastqc.zip")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10_1.trim2_fastqc.zip")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) )
  
if __name__ == '__main__':
    unittest.main()
