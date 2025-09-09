from src.storage.secure_storage import SecureStorage
import unittest
import tempfile
import os
from resume.store import ResumeStore

class TestResumeStore(unittest.TestCase):
    def setUp(self):
        self.store = ResumeStore()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_resume.txt")
        # Use SecureStorage to save the test file
        with open(self.test_file, "w") as f:
            f.write("Sample resume content.")
        storage = SecureStorage()
        storage.save_file(self.test_file, "test_resume.txt")
        self.metadata = {
            "filename": "test_resume.txt",
            "type": "txt",
            "user_id": "user123",
            "size": os.path.getsize(self.test_file)
        }

    def tearDown(self):
        # Clean up files and directories
        try:
            os.remove(self.test_file)
        except Exception:
            pass
        try:
            os.rmdir(self.test_dir)
        except Exception:
            pass
        # Remove stored resume and metadata using SecureStorage
        storage = SecureStorage()
        storage.delete_file("test_resume.txt")
        storage.delete_metadata("test_resume.txt")
        self.store.delete_resume("test_resume.txt")

    def test_save_and_retrieve_resume(self):
        result = self.store.save_resume(self.test_file, self.metadata)
        self.assertEqual(result["status"], "saved")
        retrieved = self.store.retrieve_resume("test_resume.txt")
        self.assertTrue(os.path.isfile(retrieved))
        meta = self.store.retrieve_metadata("test_resume.txt")
        self.assertEqual(meta["filename"], "test_resume.txt")

    def test_delete_resume(self):
        self.store.save_resume(self.test_file, self.metadata)
        del_result = self.store.delete_resume("test_resume.txt")
        self.assertTrue(del_result.get("file_deleted", False))
        self.assertTrue(del_result.get("metadata_deleted", False))
        self.assertIsNone(self.store.retrieve_resume("test_resume.txt"))
        self.assertIsNone(self.store.retrieve_metadata("test_resume.txt"))

    def test_error_handling_missing_file(self):
        result = self.store.save_resume("missing.txt", self.metadata)
        self.assertIn("error", result)

    def test_metadata_schema_validation(self):
        # Missing required field 'filename'
        bad_metadata = {"type": "txt", "user_id": "user123"}
        result = self.store.save_resume(self.test_file, bad_metadata)
        # Should still save, but you can add schema validation in ResumeStore
        self.assertEqual(result["status"], "saved")

    def test_directory_listing(self):
        self.store.save_resume(self.test_file, self.metadata)
        storage = SecureStorage()
        files = storage.list_files()
        self.assertIn("test_resume.txt", files)
        meta_files = storage.list_metadata()
        self.assertTrue(any(f.startswith("test_resume.txt") for f in meta_files))

if __name__ == "__main__":
    unittest.main()
