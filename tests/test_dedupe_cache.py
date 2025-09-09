import os
from src.cache.dedupe_cache import DedupeCache
import tempfile
import uuid

def test_add_and_check_duplicate():
    db_file = tempfile.NamedTemporaryFile(delete=False)
    cache = DedupeCache(db_file.name)
    user_id = str(uuid.uuid4())
    url = "https://example.com/job/1"
    hash_ = "abc123"
    assert not cache.is_duplicate(user_id, url, hash_)
    cache.add(user_id, url, hash_)
    assert cache.is_duplicate(user_id, url, hash_)
    db_file.close()
    os.unlink(db_file.name)

def test_clear_cache():
    db_file = tempfile.NamedTemporaryFile(delete=False)
    cache = DedupeCache(db_file.name)
    user_id = str(uuid.uuid4())
    url = "https://example.com/job/2"
    cache.add(user_id, url)
    assert cache.is_duplicate(user_id, url)
    cache.clear()
    assert not cache.is_duplicate(user_id, url)
    db_file.close()
    os.unlink(db_file.name)
