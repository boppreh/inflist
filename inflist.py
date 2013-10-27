class InfList(object):
    def __init__(self, fn):
        self.fn = fn

    def __getitem__(self, index):
        return self.fn(index)

if __name__ == '__main__':
    l = InfList(lambda n: n * 2)
    assert l[10] == 20
