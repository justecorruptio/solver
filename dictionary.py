import re


class Dictionary(object):

    def __init__(self):
        self.defs = {}

        fh = open('definitions.txt', 'r')
        for line in fh:
            word, sense = line.strip().split('\t', 1)
            self.defs[word] = sense

    def lookup(self, word):
        if word not in self.defs:
            return None

        sense = self.defs[word]

        links = list(set(re.findall(r'\{_([^_]+)_\}', sense)))
        sense = [re.sub('\{_([^_]+)_\}', r'\1', sense)]
        for link in links:
            link = link.upper()
            if link not in self.defs:
                continue
            linked = re.sub('\{_([^_]+)_\}', r'\1', self.defs[link])
            sense.append(linked)

        return ' '.join(sense)


