
import os, json, argparse, sys, datetime, time
import pronto, six

"""
For every IPR site (Active_site/Binding_site/Conserved_site/Domain/Repeat)
create missing associated families. OTOH, mark such families of obsoleted
domains such that they can be merged with their domains.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

pmids = {}
dups = set()
labels_needed = set()
dpairs = []
dpmids = {}
print('reading dump data...')
file = open('PMID.ndjson')
for line in file.readlines():
    arr = json.loads(line.strip())
    qit = arr[0]
    pma = arr[1]
    if len(pma) == 0:
        continue
    pmid = pma[0]
    subj = arr[2]
    p = pmids.get(pmid)
    if p is None:
        pmids[pmid] = (qit, subj)
    else:
        dp = dpmids.get(pmid)
        if dp is None:
            dpmids[pmid] = [p[0], qit]
        else:
            dp.append(qit)
        dups.add(qit)
        labels_needed.add(p[0])
        labels_needed.add(qit)
        dpairs.append((p[0], qit))

dsize = len(labels_needed)
print('duplicate PMID items: {}'.format(len(dups)))
props = ''
if dontquery is False and dsize > 0:
    BATCH_SIZE = 500
    print('fetching labels')
    rindex = 0
    arr = list(labels_needed)
    while rindex < dsize:
        lindex = rindex
        rindex = rindex + BATCH_SIZE
        if rindex > dsize:
            rindex = dsize
        barr = arr[lindex:rindex]
        print(barr)
        print('fetching batch {}-{}'.format(lindex, rindex-1))
        ret = os.popen('echo "{}" |wd data --props labels.en,descriptions >{}.tmp'.format(' '.join(barr), script))
        if ret.close() is not None:
            raise
        file = open('{}.tmp'.format(script))
        props = props + file.read()
        file.close()
        time.sleep(5)
    f = open('{}.tmp'.format(script), 'w')
    f.write(props)
    f.close()

labels = {}
descr = {}
file = open('{}.tmp'.format(script))
for line in file.readlines():
    d = json.loads(line.strip())
    tmp = d.get('labels').get('en')
    if tmp is None:
        labels[d.get('id')] = ''
    else:
        labels[d.get('id')] = tmp.get('value')
    tmp = d.get('descriptions')
    if tmp is None:
        descr[d.get('id')] = {}
    else:
        descr[d.get('id')] = tmp

print('Merging duplicates...')
for pm in dpmids.keys():
    its = sorted(list(set(dpmids.get(pm))))
    it = its[0]
    d1 = descr.get(it)
    for dup in its[1:]:
        if QS:
            print('MERGE|{}|{}'.format(it, dup))
        else:
            d2 = descr.get(dup)
            for lang in d1.keys():
                if lang is None:
                    continue
                d2d = d2.get(lang)
                if d2d is None:
                    continue
                d2d = d2d.get('value')
                if d2d is None:
                    continue
                d1d = d1.get(lang).get('value')
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
