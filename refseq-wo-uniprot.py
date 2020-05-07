from sys import *
import csv, os, json

"""
Set missing UniProt if there is a RefSeq Id which is referred to only once
by UniProt.
Dependecy: List of UniProt-->RefSeq associations created from idmapping.tar.gz
via the script zgrep RefSeq$'\t' idmapping.dat.gz |grep -v - |sed 's/RefSeq\t//g' |sed 's/\..$//g' >uniprot-refseq.tab
Note: Part of items have RefSeq IDs (with presumably identical proteins)
that are referred to by more than one UniProt entry. We take only one of
these UniProt IDs as new ID.
"""

QS = False
dontquery = False
script = os.path.basename(argv[0])[:-3]
ndate = '2020-05-02'
newd = ndate + 'T00:00:00Z'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)

# taxa not in UniProt
nontaxa = ['Q56085857', 'Q27944478', 'Q21102943', 'Q21102968',
        'Q21102941', 'Q21102930']

print('reading UniProt --> RefSeq map')
refs = {}
with open('uniprot-refseq.tab'.format(script)) as file:
    for line in file.readlines():
        u = line.rstrip().split(sep='\t')
        if len(u) != 2:
            continue
        r = refs.get(u[1])
        if r is None:
            refs[u[1]] = u[0]
        else:
            if type(r) is list:
                r.append(u[0])
            else:
                refs[u[1]] = [r, u[0]]

qs = {}
obsf = {}
stmts = {}
for d in jol:
    tax = d.get('taxon')
    if tax in nontaxa:
        continue
    rf = d.get('refseq')
    fstop = rf.rfind('.')
    if fstop != -1:
        rf = rf[:fstop]
    it = d.get('item')
    stmt = d.get('stmt')
    stmts[it] = stmt
    p31 = d.get('p31')
    obsf[it] = p31 == "Q66826848"
    uid = refs.get(rf)
    if uid is None:
        continue
    q = qs.get(it)
    if type(uid) is list:
        if q is None:
            qs[it] = set(uid)
        else:
            q.union(set(uid))
    else:
        if q is None:
            qs[it] = set([uid])
        else:
            q.add(uid)

for it in qs.keys():
    bag = qs.get(it)
    if bag is None:
        continue
    short_id = None
    long_id = None
    if len(bag) > 1:
        for u in list(bag):
            if len(u) > 6:
                long_id = u
            else:
                short_id = u
    else:
        short_id = bag.pop()
    if short_id is None:
        short_id = long_id
    if QS:
        print('{}|P352|"{}"|S248|Q905695|S813|+{}/11'.format(it, short_id, newd))
        if obsf.get(it):
            print('-{}|P31|Q66826848'.format(it))
    else:
        if obsf.get(it):
            stmt = stmts.get(it)
            if stmt is None:
                print("CAN'T HAPPEN")
                continue
            j = {"id": it,
                "claims": {
                    "P31": [{ "id": stmt, "remove": True }],
                    "P352": [ { "value": short_id,
                                    "references": { "P248": "Q905695",
                                        "P813": ndate }}]
                    } }
        else:
            j = {"id": it,
                "claims": {
                    "P352": [ { "value": short_id,
                                    "references": { "P248": "Q905695",
                                        "P813": ndate }}]
                    } }
        f = open('t.json', 'w')
        f.write(json.dumps(j))
        f.close()
        print(json.dumps(j), flush=True)
        ret = os.popen('wd ee t.json --summary refseq-wo-uniprot')
        print(ret.read())
        if ret.close() is not None:
            print('ERROR')
