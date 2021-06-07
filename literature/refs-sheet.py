
import csv, json, argparse, os, sys
from sys import *

def Len(obj):
    if obj is None:
        return 0
    else:
        return len(obj)

def add_to_slot(prot,data,title,pdate,pmid,pmcid,doi,rev):
    l = data.get(prot)
    if l is None:
        l = set([(title,pdate,pmid,pmcid,doi,rev)])
        data[prot] = l
    else:
        l.add((title,pdate,pmid,pmcid,doi,rev))
8
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-t", "--topic", help="base name", required=True)

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
topic = args.topic

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.refs.rq >{}.refs.json'.format(topic, topic))
    if ret.close() is not None:
        raise
file = open('{}.refs.json'.format(topic))
s = file.read()
jol = json.loads(s)

prots = set()
data = dict()
for item in jol:
    title = item.get('title')
    try:
        pdate = item.get('pubdate')[:10]
    except TypeError:
        print(title)
        raise
    pmid = item.get('pmid')
    pmcid = item.get('pmcid')
    doi = item.get('doi')
    rev = item.get('rev')
    is_added = False
    if Len(rev) > 0:
        rev = '✔'
    else:
        rev = ''
    prot = item.get('protLabel')
    if prot == 'replication/transcription complex':
        prot = 'RTC'
    if Len(prot) > 0:
        is_added = True
        prots.add(prot)
        add_to_slot(prot,data,title,pdate,pmid,pmcid,doi,rev)
    for topic in ['autoi', 'fusion', 'omics', 'rna', 'rev']:
        if Len(item.get(topic)) > 0:
            is_added = True
            add_to_slot(topic,data,title,pdate,pmid,pmcid,doi,rev)
            prots.add(topic)
    if not is_added and item.get('top') == 'Q7202':
        prot = 'Misc'
        prots.add(prot)
        add_to_slot(prot,data,title,pdate,pmid,pmcid,doi,rev)

for p in prots:
    with open('refs-{}.csv'.format(p), 'w', newline='') as csvfile:
        fieldnames = ['Title', 'Rev', 'Published', 'PMID', 'PMC', 'DOI']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        if data.get(p) is None:
            continue
        print('writing {}'.format(p), flush=True, file=stderr)
        for title,pdate,pmid,pmcid,doi,rev in sorted(data.get(p), key=lambda tup : tup[1], reverse=True):
            if Len(pmid) > 0:
                pmid = "https://pubmed.ncbi.nlm.nih.gov/"+pmid
            else:
                pmid = ''
            if Len(pmcid) > 0:
                pmcid = "https://www.ncbi.nlm.nih.gov/pmc/articles/"+pmcid
            else:
                pmcid = ''
            if doi is not None:
                doi = "https://doi.org/"+doi
            else:
                doi = ''
            try:
                d = {'Title':title, 'Rev':rev, 'Published':pdate, 'PMID':pmid, 'PMC':pmcid, 'DOI':doi }
            except TypeError:
                print(title)
                exit()
            writer.writerow(d)

