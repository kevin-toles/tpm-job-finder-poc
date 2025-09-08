import unittest
import tempfile
import os
from resume.uploader import ResumeUploader

class TestResumeUploader(unittest.TestCase):
    def setUp(self):
        self.uploader = ResumeUploader()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_resume.txt")
        with open(self.test_file, "w") as f:
            f.write("Sample resume content.")

    def tearDown(self):
        os.remove(self.test_file)
        os.rmdir(self.test_dir)

    def test_upload_valid_file(self):
        result = self.uploader.upload_resume(self.test_file, user_id="user123")
        self.assertEqual(result["status"], "uploaded")
        self.assertEqual(result["metadata"]["type"], "txt")
        self.assertEqual(result["metadata"]["size"], os.path.getsize(self.test_file))

    def test_upload_unsupported_format(self):
        bad_file = os.path.join(self.test_dir, "resume.exe")
        with open(bad_file, "w") as f:
            f.write("Not a resume.")
        result = self.uploader.upload_resume(bad_file)
        self.assertIn("error", result)
        self.assertIn("Unsupported file type", result["error"])
        os.remove(bad_file)

    def test_upload_missing_file(self):
        result = self.uploader.upload_resume(os.path.join(self.test_dir, "missing.txt"))
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])

    def test_find_resume(self):
        found = self.uploader.find_resume("test_resume.txt", search_dir=self.test_dir)
        self.assertEqual(found, self.test_file)
        not_found = self.uploader.find_resume("not_here.txt", search_dir=self.test_dir)
        self.assertIsNone(not_found)

if __name__ == "__main__":
    unittest.main()
