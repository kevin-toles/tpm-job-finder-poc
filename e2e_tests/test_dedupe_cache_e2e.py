import os
from src.cache.dedupe_cache import DedupeCache
import tempfile
import uuid

def test_e2e_dedupe_cache_workflow():
    db_file = tempfile.NamedTemporaryFile(delete=False)
    cache = DedupeCache(db_file.name)
    user_id = str(uuid.uuid4())
    url1 = "https://example.com/job/5"
    url2 = "https://example.com/job/6"
    hash1 = "jkl012"
    hash2 = "mno345"
    # Add first job
    assert not cache.is_duplicate(user_id, url1, hash1)
    cache.add(user_id, url1, hash1)
    assert cache.is_duplicate(user_id, url1, hash1)
    # Add second job
    assert not cache.is_duplicate(user_id, url2, hash2)
    cache.add(user_id, url2, hash2)
    assert cache.is_duplicate(user_id, url2, hash2)
    # Clear and check
    cache.clear()
    assert not cache.is_duplicate(user_id, url1, hash1)
    assert not cache.is_duplicate(user_id, url2, hash2)
    db_file.close()
    os.unlink(db_file.name)
