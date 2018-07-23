class Freq(object):
    def __init__(self, anagrams, freq_list):

        self.ranks = {}
        curr_rank = 1

        fh = open(freq_list, 'r')
        for line in fh:
            cnt, word, pos, _ = line.strip().split()
            word = word.upper()
            cnt = int(cnt)

            if word not in anagrams.words:
                continue

            if word in self.ranks:
                continue

            self.ranks[word] = curr_rank
            curr_rank += 1

        fh.close()
