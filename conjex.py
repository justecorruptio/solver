from itertools import chain
import re
import time


class Conjex(object):
    def __init__(self):
        self.all = [[] for i in xrange(16)]

    def add(self, word):
        self.all[len(word)].append(word)

    def clean_pat(self, pat):
        pat = pat.upper()
        pat = pat.replace(' ', '')
        pat = pat.replace('_', '(.*)')
        match = re.match(r'([^<>=\d]+)(>\d+)?(<\d+)?(=\d+)?', pat)
        if not match:
            return '.', 0, 0
        min_len = 0
        max_len = 15
        pat, a, b, c = match.groups()
        if a:
            min_len = int(a[1:])
        if b:
            max_len = int(b[1:]) - 1
        if c:
            min_len = max_len = int(c[1:])

        return pat, min_len, max_len

    def matchex(self, pat):

        pat, min_len, max_len = self.clean_pat(pat)

        parts = pat.split('&')
        all_matches = []
        for part in parts:
            matches = {}
            regex = re.compile('^' + part + '$')
            for word in chain(*self.all[min_len : max_len + 1]):
                match = regex.match(word)
                if match:
                    groups = match.groups() or (word,)
                    matches[groups] = word
            all_matches.append(matches)

        intersect = reduce(
            lambda a, b: a & b,
            (set(z.iterkeys()) for z in all_matches),
        )

        union = []
        for k in sorted(intersect):
            for z in all_matches:
                union.append(z[k])

        return union

if __name__ == '__main__':

    a = time.time()
    cj = Conjex()
    with open('owl3.txt', 'r') as fh:
        for line in fh:
            word = line.strip().upper()
            cj.add(word)
    b = time.time()
    print b - a

    a = time.time()
    res = cj.matchex(r'')
    b = time.time()
    print b - a
    print res
