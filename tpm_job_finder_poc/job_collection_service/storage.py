"""
Job Collection Service - Storage implementation.

Handles persistence and retrieval of job postings with search capabilities.
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pathlib import Path

from tpm_job_finder_poc.shared.contracts.job_collection_service import (
    JobPosting,
    JobQuery,
    JobType
)

logger = logging.getLogger(__name__)


class JobStorage:
    """
    Job storage implementation for persisting and retrieving job postings.
    
    Provides file-based storage with JSON serialization and search capabilities.
    """
    
    def __init__(self, storage_path: str = "./job_storage"):
        """
        Initialize job storage.
        
        Args:
            storage_path: Directory path for storing job files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.jobs_dir = self.storage_path / "jobs"
        self.indices_dir = self.storage_path / "indices"
        self.metadata_dir = self.storage_path / "metadata"
        
        for dir_path in [self.jobs_dir, self.indices_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized job storage at {self.storage_path}")
    
    async def store_job(self, job: JobPosting) -> bool:
        """
        Store a single job posting.
        
        Args:
            job: Job posting to store
            
        Returns:
            True if job was stored successfully
        """
        try:
            # Create job file path
            job_file = self.jobs_dir / f"{job.id}.json"
            
            # Convert job to dict and serialize
            job_dict = job.to_dict()
            job_dict['stored_at'] = datetime.now().isoformat()
            
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_dict, f, indent=2, default=str)
            
            # Update indices
            await self._update_indices(job)
            
            logger.debug(f"Stored job {job.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing job {job.id}: {e}")
            return False
    
    async def store_jobs(self, jobs: List[JobPosting]) -> int:
        """
        Store multiple job postings.
        
        Args:
            jobs: List of job postings to store
            
        Returns:
            Number of jobs successfully stored
        """
        stored_count = 0
        
        for job in jobs:
            if await self.store_job(job):
                stored_count += 1
        
        logger.info(f"Stored {stored_count}/{len(jobs)} jobs")
        return stored_count
    
    async def get_job(self, job_id: str) -> Optional[JobPosting]:
        """
        Retrieve a job posting by ID.
        
        Args:
            job_id: ID of the job to retrieve
            
        Returns:
            JobPosting if found, None otherwise
        """
        try:
            job_file = self.jobs_dir / f"{job_id}.json"
            
            if not job_file.exists():
                return None
            
            with open(job_file, 'r', encoding='utf-8') as f:
                job_dict = json.load(f)
            
            return self._dict_to_job_posting(job_dict)
            
        except Exception as e:
            logger.error(f"Error retrieving job {job_id}: {e}")
            return None
    
    async def search_jobs(self, query: JobQuery) -> List[JobPosting]:
        """
        Search stored job postings.
        
        Args:
            query: Search query parameters
            
        Returns:
            List of matching job postings
        """
        try:
            matching_jobs = []
            
            # Get all job files
            job_files = list(self.jobs_dir.glob("*.json"))
            
            for job_file in job_files:
                try:
                    with open(job_file, 'r', encoding='utf-8') as f:
                        job_dict = json.load(f)
                    
                    if self._matches_query(job_dict, query):
                        job_posting = self._dict_to_job_posting(job_dict)
                        matching_jobs.append(job_posting)
                        
                except Exception as e:
                    logger.warning(f"Error reading job file {job_file}: {e}")
                    continue
            
            # Sort by date_posted (newest first)
            matching_jobs.sort(
                key=lambda job: job.date_posted or datetime.min,
                reverse=True
            )
            
            # Apply limit if specified
            if query.max_jobs_per_source and query.max_jobs_per_source > 0:
                matching_jobs = matching_jobs[:query.max_jobs_per_source]
            
            logger.info(f"Found {len(matching_jobs)} jobs matching query")
            return matching_jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []
    
    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job posting.
        
        Args:
            job_id: ID of the job to delete
            
        Returns:
            True if job was deleted successfully
        """
        try:
            job_file = self.jobs_dir / f"{job_id}.json"
            
            if not job_file.exists():
                return False
            
            job_file.unlink()
            
            # Update indices
            await self._remove_from_indices(job_id)
            
            logger.debug(f"Deleted job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            return False
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            # Count total jobs
            job_files = list(self.jobs_dir.glob("*.json"))
            total_jobs = len(job_files)
            
            # Count jobs from today
            today = date.today()
            jobs_today = 0
            oldest_job_date = None
            newest_job_date = None
            
            for job_file in job_files[:100]:  # Sample first 100 for performance
                try:
                    with open(job_file, 'r', encoding='utf-8') as f:
                        job_dict = json.load(f)
                    
                    # Check if job is from today
                    stored_at = job_dict.get('stored_at')
                    if stored_at:
                        try:
                            stored_date = datetime.fromisoformat(stored_at).date()
                            if stored_date == today:
                                jobs_today += 1
                            
                            # Track date range
                            if oldest_job_date is None or stored_date < oldest_job_date:
                                oldest_job_date = stored_date
                            if newest_job_date is None or stored_date > newest_job_date:
                                newest_job_date = stored_date
                                
                        except ValueError:
                            pass
                            
                except Exception:
                    continue
            
            # Calculate storage size
            storage_size_bytes = sum(
                f.stat().st_size for f in self.storage_path.rglob('*') if f.is_file()
            )
            storage_size_mb = storage_size_bytes / (1024 * 1024)
            
            return {
                "total_jobs": total_jobs,
                "jobs_today": jobs_today,
                "storage_size_mb": round(storage_size_mb, 2),
                "oldest_job_date": oldest_job_date.isoformat() if oldest_job_date else None,
                "newest_job_date": newest_job_date.isoformat() if newest_job_date else None,
                "storage_path": str(self.storage_path),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {
                "total_jobs": 0,
                "jobs_today": 0,
                "storage_size_mb": 0,
                "error": str(e)
            }
    
    def _matches_query(self, job_dict: Dict[str, Any], query: JobQuery) -> bool:
        """Check if job matches search query."""
        # Keywords filter
        if query.keywords:
            title = job_dict.get('title', '').lower()
            company = job_dict.get('company', '').lower()
            
            # Check if any keyword matches title or company
            keywords_match = any(
                keyword.lower() in title or keyword.lower() in company
                for keyword in query.keywords
            )
            
            if not keywords_match:
                return False
        
        # Location filter
        if query.location:
            job_location = job_dict.get('location', '')
            if not job_location:
                if not query.include_remote:
                    return False
            else:
                location_match = (
                    query.location.lower() in job_location.lower() or
                    (query.include_remote and 'remote' in job_location.lower())
                )
                if not location_match:
                    return False
        
        # Sources filter
        if query.sources:
            job_source = job_dict.get('source', '')
            if job_source not in query.sources:
                return False
        
        # Date range filter
        if query.date_range_days > 0:
            stored_at = job_dict.get('stored_at')
            if stored_at:
                try:
                    stored_date = datetime.fromisoformat(stored_at)
                    cutoff_date = datetime.now() - timedelta(days=query.date_range_days)
                    if stored_date < cutoff_date:
                        return False
                except ValueError:
                    pass
        
        return True
    
    def _dict_to_job_posting(self, job_dict: Dict[str, Any]) -> JobPosting:
        """Convert job dictionary to JobPosting object."""
        # Parse date_posted
        date_posted = job_dict.get('date_posted')
        if isinstance(date_posted, str):
            try:
                date_posted = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                date_posted = None
        
        # Parse aggregated_at
        aggregated_at = job_dict.get('aggregated_at')
        if isinstance(aggregated_at, str):
            try:
                aggregated_at = datetime.fromisoformat(aggregated_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                aggregated_at = None
        
        # Parse job_type
        job_type = job_dict.get('job_type')
        if isinstance(job_type, str):
            try:
                job_type = JobType(job_type)
            except ValueError:
                job_type = None
        
        return JobPosting(
            id=job_dict.get('id', ''),
            source=job_dict.get('source', ''),
            title=job_dict.get('title', ''),
            company=job_dict.get('company', ''),
            location=job_dict.get('location'),
            url=job_dict.get('url'),
            date_posted=date_posted,
            job_type=job_type,
            remote_friendly=job_dict.get('remote_friendly', False),
            tpm_keywords_found=job_dict.get('tpm_keywords_found', 0),
            raw_data=job_dict.get('raw_data'),
            aggregated_at=aggregated_at
        )
    
    async def _update_indices(self, job: JobPosting):
        """Update search indices for the job."""
        try:
            # Company index
            company_index_file = self.indices_dir / "companies.json"
            company_index = await self._load_index(company_index_file)
            
            if job.company not in company_index:
                company_index[job.company] = []
            if job.id not in company_index[job.company]:
                company_index[job.company].append(job.id)
            
            await self._save_index(company_index_file, company_index)
            
            # Source index
            source_index_file = self.indices_dir / "sources.json"
            source_index = await self._load_index(source_index_file)
            
            if job.source not in source_index:
                source_index[job.source] = []
            if job.id not in source_index[job.source]:
                source_index[job.source].append(job.id)
            
            await self._save_index(source_index_file, source_index)
            
        except Exception as e:
            logger.warning(f"Error updating indices for job {job.id}: {e}")
    
    async def _remove_from_indices(self, job_id: str):
        """Remove job from search indices."""
        try:
            # Company index
            company_index_file = self.indices_dir / "companies.json"
            company_index = await self._load_index(company_index_file)
            
            for company, jobs in company_index.items():
                if job_id in jobs:
                    jobs.remove(job_id)
            
            await self._save_index(company_index_file, company_index)
            
            # Source index
            source_index_file = self.indices_dir / "sources.json"
            source_index = await self._load_index(source_index_file)
            
            for source, jobs in source_index.items():
                if job_id in jobs:
                    jobs.remove(job_id)
            
            await self._save_index(source_index_file, source_index)
            
        except Exception as e:
            logger.warning(f"Error removing job {job_id} from indices: {e}")
    
    async def _load_index(self, index_file: Path) -> Dict[str, List[str]]:
        """Load an index file."""
        try:
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Error loading index {index_file}: {e}")
            return {}
    
    async def _save_index(self, index_file: Path, index_data: Dict[str, List[str]]):
        """Save an index file."""
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving index {index_file}: {e}")


# Add missing import for timedelta
from datetime import timedelta