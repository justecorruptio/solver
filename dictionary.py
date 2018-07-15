class Dictionary(object):

    def __init__(self):
        self.defs = {}

        fh = open('definitions.txt', 'r')
        for line in fh:
            word, sense = line.strip().split('\t', 1)
            self.defs[word] = sense
