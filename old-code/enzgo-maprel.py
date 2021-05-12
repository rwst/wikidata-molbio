from sys import *
import csv

reader = csv.DictReader(open('goid.tab', 'r'), delimiter='\t')
efs = {}
for item in reader:
    go = item.get('goid')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    git = efs.get(go)
    if git is None:
        efs[go] = it
    else:
        print('============= {}'.format(go))

#set_enzgo = set(l.rstrip() for l in stdin.readlines())
#print(len(set_enzgo))
#print(len(efs.keys()))
#for go in set_enzgo:
#    if go not in efs.keys():
#        print(go)

reader = csv.DictReader(open('mf.tab', 'r'), delimiter='\t')
mfs = {}
ecs = {}
for item in reader:
    ec = item.get('ec')
    lab = item.get('pLabel')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    git = mfs.get(it)
    if git is None:
        mfs[it] = [ec]
    else:
        git.append(ec)
    git = ecs.get(ec)
    if git is None:
        ecs[ec] = [it]
    else:
        git.append(it)

reader = csv.DictReader(open('enzgo-parents.tab', 'r'), delimiter='\t')
pps = {}
for item in reader:
    iturl = item.get('p')
    p = iturl[iturl.rfind('/')+1:]
    iturl = item.get('pp')
    pp = iturl[iturl.rfind('/')+1:]
    git = pps.get(p)
    if git is None:
        pps[p] = [pp]
    else:
        git.append(pp)

for tup in ecs.items():
    ids = tup[1]
    if len(ids) > 1:
        E = []
        B = []
        for i in ids:
            if pps.get(i) is None:
                #print('********************** {}'.format(i))
                continue
            if all(p not in ids for p in pps.get(i)):
                E.append(i)
            else:
                B.append(i)
        if len(E) == 1:
            print('E{} {} ### B{}'.format(E, len(ids), B))
        #print('{}|P591|"{}"|P4390|Q39893449'.format(tup[0], ec))
