IMAGE_MIME_TYPES = frozenset({"image/png", "image/jpeg"})


def is_image_mime(mime_type: str) -> bool:
    return mime_type in IMAGE_MIME_TYPES
