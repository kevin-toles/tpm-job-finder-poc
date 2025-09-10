import os
from cache.dedupe_cache import DedupeCache
import tempfile
import uuid

def test_regression_duplicate_url_and_hash():
    db_file = tempfile.NamedTemporaryFile(delete=False)
    cache = DedupeCache(db_file.name)
    user_id = str(uuid.uuid4())
    url = "https://example.com/job/4"
    hash_ = "ghi789"
    cache.add(user_id, url, hash_)
    # Regression: should detect duplicate by either url or hash
    assert cache.is_duplicate(user_id, url)
    assert cache.is_duplicate(user_id, hash_=hash_)
    db_file.close()
    os.unlink(db_file.name)
