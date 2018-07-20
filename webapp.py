import os
import web
import re
import sys
import time

abspath = os.path.abspath(os.path.dirname(__file__))

os.chdir(abspath)
sys.path.append(abspath)

from anagram import Anagram
from dictionary import Dictionary

anagram = Anagram()
dictionary = Dictionary()

urls = (
    '/?', 'index',
    '/d/([a-zA-Z]+)/?', 'definition',
    '/t(?:est)?/([-a-zA-Z_]{2,3})/?', 'test',
    '/([a-zA-Z]+)/?', 'api',
)
app = web.application(urls, globals())

header = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet" type="text/css">
        <style>
            textarea {
                min-height: 150px !important;
                resize: vertical !important;
            }
            #small {
                padding-top: 50px;
            }
            .mono {
                font-family: "Lucida Console", Monaco, monospace;
            }
        </style>
    </head>
    <body>
"""

footer = """
    </body></html>
"""

index_template = """
    <div class="container-fluid"><div class="row">
    <div class="col-sm-12"><h3>Anagram/Snatch Solver</h3></div>
    <div class="col-sm-12">
        <form id="qform" action="" method="post">
            <div class="form-group">
            <textarea class="form-control" name="q" autofocus>%s</textarea>
            </div>
            <div class="form-group">
            <button class="btn btn-default" type="submit">Solve!</button>
            </div>
        </form>
    </div>

    </div>
    <div class="row">%s</div>
    <div class="row" id="small"><div class="col-xs-12">
        <small>Generated in %0.4f secs.<small>
    </div></div>
    </div>
"""

test_template = """
    <div class="container-fluid mono"><div class="row">
    <div class="col-sm-12"><h3>Scrabble Test: %s</h3></div>
    <div class="col-sm-12">
        <form id="qform" action="" method="post">
            <div class="form-group">
            <textarea class="form-control" name="q" rows="10" autofocus>%s</textarea>
            </div>
            <div class="form-group">
            <button class="btn btn-default" type="submit">Check!</button>
            </div>
        </form>
    </div>

    </div>
    <div class="row">%s</div>
    <div class="row" id="small"><div class="col-xs-12">
        <small>Generated in %0.4f secs.<small>
    </div></div>
    </div>
"""

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
            result_str = []
        else:
            if len(data) == 1:
                result = anagram.extend(data[0])
            else:
                result = anagram.snatch(data)

            if not result:
                result_str = [col('No Solution!')]
            else:
                result_str = []
                for combo, built in result:
                    result_str += [col(fmt(combo, built))]

        for word in data:
            if len(word) <= 1:
                continue
            if word not in anagram.lookup(word):
                result_str.insert(0, col(word + ' is not a word', klass='bg-danger'))

        end_time = time.time()

        return (header + index_template + footer) % (
            form_q, ''.join(result_str), end_time - start_time,
        )

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
        return (header + test_template + footer) % (
            query, "", "", 0,
        )

    def POST(self, query):
        start_time = time.time()
        regex = re.sub(r'[-_]', '.', query)
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

        result = []
        for word, is_missing in sorted(missing + extra):
            result.append(col(word, is_missing and 'text-info' or 'text-danger'))

        if not result:
            result = col('Perfect!', 'text-success')

        end_time = time.time()

        return (header + test_template + footer) % (
            query, form_q, ''.join(result), end_time - start_time,
        )



application = app.wsgifunc()


if __name__ == "__main__":
    app.run()
