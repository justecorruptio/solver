import json
import os
import web
import random
import re
import sys
import time

web.config.debug = True

abspath = os.path.abspath(os.path.dirname(__file__))

os.chdir(abspath)
sys.path.append(abspath)

from anagram import Anagram
from game import game_template
from dictionary import Dictionary
from freq import Freq

from templates import (
    header,
    footer,
    timed_footer,
    index_template,
    test_template,
)

anagram = Anagram('owl3.txt')
dictionary = Dictionary()
uncommon = Freq(anagram, 'uncommon.txt')

urls = (
    '/?', 'index',
    '/d/([a-zA-Z]+)/?', 'definition',
    '/t(?:est)?/([-a-zA-Z_]{2,3})/?', 'test',
    '/game/?', 'game',
    '/([a-zA-Z]+)/?', 'api',
)
app = web.application(urls, globals())


def col(s, klass=''):
    return '<div class="col-xs-12 col-sm-6 col-lg-3 %s">%s</div>\n' % (klass, s)

def fmt(combo, built):
    ret = ''
    for c in combo:
        words = ' + '.join(w for w in combo if len(w) > 1)
        letters = ' '.join(w for w in combo if len(w) == 1)
    return ' + '.join(filter(None, [words, letters])) + ' = ' + built

class index(object):
    def GET(self):
        start_time = time.time()
        form = web.input(q='')
        form_q = re.sub(r'[^a-zA-Z\n]', ' ', form.q)
        form_q = re.sub(r'[ \t]+', ' ', form_q)
        form_q = re.sub(r'\s*\n\s*', '\n', form_q)
        form_q = form_q.upper().strip()

        data = form_q.split()
        if not data or len(''.join(data)) < 4:
            rows = []
        else:
            if len(data) == 1:
                result = anagram.extend(data[0])
            else:
                result = anagram.snatch(data)

            if not result:
                rows = [col('No Solution!')]
            else:
                rows = []
                for combo, built in result:
                    rows += [col(fmt(combo, built))]

        for word in data:
            if len(word) <= 1:
                continue
            if word not in anagram.words:
                rows.insert(0, col(word + ' is not a word!', klass='bg-danger'))

        if len(data) == 1 and word in anagram.words:
                rows.insert(0, col(word + ' is word!', klass='bg-success'))

        end_time = time.time()
        elapsed = end_time - start_time
        rows = ''.join(rows)

        return (header + index_template + timed_footer).format(**locals())

    POST = GET

class api(object):
    def GET(self, word):
        return '\n'.join(w for _, w in anagram.extend(word.upper())) + '\n'

class definition(object):
    def GET(self, word):
        return (dictionary.lookup(word.upper()) or 'No definition found!') + '\n'

class test(object):
    def GET(self, query):
        regex_q = re.sub(r'[-_]', '.', query)
        form_q = ''
        rows = ''
        elapsed = 0.0
        return (header + test_template + timed_footer).format(**locals())

    def POST(self, query):
        start_time = time.time()
        regex = re.sub(r'[-_]', '.', query)
        regex = regex.upper().strip()
        regex = '^' + regex + '$'

        form = web.input(q='')
        form_q = re.sub(r'[^a-zA-Z\n]', ' ', form.q)
        form_q = re.sub(r'[ \t]+', ' ', form_q)
        form_q = re.sub(r'\s*\n\s*', '\n', form_q)
        form_q = form_q.upper().strip()

        data = set(form_q.split())
        correct = set(
            word for word in anagram.words
            if re.match(regex, word)
        )

        missing = [(word, True) for word in correct - data]
        extra = [(word, False) for word in data - correct]

        rows = []
        for word, is_missing in sorted(missing + extra):
            rows.append(col(word, is_missing and 'text-info' or 'text-danger'))

        if not rows:
            rows = [col('Perfect!', 'text-success')]

        rows.append(col('%d Total' % (len(correct),)))

        end_time = time.time()
        elapsed = end_time - start_time
        rows = ''.join(rows)

        return (header + test_template + timed_footer).format(**locals())


possible_questions = set()
for hx, words in anagram.data.iteritems():
    word = words[0]
    if len(word) < 4 or len(word) > 7:
        continue
    if not any(w in uncommon.ranks for w in words):
        continue
    for i, c in enumerate(word):
        rest = word[:i] + word[i + 1:]
        subs = anagram.lookup(rest)
        for sub in subs:
            if word == sub + c:
                continue
            possible_questions.add((sub, c))
possible_questions = list(possible_questions)

class game(object):
    def _gen_question(self):
        pass

    def GET(self):
        return (header + game_template + footer).format(**locals())

    def POST(self):
        form = web.input(curr_score=0, input='', question='', time_left=0, time_upper=0)
        question = form['question']
        inp = form['input'].upper().strip()
        curr_score = int(form['curr_score'])
        time_left = int(form['time_left'])
        time_upper = int(form['time_upper'])

        time_unused = 1000 - (time_upper - time_left)

        match = re.match(r'([A-Z]+) \+ ([A-Z]+)', question)
        if not match:
            return json.dumps({
                'question': '%s + %s = ?' % random.choice(possible_questions),
                'score': 0,
                'new_time_upper': 1000,
            })

        sub, c = match.groups()
        if not (
            sub in anagram.words and
            anagram.hash(sub) * anagram.hash(c) == anagram.hash(inp) and
            inp in anagram.words
        ):
            raise web.notfound()

        return json.dumps({
            'question': '%s + %s = ?' % random.choice(possible_questions),
            'score': curr_score + int([0, 1, 3, 9, 27][len(inp) - 3] * time_unused / 100),
            'new_time_upper': min(2000, time_left + [0, 80, 120, 200, 500][len(inp) - 3]),
        })


application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
