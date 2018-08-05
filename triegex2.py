from copy import deepcopy
import pprint
import sre_parse

class ConjexParser(object):
    def __init__(self, pattern):
        self.pattern = pattern

        tree = sre_parse.parse(pattern).data
        self.tree = self._clean(tree)

    def _clean(self, tree):
        for i, (name, args) in enumerate(tree):
            if name == 'literal':
                tree[i] = ('_', chr(args))
            elif name == 'in':
                tree[i] = ('|', [[branch] for branch in self._clean(args)])
            elif name == 'branch':
                tree[i] = ('|', map(self._clean, args[1]))
            elif name == 'subpattern':
                res = self._clean(args[1])
                if len(res) == 1:
                    tree[i] = res[0]
                else:
                    tree[i] = ('|', [res])
            elif name.endswith('repeat'):
                a = args[0]
                b = min(args[1], 16)
                tree[i] = ('@', self._clean(args[2]), a, b)
            elif name == 'range':
                tree[i] = ('-', chr(args[0]), chr(args[1]))
            elif name == 'negate':
                raise NotImplemented()
                tree[i] = ('^',)
            elif name == 'any':
                tree[i] = ('.',)
            elif name == 'at':
                tree[i] = ({'at_beginning': '^', 'at_end': '$'}[args],)
            else:
                raise NotImplemented()

        to_and = []
        buff = []
        for i, node in enumerate(tree):
            if node == ('_', '&'):
                to_and.append(buff)
                buff = []
            else:
                buff.append(node)
        to_and.append(buff)

        if len(to_and) > 1:
            tree[:] = [('&', to_and)]

        return tree

class TrieNode(object):
    __slots__ = ['terminal', 'children']

    def __init__(self):
        self.terminal = False
        self.children = {}

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def __repr__(self):
        return '(%s, %s)' % (self.terminal, self.children)

class State(object):
    def __init__(self, ptrs):
        self.op = None
        self.children = []

        self.ptrs = set(ptrs)

    def split(self, op, num):
        self.children = [deepcopy(self) for i in xrange(num)]
        self.op = op
        self.ptrs = None
        return self.children

    def merge(self):
        if self.op == '|' and all(c.op is None for c in self.children):
            self.op = None
            self.ptrs = set()
            #for child in self.children:
            #    print "--", child.op, child.ptrs
            for child in self.children:
                self.ptrs |= child.ptrs
            self.children = []

    def step(self, charset, inv=False, execute=True):
        if self.op is None:
            new_ptrs = set()
            accepted_chars = {}
            for ptr in self.ptrs:
                for char, child in ptr.children.iteritems():
                    if (not inv) == (char in charset):
                        accepted_chars[char] = child
                        new_ptrs.add(child)
            if execute:
                self.ptrs = new_ptrs
            return accepted_chars

        elif self.op == '&':
            children_accepted_chars = [c.step(charset, inv=inv, execute=False) for c in self.children]
            good_chars = reduce(lambda a, b: set(a) & set(b), children_accepted_chars)
            if good_chars:
                for child in self.children:
                    child.step(good_chars, False)
            else:
                self.op = None
                self.ptrs = set()
                self.children = []

            return good_chars

        elif self.op == '|':
            children_accepted_chars = [c.step(charset, inv=inv) for c in self.children]
            good_chars = reduce(lambda a, b: set(a) | set(b), children_accepted_chars)

            return good_chars

    def close(self):
        if self.op is None:
            return set(filter(None, [ptr.terminal for ptr in self.ptrs]))

        elif self.op == '&':
            children_ptrs = [c.close() for c in self.children]
            if not all(children_ptrs):
                return set()
            return reduce(lambda a, b: a | b, children_ptrs)

        elif self.op == '|':
            children_ptrs = [c.close() for c in self.children]
            return reduce(lambda a, b: a | b, children_ptrs)


class Triegex(object):
    def __init__(self):
        self.root = TrieNode()

    def add(self, word):
        ptr = self.root
        for c in word:
            if c not in ptr.children:
                ptr.children[c] = TrieNode()
            ptr = ptr.children[c]
        ptr.terminal = word

    def __repr__(self):
        def _recur(ptr, indent=-1, c=None):
            ret = ''
            if c:
                ret = ' ' * indent + c
            if ptr.terminal:
                ret += '.' * max(9 - indent, 1) + ptr.terminal
            if ret:
                ret += '\n'
            for c, child in sorted(ptr.children.iteritems()):
                ret += _recur(child, indent + 1, c)
            return ret

        return _recur(self.root)

    def matchex(self, conjex):
        parser = ConjexParser(conjex)
        cj_tree = parser.tree

        state = State([self.root])

        def _recur(cj_ptr, in_state):
            for node in cj_ptr:
                name = node[0]
                if name == '_':
                    in_state.step(node[1])
                elif name == '.':
                    in_state.step('', inv=True)
                elif name in '&|':
                    sub_states = in_state.split(name, len(node[1]))
                    for sub_node, sub_state in zip(node[1], sub_states):
                        _recur(sub_node, sub_state)
                elif name == '@':
                    low, high = node[2], node[3]
                    sub_states = in_state.split('|', high - low + 1)
                    for i, sub_state in enumerate(sub_states):
                        for j in xrange(low + i):
                            _recur(node[1], sub_state)
                in_state.merge()

        _recur(cj_tree, state)
        return sorted(state.close())


if __name__ == '__main__':
    cp = ConjexParser(r'..(I&Y).')

    #print cp.tree

    trie = Triegex()

    '''
    for w in """
        CAD
        CAR
        CARD
        CARE
        CATE
        CARET
        CARS
        CART
        CAT
        CATS
        CAM
        CAMS
        CAYS
        CIG

        CAA BAA CAAAAA BAAAAA CAAA B
        XY ZW
        CBCB
        CB
    """.split():
        trie.add(w)
    '''
    for w in """
        ABC BAD
    """.split():
        trie.add(w)

    #print trie.matchex('(C&B).*')
    print trie.matchex('..(C&D)')
