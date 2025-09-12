
# ResumeUploader Service Stub
# Accepts resume files (txt/pdf/doc/docx) and registers metadata
# UI integration can be added later


import os
from tpm_job_finder_poc.storage.secure_storage import SecureStorage

class ResumeUploader:
    """
    Service for uploading resumes and registering metadata.
    Accepts txt, pdf, doc, and docx formats. Includes file size detection, validation, error handling, and stubs for DB/cloud persistence.
    """
    SUPPORTED_TYPES = (".txt", ".pdf", ".doc", ".docx")

    def upload_resume(self, file_path, user_id=None):
        """
        Upload a resume file, validate format, detect file size, and register metadata.
        Args:
            file_path: Path to the resume file.
            user_id: Optional user identifier.
        Returns:
            metadata dict or error dict
        """
        if not os.path.isfile(file_path):
            return {"error": "File not found.", "file_path": file_path}
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_TYPES:
            return {"error": f"Unsupported file type: {ext}", "file_path": file_path}
        try:
            size = os.path.getsize(file_path)
        except Exception as e:
            from tpm_job_finder_poc.error_handler.handler import handle_error
            handle_error(e, context={'component': 'resume_uploader', 'method': 'upload_resume', 'file_path': file_path})
            size = None
        metadata = {
            "filename": os.path.basename(file_path),
            "type": ext.replace(".", ""),
            "size": size,
            "user_id": user_id,
            "file_path": file_path
        }
        # Use SecureStorage for persistence
        try:
            storage = SecureStorage()
            file_result = storage.save_file(file_path, metadata["filename"])
            meta_result = storage.save_metadata(metadata["filename"], metadata)
            return {"status": "uploaded", "metadata": metadata, "file_result": file_result, "meta_result": meta_result}
        except Exception as e:
            from tpm_job_finder_poc.error_handler.handler import handle_error
            handle_error(e, context={'component': 'resume_uploader', 'method': 'upload_resume', 'file_path': file_path})
            return {"error": str(e), "metadata": metadata}

    def register_metadata(self, metadata):
        """
        Register resume metadata in the system (stub).
        Args:
            metadata: Metadata dict from upload_resume.
        Returns:
            registration status (stub)
        """
        # TODO: Implement metadata registration (DB or file)
        return {"status": "registered (stub)", "metadata": metadata}

    # save_to_persistence is now handled by SecureStorage

    def find_resume(self, filename, search_dir="resumes"):
        """
        Locate a resume file by filename in the given directory.
        Args:
            filename: Name of the resume file to find.
            search_dir: Directory to search (default: 'resumes').
        Returns:
            Full file path if found, else None.
        """
        for root, _, files in os.walk(search_dir):
            if filename in files:
                return os.path.join(root, filename)
        return None

# Simple CLI for testing uploads
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ResumeUploader CLI")
    parser.add_argument("filename", help="Resume file name (in resumes/ directory)")
    parser.add_argument("--user_id", help="User ID", default=None)
    args = parser.parse_args()
    uploader = ResumeUploader()
    file_path = uploader.find_resume(args.filename)
    if not file_path:
        from tpm_job_finder_poc.error_handler.handler import handle_error
        handle_error(FileNotFoundError(f"File '{args.filename}' not found in resumes/ directory."), context={'component': 'resume_uploader_cli', 'filename': args.filename})
        print(f"File '{args.filename}' not found in resumes/ directory.")
    else:
        result = uploader.upload_resume(file_path, user_id=args.user_id)
        print(result)
