# ResumeStore - Local Storage & Secure Metadata Stub

import os
from src.storage.secure_storage import SecureStorage
from typing import Optional, Dict, Any

class ResumeStore:
    """
    Local-only resume storage and metadata management for POC.
    Stubs for access control, secure metadata storage, retrieval, deletion, and audit logging.
    Ready for upgrade to database/object storage and encryption at rest.
    """
    def __init__(self, storage_dir="resumes", metadata_dir="resume_metadata"):
        self.storage = SecureStorage()

    def save_resume(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save resume file and metadata using SecureStorage.
        """
        try:
            file_name = metadata.get("filename", None)
            if not file_name:
                file_name = os.path.basename(file_path)
            file_path_saved = self.storage.save_file(file_path, file_name)
            meta_path_saved = self.storage.save_metadata(file_name, metadata)
            return {"status": "saved", "file": file_path_saved, "metadata": meta_path_saved}
        except Exception as e:
            return {"error": str(e)}

    def retrieve_resume(self, filename: str) -> Optional[str]:
        """
        Retrieve resume file by filename using SecureStorage.
        """
        return self.storage.retrieve_file(filename)

    def retrieve_metadata(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata JSON by filename using SecureStorage.
        """
        return self.storage.retrieve_metadata(filename)

    def delete_resume(self, filename: str) -> Dict[str, Any]:
        """
        Delete resume file and metadata using SecureStorage.
        """
        result = {}
        if self.storage.delete_file(filename):
            result["file_deleted"] = True
        if self.storage.delete_metadata(filename):
            result["metadata_deleted"] = True
        return result

    # --- Stubs for future features ---
    # Now handled by SecureStorage

    # --- API Stubs ---
    def api_save(self, file_path, metadata):
        return self.save_resume(file_path, metadata)

    def api_retrieve(self, filename):
        return self.retrieve_resume(filename)

    def api_delete(self, filename):
        return self.delete_resume(filename)

    def api_audit_log(self, action, details):
        self.storage.log_action(action, details)

# Example usage:
# store = ResumeStore()
# result = store.save_resume("resumes/my_resume.pdf", {"user_id": "123", "type": "pdf"})
# print(result)
