import pronto, six, csv
from sys import *

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

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
mfs = {}
for item in reader:
    ec = item.get('ecLabel')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    git = mfs.get(it)
    if git is None:
        mfs[it] = ec
    else:
        print(it)

reader = csv.DictReader(open('efnames.tab', 'r'), delimiter='\t')
ns = {}
for item in reader:
    ec = item.get('pLabel')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    git = ns.get(it)
    if git is None:
        ns[it] = ec
    else:
        print(it)

reader = csv.DictReader(open('mf.tab', 'r'), delimiter='\t')
ms = {}
for item in reader:
    lab = item.get('pLabel')
    iturl = item.get('p')
    it = iturl[iturl.rfind('/')+1:]
    git = ms.get(it)
    if git is None:
        ms[it] = lab
    else:
        print(it)

reader = csv.DictReader(open('ec2go.tab', 'r'), delimiter='\t')
ecgo = {}
for item in reader:
    ec = item.get('ec')
    go = item.get('goid')
    git = ecgo.get(ec)
    if git is None:
        ecgo[ec] = [go]
    else:
        git.append(go)

for tup in mfs.items():
    red = False
    ec = tup[1].replace('.-', '')
    goecl = ecgo.get(ec)
    while goecl is None:
        red = True
        ec = ec[:ec.rfind('.')]
        goecl = ecgo.get(ec)
    if None is efs.get(goecl[0]):
        print(tup[0])
        continue
    if len(goecl) == 1:
        pass #print('{}|P680|{}'.format(tup[0], efs.get(goecl[0]), goecl[0]))
    else:
        for e in goecl:
            print('{}|P680|{} x {} {}'.format(tup[0], efs.get(e), ns.get(tup[0]), ms.get(efs.get(e))))
