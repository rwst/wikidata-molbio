from sys import *
import csv

reader = csv.DictReader(open('gene-entrezids.tab', 'r'), delimiter='\t')
genes = {}
for item in reader:
    gid = item.get('geneid')
    iturl = item.get('item')
    iturl = iturl[iturl.rfind('/')+1:]
    gitem = genes.get(gid)
    if gitem is not None:
        if iturl != gitem[0]:
            print('duplicate gene id: {} {} {}'.format(gid,gitem,iturl))
        continue
    else:
        name = item.get('itemLabel')
        genes[gid] = (iturl, name)
reader = csv.DictReader(open('mim2gene.txt', 'r'), delimiter='\t')
mims = {}
for item in reader:
    type = item.get('mtype')
    if type != 'gene':
        continue
    gid = item.get('gid')
    gene = genes.get(gid)
    mimid = item.get('mimid')
    name = item.get('gname')
    if gene is None and gid is not None and len(gid) > 0:
        print('missing gene: {} Entrez: {} OMIM: {}'.format(name,gid,mimid))
    if gene is None:
        continue
    it = gene[0]
    na = gene[1]
    if name != na:
        print('name mismatch: {} ({}) {}'.format(name, gid, na))
    #print('{}|P492|"{}"'.format(it, mimid))
    print('{}|P492|"{}"|S248|Q241953|S813|+2019-08-19T00:00:00Z/11'.format(it, mimid))
