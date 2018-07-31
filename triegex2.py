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
                tree[i] = ('[', [[branch] for branch in self._clean(args)])
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
                b = min(args[1], 32)
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

class ConjexPlanner(object):
    def __init__(self, tree):
        self.tree = tree

        dup = deepcopy(tree)
        self.plan = self._split(dup, dup)

    def _split(self, root, ptr):
        for i, node in enumerate(ptr):
            name = node[0]
            if name in '&|':
                res = []
                for child in node[1]:
                    ptr[i: i + 1] = child
                    dup = deepcopy(root)
                    res.append(self._split(dup, dup))
                return ({'&': 'and', '|': 'or'}[name], res)
        return ('base', root)

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

    def _step(self, ptrs):
        res = set()
        for ptr in ptrs:
            name = node[0]
            if name == '_':
                c = node[1]
                if c in ptr.children:
                    res.add(ptr.children[c])
            elif name == '.':
                res.update(ptr.children.itervalues())
        return res

    def _init_state(self, plan):
        name, sub = plan
        if name == 'base':
            return (name, set([self.root]), sub)
        return (name, set([self.root]), map(self._init_state, sub))

    def matchex(self, conjex):
        parser = ConjexParser(conjex)
        planner = ConjexPlanner(parser.tree)

        state = self._init_state(planner.plan)


if __name__ == '__main__':
    cp = ConjexParser(r'..(I&Y).')

    #print cp.tree

    planner = ConjexPlanner(cp.tree)

    #print planner.plan

    trie = Triegex()

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

    #print trie._matchex_one(ConjexParser(r'CA.').tree)
    print trie.matchex(r'CA(R&D)')
