from sys import *
import csv, os, json

"""
Merge items with duplicate UniProt Id, always newer into older.
Note: items cannot have two different descriptions in any language.
"""
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

args = parser.parse_args()

QS = args.output_qs
dontquery = not args.query
script = os.path.basename(argv[0])[:-3]

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
    uid = d.get('uid')
    it = d.get('item')
    git = unips.get(uid)
    if git is None:
        unips[uid] = [it]
    else:
        dups.add(uid)
        git.append(it)

items = []
desc = {}
for u in dups:
    items = items + list(set(unips.get(u)))
print('Fetching description for {} items'.format(len(items)), flush=True)
itstr = " ".join(list(map(str, items)))
ret = os.popen('echo {}| wd data --simplify --props descriptions >t.json'.format(itstr))
print(ret.read())
if ret.close() is not None:
    print('ERROR')
with open('t.json'.format(script)) as file:
    lines = file.readlines()
    for s in lines:
        jol = json.loads(s)
        it = jol.get('id')
        desc[it] = jol.get('descriptions')

for u in dups:
    its = sorted(list(set(unips.get(u))))
    it = its[0]
    d1 = desc.get(it)
    for dup in its[1:]:
        if QS:
            print('MERGE|{}|{}'.format(it, dup))
        else:
            d2 = desc.get(dup)
            for lang in d1.keys():
                if lang is None:
                    continue
                d2d = d2.get(lang)
                if d2d is None:
                    continue
                d1d = d1.get(lang)
                if d1d == d2d:
                    continue
                # for any pair of different descriptions set the shorter to the longer one
                if len(d1d) >= len(d2d):
                    j = {"id": dup, "descriptions": { lang: { "value": d2d, "remove": True} }}
                else:
                    j = {"id": it, "descriptions": { lang: { "value": d1d, "remove": True} }}
                f = open('t.json', 'w')
                f.write(json.dumps(j))
                f.close()
                print(json.dumps(j), flush=True)
                ret = os.popen('wd ee t.json --summary adapt-desc-before-merge')
                print(ret.read())
                if ret.close() is not None:
                    print('ERROR')
                    
            print('wd me {} {}'.format(dup, it), flush=True)
            ret = os.popen('wd me {} {}'.format(dup, it))
            print(ret.read())
            if ret.close() is not None:
                print('ERROR')
