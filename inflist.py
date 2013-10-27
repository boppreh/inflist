class InfList(object):
    def __init__(self, fn):
        self.fn = fn

    def __getitem__(self, index):
        return self.fn(index)

    def __contains__(self, item):
        i = 0
        while True:
            if item == self.fn(i):
                return i
            i += 1

if __name__ == '__main__':
    l = InfList(lambda n: n * 2)
    assert l[10] == 20
    assert 6 in l
