from rag.mime import IMAGE_MIME_TYPES, is_image_mime


def test_is_image_mime_recognizes_png_and_jpeg() -> None:
    assert is_image_mime("image/png")
    assert is_image_mime("image/jpeg")
    assert not is_image_mime("application/pdf")
    assert IMAGE_MIME_TYPES == frozenset({"image/png", "image/jpeg"})
