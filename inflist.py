class InfList(object):
    def __init__(self, fn):
        self.fn = fn

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.fn(index)
        elif isinstance(index, slice):
            start, stop, step = index.start or 0, index.stop, index.step or 1

            if stop is not None:
                return [self.fn(i) for i in range(start, stop, step)]
            else:
                return InfList(lambda i: self.fn(i * step + start))

        else:
            raise TypeError('List indexes must be integers or slices')

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
