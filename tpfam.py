import csv
from anytree import Node, find, findall, PreOrderIter, RenderTree, Resolver, AsciiStyle, ChildResolverError
from sys import *

class TCNode(Node):
    q = ''
    lab = ''

print_missing_triples = False
print_qs = True
tree = TCNode('Root')
node9 = TCNode('9', parent=tree, q='Q142943', lab='')

reader = csv.DictReader(open('tpfam.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    plab = item.get('pLabel')
    tc = item.get('tc')
    if len(tc) == 0:
        continue
    node = tree
    #print(tc.split('.'))
    for n in tc.split('.'):
        sub = next((c for c in node.children if c.name == n),None)
        if sub is None:
            sub = TCNode(n, parent=node, q='', lab='')
        node = sub
    node.q = qit
    node.lab = plab


r = Resolver()
reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
leaves = []
missing = {}
for item in reader:
    iturl = item.get('p')
    q = iturl[iturl.rfind('/')+1:]
    tc = item.get('tc')
    if len(tc) == 0:
        continue
    mr = len(item.get('mr')) > 0

#for pre, _, node in RenderTree(tree):
#    print(" %s%s {{Q|%s}}" % (pre, node.name, node.q))

    origtc = tc
    found = False
    if mr:
        p = tc.rfind('.')
        tc = tc[:p]
    while not found and tc.rfind('.') >= 0:
        try:
            res = r.glob(tree, '/Root/'+tc.replace('.', '/'))
        except ChildResolverError:
            m = missing.get(tc)
            if m is None:
                missing[tc] = 1
            else:
                missing[tc] = m + 1
            p = tc.rfind('.')
            tc = tc[:p]
            continue
        if len(res[0].q) > 0:
            if print_qs:
                print('{}|P361|{}|S887|Q69274598|S7260|"{}"|S813|+2019-10-02T00:00:00Z/11'.format(q,res[0].q,origtc))
            found = True
            break
        else:
            p = tc.rfind('.')
            tc = tc[:p]
    if not found:
        try:
            res = r.glob(tree, '/Root/'+tc[0])
        except ChildResolverError:
            raise
        if print_qs:
            print('{}|P361|{}|S887|Q69274598|S7260|"{}"|S813|+2019-10-02T00:00:00Z/11'.format(q,res[0].q,origtc))

if print_missing_triples:
    for tup in sorted(list(missing.items()), key=lambda tup: tup[1]):
        print('{}  {}'.format(tup[1], tup[0]))

