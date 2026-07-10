from bot.utils.file_types import MAX_FILE_SIZE_BYTES


def test_max_file_size_is_20_megabytes():
    assert MAX_FILE_SIZE_BYTES == 20 * 1024 * 1024
