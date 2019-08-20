'''
    test_all_workflows.py  collects all the workflow test scripts and then runs them all in a test suite.
'''

import sys
sys.path.append("..")
                
import unittest

import test_readfiltering
import test_assembly
import test_comparison
import test_taxonomic_classification
import test_functional_inference
from workflows.download_offline_files import main_func

if __name__ == '__main__':
    main_func("all", "data", file_list="../workflows/config/offline_downloads.json")
    suite = unittest.TestLoader().loadTestsFromModule(test_readfiltering)
    unittest.TextTestRunner(verbosity=0).run(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_assembly)
    unittest.TextTestRunner(verbosity=0).run(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_comparison)
    unittest.TextTestRunner(verbosity=0).run(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_taxonomic_classification)
    unittest.TextTestRunner(verbosity=0).run(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_functional_inference)
    unittest.TextTestRunner(verbosity=0).run(suite)      
    
