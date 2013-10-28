class InfList(object):
    def __init__(self, fn):
        self.fn = fn
        self.replacements = {}

    def _interpret_index(self, index, in_replacements=False):
        if isinstance(index, int):
            return (index,)
        elif isinstance(index, slice) and index.stop is not None:
            return range(index.start or 0, index.stop, index.step or 1)
        elif isinstance(index, slice) and in_replacements:
            stop = max(self.replacements)
            return self._interpret_index(slice(index.start, stop, index.step))
        elif isinstance(index, list) or isinstance(index, tuple):
            return index
        else:
            raise TypeError('List indexes must be integers, finite slices or\
lists, received {}: {}.'.format(type(index), index))

    def __getitem__(self, index):
        if isinstance(index, int):
            if index in self.replacements:
                return self.replacements[index]
            else:
                return self.fn(index)

        elif isinstance(index, slice) and index.stop is None:
            start, step = index.start or 0, index.step or 1
            # Use bracket notation instead of calling self.fn directly so we
            # can use the replacement dictionary.
            return InfList(lambda i: self[i * step + start])

        return [self.fn(i) for i in self._interpret_index(index)]

    def __setitem__(self, index, value):
        if isinstance(index, int):
            self.replacements[index] = value
            return

        indexes = self._interpret_index(index, True)
        try:
            for i in indexes:
                self.replacements[i] = value[i]
        except TypeError:
            for i in indexes:
                self.replacements[i] = value

    def __delitem__(self, index):
        for i in self._interpret_index(index, True):
            del self.replacements[i]

    def __contains__(self, item):
        i = 0
        while True:
            if item == self.fn(i):
                return i
            i += 1

    def __iter__(self):
        i = 0
        while True:
            yield self.fn(i)
            i += 1

if __name__ == '__main__':
    l = InfList(lambda n: n * 2)
    assert l[10] == 20
    assert 6 in l

    for value in l:
        if value > 7:
            assert value == 8
            break

    assert l[2:4] == [4, 6]
    assert l[:4] == [0, 2, 4, 6]
    assert l[:4:2] == [0, 4]

    assert type(l[1:]) is InfList
    assert l[1:][0] == l[1]

    assert l[(1, 2, 3)] == l[1:4]
    assert l[[1, 2, 3]] == l[1:4]

    l[5] = 'a'
    assert l[5] == 'a'
    del l[5]
    assert l[5] == 10
