import csv
from anytree import Node, find, findall, PreOrderIter, RenderTree, Resolver, AsciiStyle, ChildResolverError
from sys import *

"""
input1:
SELECT DISTINCT ?p ?pLabel ?tc
{
    ?p p:P7260 [ ps:P7260 ?tc; pq:P4390 wd:Q39893449; ].
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .
}

input2 (partof):
SELECT DISTINCT ?p ?tc ?q ?tc1
{
    ?p wdt:P31 wd:Q8054.
    ?p wdt:P7260 ?tc.
    OPTIONAL {
      ?p p:P361 [ ps:P361 ?q; prov:wasDerivedFrom [ pr:P887 wd:Q69274598; ] ].
      ?q p:P7260 [ ps:P7260 ?tc1; pq:P4390 wd:Q39893449; ].
      }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .
}

input2 (subc):
SELECT DISTINCT ?p ?tc ?q ?tc1
{
    ?p p:P7260 [ ps:P7260 ?tc; pq:P4390 wd:Q39893449; ].
    OPTIONAL {
      ?p p:P279 [ ps:P279 ?q; prov:wasDerivedFrom [ pr:P887 wd:Q69274598; ] ].
      ?q p:P7260 [ ps:P7260 ?tc1; pq:P4390 wd:Q39893449; ].
      }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .
}

"""

class TCNode(Node):
    q = ''
    lab = ''

print_tree = False
print_partof_tpfam = False
print_subc_tpfam = not print_partof_tpfam
print_rm_bad_partofs = print_partof_tpfam
print_rm_bad_subcs = print_subc_tpfam
print_missing_triples = False
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

if print_tree:
    for pre, _, node in RenderTree(tree):
        if len(node.lab) > 0:
            print(" %s%s %s {{Q|%s}}" % (pre, node.name, node.lab, node.q))
        else:
            print(" %s%s" % (pre, node.name))
    exit()

r = Resolver()
reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
leaves = []
missing = {}
superc = {}
for item in reader:
    iturl = item.get('p')
    q = iturl[iturl.rfind('/')+1:]
    tc = item.get('tc')
    tc1 = item.get('tc1')
    if len(tc) == 0:
        continue
    if len(tc1) > 0 and not tc.startswith(tc1):
        continue
    iturl = item.get('q')
    if len(iturl) > 0:
        qq = iturl[iturl.rfind('/')+1:]
        s = superc.get((q,tc))
        if s != None:
            s.add(qq)
        else:
            superc[(q,tc)] = set([qq])

for q,tc in superc.keys():
    origtc = tc
    found = False
    mr = print_subc_tpfam
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
            tpsuperfam = res[0].q
            if print_partof_tpfam:
                s = superc.get((q,origtc))
                if s is None or tpsuperfam not in s:
                        print('{}|P361|{}|S887|Q69274598|S7260|"{}"|S813|+2019-10-02T00:00:00Z/11'.format(q,
                            tpsuperfam, origtc))
            if print_subc_tpfam:
                s = superc.get((q,origtc))
                if s is None or tpsuperfam not in s:
                    print('{}|P279|{}|S887|Q69274598|S7260|"{}"|S813|+2019-10-02T00:00:00Z/11'.format(q,
                        tpsuperfam, origtc))
            if print_rm_bad_partofs:
                s = superc.get((q,origtc))
                if s != None:
                    for tpf in s:
                        if tpf != tpsuperfam:
                            print('-{}|P361|{}'.format(q, tpf))
            if print_rm_bad_subcs:
                s = superc.get((q,origtc))
                if s != None:
                    for tpf in s:
                        if tpf != tpsuperfam:
                            print('-{}|P279|{}'.format(q, tpf))
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
        if print_partof_tpfam:
            tpsuperfam = res[0].q
            s = superc.get((q,origtc))
            if s is None or tpsuperfam not in s:
                print('{}|P361|{}|S887|Q69274598|S7260|"{}"|S813|+2019-10-02T00:00:00Z/11'.format(q,res[0].q,origtc))
        if print_subc_tpfam:
            tpsuperfam = res[0].q
            s = superc.get((q,origtc))
            if s is None or tpsuperfam not in s:
                print('{}|P279|{}|S887|Q69274598|S7260|"{}"|S813|+2019-10-02T00:00:00Z/11'.format(q,res[0].q,origtc))
        if print_rm_bad_partofs:
            s = superc.get((q,origtc))
            if s != None:
                for tpf in s:
                    if tpf != tpsuperfam:
                        print('-{}|P361|{}'.format(q, tpf))
        if print_rm_bad_subcs:
            s = superc.get((q,origtc))
            if s != None:
                for tpf in s:
                    if tpf != tpsuperfam:
                        print('-{}|P279|{}'.format(q, tpf))

if print_missing_triples:
    for tup in sorted(list(missing.items()), key=lambda tup: tup[1]):
        print('{}  {}'.format(tup[1], tup[0]))

