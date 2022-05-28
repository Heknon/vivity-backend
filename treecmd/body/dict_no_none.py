class DictNoNone(dict):
    def __init__(self, seq=None, **kwargs):
        kwargs = filter(lambda item: item[1] is not None, kwargs.items())
        super().__init__(**dict(kwargs))

    def __setitem__(self, key, value):
        if key in self or value is not None:
            dict.__setitem__(self, key, value)
