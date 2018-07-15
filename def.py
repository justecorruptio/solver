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
                    defi = self.parse_text(text)
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

    def parse_text(self, text):
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

        text = re.sub(r"""\{\{
            (?:[wl])
            (?:\|[^\|\{\}]*?)* \|([^\|\{\}]*?)
        \}\}""", r'\1', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            (?:[ilm]|keyword|smallcaps|ipachar|pedia|unsupported|vern)
            (?:\|.*?)? \|([^\|]*?)
        \}\}""", r'\1', text, flags=re.I|re.X)

        '''
        text = re.sub(
            r'\{\{(?:[i]|unsupported)\|(.*?)\}\}', r'\1', text,
            flags=re.I,
        )
        '''

        text = re.sub(r"""\{\{(?:
            C\.|circa2
        ).*?\}\}""", '', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            taxlink
            \|([^\|\}]*?)(:?\|.*?)?\}\}
        """, r'"\1"', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{(?:
            lb|lbl|label|defdate|senseid|\+preo|anchor|topics|qualifier
            |q|qual|attention|top|jump|tcx|rfex|Rfc-sense|altname|defdate
            |Rfquote-sense|def-date|syndiff|defdt|Tlb|&Lit|sense|c|Rfc-def
        )\|.*?\}\}""", '', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            (
                [^-\|\}]*?of
            )\s?
            \|([^\|\}]*?) (:?\|[^\|\{\}]*?)* \}\}
        """, r'\1 \2', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            (?:en-)?(
                alt\sform|short\sfor|clipping|Only\sused\sin|Altcaps
                |alt-sp|altspell|altform|Eye\sdialect|Pronunciation\sspelling|
                [^|^}]*?of
            )\s?
            \|([^\|\}]*?) (:?\|[^\|\{\}]*?)* \}\}
        """, lambda m: (
            {
                'alt form': 'alternate form of',
                'altform': 'alternate form of',
                'altcaps': 'alternate letter-case form of',
                'past of': 'simple past tense and past participle of',
                'simple past of': 'simple past tense of',
                'short for': 'short for',
                'clipping': 'Clipping of',
                'only used in': 'Only used in',
                'altspell': 'Alternative spelling of',
                'alt-sp': 'Alternative spelling of',
                'eye dialect': 'Eye dialect spelling of',
                'pronunciation spelling': 'Pronunciation spelling of',
                'comparative of': 'comparative form of',
                'superlative of': 'superlative form of',
                'third-person singular of':
                    'third-person singular simple present indicative form of',
            }.get(m.group(1).lower(), m.group(1)) + ' ' + m.group(2)
        ), text, flags=re.I|re.X)


        text = re.sub(r"""\{\{
            si-unit(?:-2|-np)?
            \|[^\|\}]*? \|[^\|\}]*?
            \|([^\|\}]*?)
            (:?\|.*?)?\}\}
        """, r'Scientific unit of \1', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            lati?n-def
            \|[^\|\}]*? \|[^\|\}]*?
            \|([^\|\}]*?)
            (:?\|.*?)?\}\}
        """, r'\1', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            cog
            \|([^\|\}]*?)
            \|([^\|\}]*?)
            (:?\|.*?)?\}\}
        """, r'@L_\1@ "\2"', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            etyl
            \|([^\|\}]*?)
            (:?\|.*?)?\}\}
        """, r'@L_\1@', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            soplink
            \|([^\|\}]*?)
            \|([^\|\}]*?)
            (:?\|.*?)?\}\}
        """, r'\1 \2', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            etyl
            \|([^\|\}]*?)
            (:?\|.*?)?\}\}
        """, r'@L_\1@', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            (?:standspell|Altspelling)
            \|[^\|\}]*?
            \|([^\|\}]*?)
            (:?\|.*?)?\}\}
        """, r'alternative spelling of \1', text, flags=re.I|re.X)

        # Giving up
        text = re.sub(r"""\{\{
            frac \|.*? \}\}
        """, r'a fraction of', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            nuclide \|.*? \}\}
        """, r'a nuclide', text, flags=re.I|re.X)

        text = re.sub(r"""\{\{
            chem \|.*? \}\}
        """, r'a chemical', text, flags=re.I|re.X)

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

        text = text.replace('{{nbsp}}', ' ')
        text = re.sub(r'\{\{([^\|\}]+)\}\}', r'\1', text)

        text = re.sub(r"""\{\{(?:
                gloss
            )
            \|.*?
            \}\}
            """, r'', text,
            flags=re.I|re.X,
        )

        text = re.sub(r"""\{\{(?:
                def|Non-gloss\sdefinition|Ngd|n-g|non-gloss
            )
            \|(.*?)
            \}\}
            """, r'\1', text,
            flags=re.I|re.X,
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
