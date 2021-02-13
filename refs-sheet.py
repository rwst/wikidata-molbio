
import csv, json
from sys import *

reader = csv.DictReader(open('query.tsv', 'r'), delimiter='\t')
prots = set()
data = dict()
for item in reader:
    title = item.get('title')
    pdate = item.get('pubdate')[:10]
    pmid = item.get('pmid')
    pmcid = item.get('pmcid')
    doi = item.get('doi')
    rev = item.get('rev')
    if len(rev) > 0:
        rev = '✔'
    else:
        rev = ''
    prot = item.get('protLabel')
    if prot == 'replication/transcription complex':
        prot = 'RTC'
    if len(prot) == 0:
        prot = 'Misc'
        if len(item.get('rna')) > 0:
            prot = 'RNA'
        elif len(item.get('omics')) > 0:
            prot = 'omics'
        elif len(rev) > 0:
            prot = 'Rev'
    l = data.get(prot)
    if l is None:
        l = set()
        data[prot] = l
    l.add((title,pdate,pmid,pmcid,doi,rev))
    prots.add(prot)

for p in prots:
    with open('refs-{}.csv'.format(p), 'w', newline='') as csvfile:
        fieldnames = ['Title', 'Rev', 'Published', 'PMID', 'PMC', 'DOI']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for title,pdate,pmid,pmcid,doi,rev in data.get(p):
            if len(pmid) > 0:
                pmid = "https://pubmed.ncbi.nlm.nih.gov/"+pmid
            if len(pmcid) > 0:
                pmcid = "https://www.ncbi.nlm.nih.gov/pmc/articles/"+pmcid
            d = {'Title':title, 'Rev':rev, 'Published':pdate, 'PMID':pmid, 'PMC':pmcid, 'DOI':"https://doi.org/"+doi}
            writer.writerow(d)

