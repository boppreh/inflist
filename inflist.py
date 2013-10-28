import operator

class InfList(object):
    def __init__(self, fn=lambda i: i):
        self.fn = fn
        self.replacements = {}

    def _interpret_index(self, index, in_replacements=False):
        if isinstance(index, int):
            return (index,)
        elif isinstance(index, slice) and index.stop is not None:
            return range(index.start or 0, index.stop, index.step or 1)
        elif isinstance(index, slice) and in_replacements:
            stop = max(self.replacements) + 1
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

        # Same here.
        return [self[i] for i in self._interpret_index(index)]

    def __setitem__(self, index, value):
        if isinstance(index, int):
            self.replacements[index] = value
            return

        indexes = self._interpret_index(index, True)
        try:
            for i in indexes:
                self.replacements[i] = value[i]
        except (TypeError, IndexError):
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

    def map(self, transformation):
        return InfList(lambda i: transformation(self[i]))

    def __eq__(self, other):
        return (isinstance(other, InfList) and
                self.fn == other.fn and
                self.replacements == other.replacements)

    def __str__(self):
        return 'InfList[{},...]'.format(','.join(map(str, self[:5])))

for binop in ['add', 'sub', 'mul', 'truediv', 'floordiv', 'lt', 'le',  'ge',
              'gt', 'and', 'or', 'lshift', 'rshift', 'pow', 'xor']:
    name = '__' + binop + '__'
    function = getattr(operator, name)
    def op_method(self, other, f=function):
        if hasattr(other, '__getitem__'):
            return InfList(lambda i: f(self[i], other[i]))
        else:
            return InfList(lambda i: f(self[i], other))
    setattr(InfList, name, op_method)


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

    l[10:20] = 'b'
    assert l[10:20] == ['b'] * 10
    del l[10:15]
    assert l[10:16] == [20, 22, 24, 26, 28, 'b']
    del l[15, 16]
    assert l[15, 16] == [30, 32]
    del l[17:]
    assert l[15:20] == [30, 32, 34, 36, 38]

    assert l.map(lambda x: x - 2)[:4] == [-2, 0, 2, 4]
    assert l[1:].map(lambda x: x - 2)[:4] == [0, 2, 4, 6]

    assert (l + 1)[:4] == [1, 3, 5, 7]
    assert (l / 2)[:4] == list(range(4))

    assert str(l) == 'InfList[0,2,4,6,8,...]'
