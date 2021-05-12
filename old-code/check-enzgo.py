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

reader = csv.DictReader(open('ec2go.tab', 'r'), delimiter='\t')
for item in reader:
    ec = item.get('ec')
    go = item.get('goid')
    it = efs.get(go)
    our_ec = mfs.get(it)
    if our_ec is None:
        print('http://www.wikidata.org/entity/{}'.format(it))
        continue
    if len(our_ec) > 1:
        ok = False
        for oe in our_ec:
            oe = oe.replace('.-', '')
            if oe == ec:
                ok = True
                break
        #if not ok:
        print('*http://www.wikidata.org/entity/{} : {} {}'.format(it, our_ec, ec))
    else:
        our_ec = our_ec[0].replace('.-', '')
        if our_ec != ec:
            print('*http://www.wikidata.org/entity/{} : {} {}'.format(it, our_ec, ec))
