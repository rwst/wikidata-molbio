from sys import *
import csv, os, json

"""
Remove obsolete UniProt Id, add inst-of Q66826848 (ref. UniProt Id)
Dependecy: List of proper UniProt IDs created from idmapping.tar.gz via the
script zcat idmapping.dat.gz |sed 's/[\t\-].*$//g' |sort |uniq >uniprot-ids
"""

QS = False
dontquery = 1#False
script = os.path.basename(argv[0])[:-3]
ndate = '2020-04-30'
newd = ndate + 'T00:00:00Z'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)

unips = {}
dups = set()
for d in jol:
    uid = d.get('u')
    it = d.get('p')
    stmt = d.get('stmt')
    git = unips.get(uid)
    if git is None:
        unips[uid] = [(it, stmt)]
    else:
        dups.add(uid)
        git.append((it, stmt))

with open('{}.wdu'.format(script), 'w+') as file:
    for u in unips.keys():
        file.write(u + '\n')
print('Sorting WD items')
ret = os.popen('sort {}.wdu > {}.wdus'.format(script, script))
if ret.close() is not None:
    raise
print('looking for uids not in UniProt...')
ret = os.popen('comm -13 uniprot-ids {}.wdus > {}.obsu'.format(script, script))
if ret.close() is not None:
    raise

with open('{}.obsu'.format(script)) as file:
    for line in file.readlines():
        u = line.rstrip()
        if u is None:
            continue
        us = unips.get(u)
        if us is None:
            continue
        for (q,stmt) in us:
            if QS:
                print('-{}|P352|"{}"'.format(q, u))
                #print('{}|Den|"obsolete"'.format(q))
                print('{}|P31|Q66826848|S352|"{}"|S248|Q905695|S813|+{}/11'.format(q, u, newd))
            else:
                j = {"id": q,
                        "claims": {
                            "P31": [{ "value": "Q66826848",
                                "references": { "P248": "Q905695",
                                    "P352": u,
                                    "P813": ndate }}],
                            "P352": [ { "id": stmt, "remove": True} ]
                            } }
                f = open('t.json', 'w')
                f.write(json.dumps(j))
                f.close()
                print(json.dumps(j), flush=True)
                ret = os.popen('wd ee t.json')
                print(ret.read())
                if ret.close() is not None:
                    print('ERROR')
