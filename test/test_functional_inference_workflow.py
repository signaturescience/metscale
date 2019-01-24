import unittest
import os
import subprocess


class TestFunctionalInference(unittest.TestCase):
    '''
        Test the functional inference workflows: 
        We test by checking if the correct files/dirs are created at the end of the workflow.
    '''
#     @classmethod
#     def setUpClass(cls):
#         os.chdir("../workflows/")
#         subprocess.run('export SINGULARITY_BINDPATH="data:/tmp"')
    
    def setUp(self):
        os.chdir("../workflows/")
        os.environ['SINGULARITY_BINDPATH'] = "data:/tmp"
        
    def test_1_functional_inference_prokka_with_megahit_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_functional_inference.json functional_inference_prokka_with_megahit_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filedir_1 = os.path.join(dirname,  "data/SRR606249_subset10_trim30_megahit.prokka_annotation")
        filedir_2 = os.path.join(dirname,  "data/SRR606249_subset10_trim2_megahit.prokka_annotation")
        self.assertTrue(os.path.isdir(filedir_1) and os.path.isdir(filedir_2))
        
    def test_2_functional_inference_prokka_with_metaspades_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_functional_inference.json functional_inference_prokka_with_metaspades_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filedir_1 = os.path.join(dirname,  "data/SRR606249_subset10_trim30_metaspades.prokka_annotation")
        filedir_2 = os.path.join(dirname,  "data/SRR606249_subset10_trim2_metaspades.prokka_annotation")
        self.assertTrue(os.path.isdir(filedir_1) and os.path.isdir(filedir_2))
        
    def test_3_functional_inference_abricate_with_megahit_workflow(self):
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_functional_inference.json functional_inference_abricate_with_megahit_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_trim30_megahit_abricate.csv")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_trim2_megahit_abricate.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))        
     
    def test_4_functional_inference_abricate_with_metaspades_workflow(self):    
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_functional_inference.json functional_inference_abricate_with_metaspades_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_trim30_metaspades_abricate.csv")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_trim2_metaspades_abricate.csv")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))
        
    def test_5_functional_inference_with_srst2_workflow(self):    
        snakemake_command = "snakemake -q --cores --use-singularity --configfile=../test/test_functional_inference.json ffunctional_inference_with_srst2_workflow"
        subprocess.run([snakemake_command], shell=True)
        dirname = os.getcwd()
        filename_1 = os.path.join(dirname,  "data/SRR606249_subset10_trim2.srst2__genes__ARGannot.r1__results.txt")
        filename_2 = os.path.join(dirname,  "data/SRR606249_subset10_trim30.srst2__genes__ARGannot.r1__results.txt")
        self.assertTrue(os.path.isfile(filename_1) and os.path.isfile(filename_2))       
        



if __name__ == '__main__':
    unittest.main()        
