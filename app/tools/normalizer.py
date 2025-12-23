import unicodedata


ZERO_WIDTH = dict.fromkeys(range(0x200B, 0x2010), None)


def normalize_text(s: str) -> str:
    if not s:
        return s

    s = unicodedata.normalize('NFKC', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Cf')
    s = s.translate(ZERO_WIDTH)
    s = s.replace('\u00A0', ' ')

    return s
