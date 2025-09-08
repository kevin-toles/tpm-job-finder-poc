import unittest
import tempfile
import os
import pandas as pd
from import_excel import import_excel_records

class TestImportExcel(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "Job ID": [1, 2],
            "Title": ["Engineer", "Manager"],
            "Score": [95, 80]
        })
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        self.df.to_excel(self.temp_file.name, index=False)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_import_all_columns(self):
        records = import_excel_records(self.temp_file.name)
        self.assertEqual(len(records), 2)
        self.assertIn("Job ID", records[0])
        self.assertIn("Title", records[0])
        self.assertIn("Score", records[0])

    def test_import_selected_columns(self):
        records = import_excel_records(self.temp_file.name, columns=["Title", "Score"])
        self.assertEqual(len(records), 2)
        self.assertIn("Title", records[0])
        self.assertIn("Score", records[0])
        self.assertNotIn("Job ID", records[0])

    def test_empty_file(self):
        temp_empty = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        pd.DataFrame().to_excel(temp_empty.name, index=False)
        temp_empty.close()
        records = import_excel_records(temp_empty.name)
        self.assertEqual(records, [])
        os.unlink(temp_empty.name)

if __name__ == "__main__":
    unittest.main()
