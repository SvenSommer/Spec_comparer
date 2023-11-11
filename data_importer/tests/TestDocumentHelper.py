import unittest
import sys
sys.path.append('../controller')

from DocumentHelper import DocumentHelper

class TestDocumentHelper(unittest.TestCase):
    def setUp(self):
        # Setup that runs before each test method
        self.document_helper = DocumentHelper("data/")


    def test_parse_filename(self):
         # Define your test cases
        test_cases = {
            "gemSpec_DS_Hersteller_V1.5.0.xlsx": ("gemSpec_DS_Hersteller", "1.5.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSpec_Perf_V2.31.0.xlsx": ("gemSpec_Perf", "2.31.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemRL_Betr_TI_V2.9.0.xlsx": ("gemRL_Betr_TI", "2.9.0", "Richtlinien", "Spezifikationsdokumente"),
            "gemSpec_IDP_FD_V1.6.0.xlsx": ("gemSpec_IDP_FD", "1.6.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSpec_eRp_FdV_V1.8.0.xlsx": ("gemSpec_eRp_FdV", "1.8.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSpec_SST_LD_BD_V1.4.0.xlsx": ("gemSpec_SST_LD_BD", "1.4.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemKPT_Betr_V3.26.1.xlsx": ("gemKPT_Betr", "3.26.1", "Konzepte", "Spezifikationsdokumente"),
            "gemProdT_eRp_FdV_PTV_1.6.2-0_V1.0.0.xlsx": ("gemProdT_eRp_FdV_PTV_1.6.2-0", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemSpec_VZD_FHIR_Directory_V1.3.0.xlsx": ("gemSpec_VZD_FHIR_Directory", "1.3.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemAnbT_VPN_ZugD_ATV_1.2.9_V1.0.0.xlsx": ("gemAnbT_VPN_ZugD_ATV_1.2.9", "1.0.0", "Anbietertyp Steckbrief", "Steckbriefe"),
            "gemProdT_VPN_ZugD_PTV_1.8.10-0_V1.0.0.xlsx": ("gemProdT_VPN_ZugD_PTV_1.8.10-0", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemSpec_VPN_ZugD_V1.22.0.xlsx": ("gemSpec_VPN_ZugD", "1.22.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemVZ_Afo_BetrEig_VSDM_FD_1.3.1_V1.0.0.xlsx": ("gemVZ_Afo_BetrEig_VSDM_FD_1.3.1", "1.0.0", "Verzeichnis", "Steckbriefe"),
            "gemProdT_Intermediaer_VSDM_PTV_1.6.8-0_V1.0.0.xlsx": ("gemProdT_Intermediaer_VSDM_PTV_1.6.8-0", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemProdT_FD_VSDM_PTV_1.7.3-0_V1.0.0.xlsx": ("gemProdT_FD_VSDM_PTV_1.7.3-0", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemProdT_FD_VSDM_PTV_1.7.3-1_V1.0.0.xlsx": ("gemProdT_FD_VSDM_PTV_1.7.3-1", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemSpec_eGK_Fach_VSDM_V1.2.1.xlsx": ("gemSpec_eGK_Fach_VSDM", "1.2.1", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSpec_SST_FD_VSDM_V1.7.0.xlsx": ("gemSpec_SST_FD_VSDM", "1.7.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSpec_SST_VSDM_V2.5.0.xlsx": ("gemSpec_SST_VSDM", "2.5.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemAnbT_FD_VSDM_nonGKV_ATV_1.0.1_V1.0.0.xlsx": ("gemAnbT_FD_VSDM_nonGKV_ATV_1.0.1", "1.0.0", "Anbietertyp Steckbrief", "Steckbriefe"),
            "gemProdT_FD_VSDM_nonGKV_PTV_1.0.1-0_V1.0.0.xlsx": ("gemProdT_FD_VSDM_nonGKV_PTV_1.0.1-0", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemSpec_VZD_FHIR_Directory_V1.2.0.xlsx": ("gemSpec_VZD_FHIR_Directory", "1.2.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSpec_VZD_FHIR_Directory_V1.3.0.xlsx": ("gemSpec_VZD_FHIR_Directory", "1.3.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemProdT_VZD_FHIR_PTV_1.1.0-1_V1.0.0.xlsx": ("gemProdT_VZD_FHIR_PTV_1.1.0-1", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemProdT_VZD_PTV_1.6.2-0_V1.0.0.xlsx": ("gemProdT_VZD_PTV_1.6.2-0", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemProdT_VZD_PTV_1.6.3-0_V1.0.0.xlsx": ("gemProdT_VZD_PTV_1.6.3-0", "1.0.0", "Produkttyp Steckbrief", "Steckbriefe"),
            "gemSpec_VZD_V1.15.0.xlsx": ("gemSpec_VZD", "1.15.0", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSpec_VZD_V1.15.0_1.xlsx": ("gemSpec_VZD", "1.15.0_1", "Spezifikationen", "Spezifikationsdokumente"),
            "gemSST_PS_eRp_verordnend_V_1.4.0-0_V1.1.0.xlsx": ("gemSST_PS_eRp_verordnend_V_1.4.0-0", "1.1.0", "Schnittstelle", "Steckbriefe"),
            "gemSST_PS_eRp_abgebend_V_1.5.0-0_V1.0.0.xlsx": ("gemSST_PS_eRp_abgebend_V_1.5.0-0", "1.0.0", "Schnittstelle", "Steckbriefe"),
            "gemSpec_Zugangsgateway_Vers_V1.52.0.xlsx": ("gemSpec_Zugangsgateway_Vers", "1.52.0", "Spezifikationen", "Spezifikationsdokumente"),
           "gemSpec_Authentisierung_Vers_V1.6.0.xlsx": ("gemSpec_Authentisierung_Vers", "1.6.0", "Spezifikationen", "Spezifikationsdokumente"),
        }

        # Test each case
        for filename, expected in test_cases.items():
            with self.subTest(filename=filename):
                spec_name, version, subtype, cattype =  self.document_helper.parse_filename(filename)
                self.assertEqual((spec_name, version, subtype, cattype), expected)
# This allows the test to be run from the command line
if __name__ == '__main__':
    unittest.main()