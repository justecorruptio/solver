WIKITIONARY_DUMP = '/Users/jay/Downloads/enwiktionary-20180701-pages-articles.xml'
ns = '{http://www.mediawiki.org/xml/export-0.10/}'

from HTMLParser import HTMLParser
import codecs
import re
from anagram import Anagram
import xml.etree.cElementTree as ET

ns_page = ns + 'page'
ns_title = ns + 'title'
ns_text = ns + 'text'


class WikiParser(object):
    def __init__(self, dump):
        #self.et = ET.iterparse(dump)
        self.anagram = Anagram()
        #self.fh = codecs.open(dump, 'r', 'utf-8')
        self.fh = open(dump, 'r')

    '''
    def __iter__(self):

        title = None
        text = None

        for event, elem in self.et:
            if elem.tag == ns_title:
                title = elem.text
                if not self.qualified(title):
                    title = None
            elif elem.tag == ns_text:
                text = elem.text
            elif elem.tag == ns_page:
                if not title or not text:
                    continue
                defi = self.parse_text(text)
                if defi:
                    yield title, defi

                title = None
                text = None
    '''
    def __iter__(self):
        title = None
        text = ''
        started = False

        d = False

        #self.fh.seek(1113985280)
        for cnt, line in enumerate(self.fh):

            if not started:
                match = re.search(r'<title>(.*?)</title>', line)
                if match:
                    title = match.group(1)
                    #if title == 'zillionaire':
                    #    d = True
                    #if d: print title, text
                    if not self.qualified(title):
                        title = None

            if '<text xml:space=' in line:
                text = line
                started = True

            if started:
                text += line
                if '</text>' in line:
                    started = False
                    if not title or not text:
                        title = None
                        text = ''
                        continue
                    defi = self.parse_text(title, text)
                    if defi:
                        yield title, defi
                    #if d:
                    #    print title, defi
                    #    1/0

                    title = None
                    text = ''

            #if cnt % 1000000 == 0:
            #    print "TELL", self.fh.tell()

    def qualified(self, title):
        if not re.match('^[a-z]{2,15}$', title):
            return False

        upper = title.upper()
        if upper not in self.anagram.words:
            return False

        return True

    def handle_template(self, match_obj):
        data = match_obj.group(1)
        if '|' not in data:
            return data
        parts = data.split('|')
        if not parts:
            return ''

        name = parts.pop(0).lower().strip()

        F = []
        args = {}
        for part in parts:
            if '=' in part:
                k, v = part.split('=', 1)
                args[k] = v
            else:
                F.append(part)

        if F:
            L = '{_' + F[0] + '_}'
        else:
            L = ''

        if name in (
            'lb', 'lbl', 'label',
            'defdate', 'senseid', 'anchor',
            'qualifier', 'q', 'qual',
            'cite-book', 'cite-web', 'isbn',
            'topics', 'top',
            '+preo', 'jump', 'gloss', 'rfex',
            'rfc-sense', 'rfquote-sense', 'sense', 'rfc-def', 'rfdef',
            'tcx',
            'attention', 'syndiff',
            'def-date', 'defdt',
            'circa', 'c.', 'circa2', 'b.c.e.',
            'tlb', '&lit',
            'c',
        ):
            return ''
        elif name.startswith('r:'):
            return ''

        elif name in (
            'non-gloss definition', 'n-g', 'ngd', 'def', 'non-gloss',
            'l', 'w', 'i', 'vern',
            'unsupported', 'nowrap',
            'ipachar',
            'pedia', 'smallcaps', 'keyword',
        ):
            return F[0]

        elif name in ('m',):
            return F[1]

        elif name in ('latn-def',):
            return F[2]

        elif name == 'soplink':
            return ' '.join(F)

        elif name == 'en-past of':
            return 'simple past tense and past participle of ' + L
        elif name == 'en-simple past of':
            return 'simple past tense of ' + L
        elif name.startswith('en-'):
            return name[3:-3] + ' form of ' + L
        elif name.endswith(' of'):
            return name + ' ' + L
        elif name in ('alt form', 'altform'):
            return 'alternative form of ' + L
        elif name in ('altname',):
            return 'synonym of ' + L
        elif name in ('short for',):
            return 'short for ' + L
        elif name in ('clipping',):
            return 'clipping of ' + L
        elif name in ('altcaps',):
            return 'alternative letter-case form of ' + L
        elif name in ('only used in',):
            return 'only used in ' + L
        elif name in ('altspell', 'standspell', 'alt-sp', 'altspelling'):
            return 'alternative spelling of ' + L
        elif name in ('eye dialect'):
            return 'eye dialect spelling of ' + L
        elif name in ('pronunciation spelling'):
            return 'pronunciation spelling of ' + L

        elif name == 'taxlink':
            return '"' + F[0] + '"'
        elif name in ('si-unit', 'si-unit-2', 'si-unit-np'):
            return 'SI unit of ' + F[2]
        elif name == 'nuclide':
            return 'a nuclide'
        elif name == 'frac':
            return 'a fraction of'
        elif name == 'chem':
            return 'a chemical'
        elif name == 'etyl':
            return '@L_' + F[0] + '@'
        elif name == 'cog':
            return '@L_' + F[0] + '@ ' + '"' + F[1] + '"'

        else:
            pass

        return ''

    def parse_text(self, title, text):
        text = text.replace('\n', '@_@')
        match = re.search(r'==English==.*?@_@# (.*?)(@_@.*|$)', text)
        if not match:
            return None

        text = match.group(1)
        while re.search(r'\{\{[dD]er\|', text):
            text = match.group(2)
            match = re.search(r'@_@# (.*?)(@_@.*|$)', text)
            if not match:
                return None
            text = match.group(1)

        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&quot;', '"')
        text = text.replace('&mdash;', '-')
        text = text.replace('&minus;', '-')
        #text = text.replace('&zwj;', '')
        #text = text.replace('&times;', u'\u00d7')
        #text = text.replace('&middot;', u'\u00b7')
        #text = text.replace('&hellip;', u'\u2026')
        text = text.replace('<text>', '')
        text = text.replace('</text>', '')

        text = re.sub(r'\[\[(Image|File):.*?\]\]', r'', text, flags=re.I)
        text = re.sub(r'\[\[[^\|\]]*?\|(.*?)\]\]', r'\1', text)
        text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)

        self._curr = (title, text)

        while re.search(r'\{\{.*\}\}', text):
            text = re.sub(r"""\{\{
                ([^\{\}]*)
            \}\}""", self.handle_template, text, flags=re.I|re.X)

        text = re.sub(r'@L_([a-z]+)@',
            lambda m: {
                'ang': 'Old English',
                'en': 'English',
                'fo': 'Faroese',
                'is': 'Icelandic',
                'la': 'Latin',
            }.get(m.group(1), 'LANG@@@@'),
            text,
        )

        text = re.sub(r'<ref.*?</ref>', ' ', text)
        text = re.sub(r'<ref.*?/>', ' ', text)
        text = re.sub(r'<sup>(.*?)</sup>', r'^[\1]', text, flags=re.I)
        text = re.sub(r'<sub>(.+?)</sub>', r'[\1]', text, flags=re.I)
        text = re.sub(r'<sup.*?\|Wp?</sup>', ' ', text)
        #text = re.sub(r'</?math>', ' ', text)
        text = re.sub(r'</?(big|small|b|i|div|span)[^>]*?>', ' ', text)
        text = re.sub(r'<!--.*?-->', ' ', text)
        text = re.sub(r'\([^\(\)]*?\)', ' ', text)
        text = re.sub(r'\([^\(\)]*?\)', ' ', text)

        text = re.sub(r'\(.*$', ' ', text)

        text = re.sub(r"''+", '', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r' ([\.;,:?!])', r'\1', text)
        text = re.sub(r'[;,:]$', r'.', text)
        text = re.sub(r'^\W+', '', text)
        text = re.sub(r'\.+$', '.', text)

        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
            if text[-1] != '.':
                text += '.'
        return text

if __name__ == '__main__':
    wiki = WikiParser(WIKITIONARY_DUMP)

    for title, text in wiki:
        pass
        '''
        if (
            '|' in text or '}}' in text or '</' in text or '\\' in text or
            '@@@@' in text or '&' in text
        ):
            print '==========' + title + '==========='
            print text
        '''

        print title.upper() + '\t' + text
