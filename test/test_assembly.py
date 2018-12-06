import unittest
import os
import subprocess


class TestAssembly(unittest.TestCase):
    '''
        Test the assembly workflows: assembly_workflow_metaspades, assembly_workflow_megahit, assembly_workflow_all
        We test by checking if the correct files are created at the end of the workflow.
    '''
    
    def setUp(self):
        os.chdir("../workflows/")
        SING_PATH = 'export SINGULARITY_BINDPATH="data:/tmp"' 
        subprocess.run([SING_PATH], shell=True)
     
    def test_assembly_workflow_metaspades(self):
        snakemake_command = "snakemake -p --verbose --core=6 --use-singularity --configfile=../test/test_assembly_workflow.json assembly_workflow_metaspades"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SSRR606249_subset10.trim2_metaspades.contigs.fa")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10.trim30_metaspades.contigs.fa")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))  
             
    def test_assembly_workflow_megahit(self):
        snakemake_command = "snakemake -p --verbose --core=6 --use-singularity --configfile=../test/test_assembly_workflow.json assembly_workflow_megahit"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SSRR606249_subset10.trim2_megahit.contigs.fa")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10.trim30_megahit.contigs.fa")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))    
        
    def test_assembly_workflow_all(self):
        snakemake_command = "snakemake -p --verbose --core=6 --use-singularity --configfile=../test/test_assembly_workflow.json assembly_workflow_all"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname, "data/SSRR606249_subset10.trim2_megahit.contigs.fa")
        filename_2 = os.path.join(dirname, "data/SRR606249_subset10.trim30_megahit.contigs.fa")
        filename_3 = os.path.join(dirname, "data/SSRR606249_subset10.trim2_metaspades.contigs.fa")
        filename_4 = os.path.join(dirname, "data/SRR606249_subset10.trim30_metaspades.contigs.fa")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2) and os.path.isfile(filename_3) and os.path.isfile(filename_4) )  
        
if __name__ == '__main__':
    unittest.main()        
 