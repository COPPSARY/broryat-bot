import hashlib

from bot.utils.hashing import sha256_file


def test_sha256_file_matches_hashlib_reference(tmp_path):
    file_path = tmp_path / "sample.txt"
    content = b"the quick brown fox jumps over the lazy dog" * 1000
    file_path.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert sha256_file(file_path) == expected


def test_sha256_file_handles_empty_file(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_bytes(b"")
    assert sha256_file(file_path) == hashlib.sha256(b"").hexdigest()
