'''
    test_all_workflows.py  collects all the workflow test scripts and then runs them all in a test suite.
'''
import unittest
import test_readfiltering
import test_assembly
import test_comparison
import test_taxonomic_classification


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(test_readfiltering)
    unittest.TextTestRunner(verbosity=0).run(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_assembly)
    unittest.TextTestRunner(verbosity=0).run(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_comparison)
    unittest.TextTestRunner(verbosity=0).run(suite)
    suite = unittest.TestLoader().loadTestsFromModule(test_taxonomic_classification)
    unittest.TextTestRunner(verbosity=0).run(suite)    
    
