import unittest
import sys
sys.path.append('../controller')

from DocumentHelper import DocumentHelper

class TestDocumentHelper(unittest.TestCase):
    def setUp(self):
        # Setup that runs before each test method
        self.document_helper = DocumentHelper()


    def test_parse_filename(self):
         # Define your test cases
        test_cases = {
            "gemSpec_DS_Hersteller_V1.5.0.xlsx": ("gemSpec_DS_Hersteller", "1.5.0"),
            "gemSpec_Perf_V2.31.0.xlsx": ("gemSpec_Perf", "2.31.0"),
            "gemRL_Betr_TI_V2.9.0.xlsx": ("gemRL_Betr_TI", "2.9.0"),
            "gemSpec_IDP_FD_V1.6.0.xlsx": ("gemSpec_IDP_FD", "1.6.0"),
            "gemSpec_eRp_FdV_V1.8.0.xlsx": ("gemSpec_eRp_FdV", "1.8.0"),
            "gemSpec_SST_LD_BD_V1.4.0.xlsx": ("gemSpec_SST_LD_BD", "1.4.0"),
            "gemKPT_Betr_V3.26.1.xlsx": ("gemKPT_Betr", "3.26.1"),
            "gemProdT_eRp_FdV_PTV_1.6.2-0_V1.0.0.xlsx": ("gemProdT_eRp_FdV_PTV_1.6.2-0", "1.0.0")
        }

        # Test each case
        for filename, expected in test_cases.items():
            with self.subTest(filename=filename):
                spec_name, version =  self.document_helper.parse_filename(filename)
                self.assertEqual((spec_name, version), expected)
# This allows the test to be run from the command line
if __name__ == '__main__':
    unittest.main()