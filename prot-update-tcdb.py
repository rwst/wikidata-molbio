from sys import *
import csv, os, json

QS = False
dontquery = False
script = os.path.basename(argv[0])[:-3]
ndate = '2020-04-29'
newd = ndate + 'T00:00:00Z'
LIMIT = 100000

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

unips = {}
tcdbs = {}
dups = set()
for d in jol:
    uid = d.get('u')
    it = d.get('p')
    git = unips.get(uid)
    if git is not None and git != it:
        #print('more than one value: {} ({}, {})'.format(uid, git, it))
        dups.add(uid)
        continue
    elif git is None:
        unips[uid] = it
    t = d.get('t')
    if t is None or len(t) == 0:
        continue
    stmt = d.get('stmt')
    refd = d.get('refdate')
    tc = tcdbs.get(it)
    if tc is None:
        tcdbs[it] = [(t,stmt,refd)]
    else:
        tc.append((t,stmt,refd))

for k in dups:
    unips.pop(k)
print('ignoring {} items with duplicate UniProt IDs'.format(len(dups)))

ctr = 0
uids = set(unips.keys())
tups = []
for line in open('tcdb.txt').readlines():
    l = line.rstrip()
    if l[0] != '>':
        continue
    ll = l.split('|')
    u = ll[2].rstrip()
    t = ll[3][:ll[3].find(' ')]
    if u in uids and unips.get(u) is not None:
        ctr = ctr + 1
        if ctr > LIMIT:
            break
        qit = unips.get(u)
        if QS:
            print('{}|P7260|"{}"|S248|Q142667|S813|+{}/11'.format(qit, t, newd))
        else:
            if tcdbs.get(qit) is None:
                j = {"id": qit, "claims": { "P7260": [{ "value": t,
                    "references": { "P248": "Q142667", "P813": ndate }}] } }
                f = open('t.json', 'w')
                f.write(json.dumps(j))
                f.close()
                print(json.dumps(j), flush=True)
                ret = os.popen('wd ee t.json')
                print(ret.read())
                if ret.close() is not None:
                    print('ERROR')
                continue
            for oldset in tcdbs.get(qit):
                origt,stmt,refd = oldset
                if refd == newd:
                    continue
                j = {"id": qit, "claims": { "P7260": [{ "id": stmt, "value": t,
                    "references": { "P248": "Q142667", "P813": ndate }}] } }
                f = open('t.json', 'w')
                f.write(json.dumps(j))
                f.close()
                print(json.dumps(j), flush=True)
                ret = os.popen('wd ee t.json')
                print(ret.read())
                if ret.close() is not None:
                    print('ERROR')

