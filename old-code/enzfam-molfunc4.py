import csv
from anytree import Node, find, findall, PreOrderIter, RenderTree, Resolver, AsciiStyle, ChildResolverError
from sys import *

class ECNode(Node):
    q = ''
    lab = ''

tree = ECNode('Root')

reader = csv.DictReader(open('molfunc-higher-ec.tab', 'r'), delimiter='\t')
leaves = []
for item in reader:
    iturl = item.get('p')
    qit = iturl[iturl.rfind('/')+1:]
    ec = item.get('ec')
    if len(ec) == 0:
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

r = Resolver()
reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    ec = item.get('ec')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
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
        print('{}|P680|{}|P4390|Q39894595|S854|"ftp://ftp.expasy.org/databases/enzyme/enzclass.txt"|S813|+2019-12-09T00:00:00Z/11'.format(it, res[0].q))
        break
