from dataclasses import dataclass

from services.upload_guard import exceeds_upload_limit, upload_limit_message


@dataclass
class FakeUploadedFile:
    name: str
    size: int


def test_exceeds_upload_limit_false_for_small_file():
    small = FakeUploadedFile(name="switch.log", size=1024)
    assert exceeds_upload_limit(small) is False


def test_exceeds_upload_limit_true_for_oversized_file():
    huge = FakeUploadedFile(name="switch.log", size=500 * 1024 * 1024)
    assert exceeds_upload_limit(huge) is True


def test_exceeds_upload_limit_false_at_exactly_the_limit():
    from services.upload_guard import MAX_UPLOAD_BYTES

    exact = FakeUploadedFile(name="sensor.csv", size=int(MAX_UPLOAD_BYTES))
    assert exceeds_upload_limit(exact) is False


def test_upload_limit_message_includes_filename_and_size():
    huge = FakeUploadedFile(name="rack22.csv", size=100 * 1024 * 1024)
    message = upload_limit_message(huge)

    assert "rack22.csv" in message
    assert "100.0 MB" in message
