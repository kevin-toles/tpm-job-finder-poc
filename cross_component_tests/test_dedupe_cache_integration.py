import os
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache
import tempfile
import uuid

def test_multi_user_deduplication():
    db_file = tempfile.NamedTemporaryFile(delete=False)
    cache = DedupeCache(db_file.name)
    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())
    url = "https://example.com/job/3"
    hash_ = "def456"
    cache.add(user1, url, hash_)
    assert cache.is_duplicate(user1, url, hash_)
    assert not cache.is_duplicate(user2, url, hash_)
    cache.add(user2, url, hash_)
    assert cache.is_duplicate(user2, url, hash_)
    db_file.close()
    os.unlink(db_file.name)
