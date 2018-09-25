import json
import os
import web
import random
import re
import sys
import time
import uuid

web.config.debug = True

abspath = os.path.abspath(os.path.dirname(__file__))

os.chdir(abspath)
sys.path.append(abspath)

from anagram import Anagram
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
    '/t(?:est)?/?', 'test',
    '/([,a-zA-Z]+)/?', 'api',
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
        word = word.upper()
        if ',' in word:
            return json.dumps([w for _, w in anagram.snatch(word.split(','))])
        else:
            return json.dumps([w for _, w in anagram.extend(word)])

class definition(object):
    def GET(self, word):
        return (dictionary.lookup(word.upper()) or 'No definition found!') + '\n'

class test(object):
    def GET(self):
        form_q = ''
        rows = ''
        elapsed = 0.0
        pattern = ''
        return (header + test_template + timed_footer).format(**locals())

    def POST(self):
        start_time = time.time()
        form = web.input(q='', pattern='')
        pattern = form.pattern.upper().strip()

        form_q = re.sub(r'[^a-zA-Z\n]', ' ', form.q)
        form_q = re.sub(r'[ \t]+', ' ', form_q)
        form_q = re.sub(r'\s*\n\s*', '\n', form_q)
        form_q = form_q.upper().strip()

        data = set(form_q.split())
        correct = set(anagram.conjex.matchex(pattern))

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

application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
