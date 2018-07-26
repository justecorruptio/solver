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
                for j, branch in enumerate(args[1]):
                    args[1][j] = self._clean(branch)
                tree[i] = ('|', args[1])
            elif name == 'subpattern':
                tree[i] =('|', [self._clean(args[1])])
            elif name.endswith('repeat'):
                a = args[0]
                b = min(args[1], 32)
                tree[i] = ('@', self._clean(args[2]), a, b)
            elif name == 'range':
                tree[i] = ('-', chr(args[0]), chr(args[1]))
            elif name == 'negate':
                raise NotImplemented()
                tree[i] = ('^',)
            elif name == 'any':
                tree[i] = ('.',)
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
            del tree[:]
            tree.append(('&', to_and))

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


class Trie(object):
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

    def match(self, pattern):

        ptrs = set([self.root])
        next = set()

        for c in pattern:
            if c == '.':
                for ptr in ptrs:
                    next.update(ptr.children.itervalues())
            else:
                for ptr in ptrs:
                    if c in ptr.children:
                        next.add(ptr.children[c])

            ptrs = next
            next = set()

        return sorted(filter(None, (ptr.terminal for ptr in ptrs)))

    def matchex(self, conjex):
        cj_tree = ConjexParser(conjex).tree

        def _recur(in_ptr, cj):
            ptrs = [in_ptr]
            next = set()
            for node in cj:
                name = node[0]
                if name == '_':
                    c = node[1]
                    for ptr in ptrs:
                        if c in ptr.children:
                            next.add(ptr.children[c])
                elif name == '.':
                    for ptr in ptrs:
                        next.update(ptr.children.itervalues())
                elif name == '|':
                    for ptr in ptrs:
                        for branch in node[1]:
                            next.update(_recur(ptr, branch))
                elif name == '&':
                    for ptr in ptrs:
                        temp = [_recur(ptr, branch) for branch in node[1]]
                        if all(temp):
                            for t in temp:
                                next.update(t)

                ptrs = next
                next = set()

            return ptrs

        return sorted(filter(None, [ptr.terminal for ptr in _recur(self.root, cj_tree)]))


if __name__ == '__main__':
    trie = Trie()

    for w in """
        CAD
        CAR
        CARD
        CARET
        CARS
        CART
        CAT
        CATS
        CAM
        CAYS
        CIG
    """.split():
        trie.add(w)

    #print trie

    for patt in """
        CAR CARE CARET
        C.R
    """.split():
        #print patt, ':',  trie.match(patt)
        pass

    #cjp = ConjexParser(r'A&BC')

    for patt in """
        CAR CA[TD] CA[PT] C..
        CA(R|)D CA(T&D)S CA.(&S)
    """.split():
        print patt, ':',  trie.matchex(patt)

    trie = Trie()

    for w in """
        ABD
        AC
    """.split():
        trie.add(w)
    print trie.matchex('A(B&C)D')
