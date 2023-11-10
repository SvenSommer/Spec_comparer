class SpecificationType:
    def get_spec_type(self, spec_name):
        if spec_name.startswith('gemKPT_'):
            return 'Konzepte', 'Spezifikationsdokumente'
        elif spec_name.startswith('gemSysL_'):
            return 'Systemlösung', 'Spezifikationsdokumente'
        elif spec_name.startswith('gemSpec_'):
            return 'Spezifikationen', 'Spezifikationsdokumente'
        elif spec_name.startswith('gemF_'):
            return 'Feature-Spezifikationen', 'Spezifikationsdokumente'
        elif spec_name.startswith('gemILF_'):
            return 'Implementierungsleitfaden', 'Spezifikationsdokumente'
        elif spec_name.startswith('gemRL_'):
            return 'Richtlinien', 'Spezifikationsdokumente'
        elif spec_name.startswith('gemProdT_'):
            return 'Produkttyp Steckbrief', 'Steckbriefe'
        elif spec_name.startswith('gemAnbT_'):
            return 'Anbietertyp Steckbrief', 'Steckbriefe'
        elif spec_name.startswith('gemAnw_'):
            return 'Anwendungssteckbrief', 'Steckbriefe'
        elif spec_name.startswith('gemILF_'):
            return 'Implementierungsleitfaden', 'Spezifikationsdokumente'
        elif spec_name.startswith('gemVZ_'):
            return 'Verzeichnis', 'Steckbriefe'
        elif spec_name.startswith('gemSST_'):
            return 'Schnittstelle', 'Steckbriefe'
        else:
            return 'Unbekannt', 'Unbekannt'