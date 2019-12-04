import csv
from anytree import Node, find, findall, PreOrderIter, RenderTree, Resolver, AsciiStyle, ChildResolverError
from sys import *

class ECNode(Node):
    q = ''
    lab = ''

tree = ECNode('Root')

reader = csv.DictReader(open('tt.tab', 'r'), delimiter='\t')
efs = []
qlabels = set()
leaves = []
for item in reader:
    iturl = item.get('p')
    desc = item.get('pDescription')
    qit = iturl[iturl.rfind('/')+1:]
    plab = item.get('pLabel')
    qlab = item.get('qLabel')
    qlabels.add(qlab)
    ec = item.get('ec')
    if len(ec) == 0:
        continue
    mr = len(item.get('mr')) > 0
    if not '.-' in ec or not mr:
        leaves.append((ec, qit))
        continue
    node = tree
    for n in ec.split('.'):
        if n == '-':
            break
        sub = next((c for c in node.children if c.name == n),None)
        if sub is None:
            sub = ECNode(n, parent=node, q='', lab='')
        node = sub
    node.q = qit
    node.lab = plab

#for pre, _, node in RenderTree(tree):
#    print(" %s%s {{Q|%s}}" % (pre, node.name, node.q))
r = Resolver()
for l in leaves:
    ec = l[0]
    if ec == '-.-.-.-':
        continue
    ec = ec.split('.')
    if len(ec) != 4:
        print(l)
    p = 3
    for i in [3,2]:
        if ec[i] == '-':
            p = i-1
    for i in range(p, -1, -1):
        t = '/'.join(ec[0:i])
        if i == 0:
            t = ''
        try:
            res = r.glob(tree, '/Root/'+t)
        except ChildResolverError:
            continue
        if len(res[0].q) == 0:
            continue
        print('{}|P279|{}|S854|"ftp://ftp.expasy.org/databases/enzyme/enzyme.dat"|S813|+2019-09-09T00:00:00Z/11'.format(l[1], res[0].q))
        break
