def ensure_utf8(s):
    """
    unicode to ascii
    u'\u554a'->'\xe5\x95\x8a'
    """
    if not isinstance(s, basestring):
        return str(s)
    if isinstance(s, unicode):
        return s.encode("u8")
    return s


def ensure_unicode(s):
    """
    ascii to unicode
    '\xe5\x95\x8a'->u'\u554a'
    """
    if not isinstance(s, basestring):
        return unicode(s)
    if isinstance(s, str):
        return s.decode("u8")
    return s
