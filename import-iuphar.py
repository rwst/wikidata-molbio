from sys import *
import csv

reader = csv.DictReader(open('genes.tab', 'r'), delimiter='\t')
genes = {}
for item in reader:
    name = item.get('itemLabel')
    if genes.get(name):
        print('duplicate gene name: {} {} {}'.format(name,genes.get(name),item.get('item')))
    else:
        genes[name] = item.get('item')
reader = csv.DictReader(open('human-uniprot-gene.tab', 'r'), delimiter='\t')
unips = {}
rms = set()
for item in reader:
    uid = item.get('uniprotid')
    name = item.get('itemLabel')
    iturl = item.get('item')
    iturl = iturl[iturl.rfind('/')+1:]
    found = unips.get(uid)
    if found and iturl != found[0]:
        print('duplicate uid: {}'.format(uid))
        rms.add(uid)
    else:
        unips[uid] = (iturl, name)
reader = csv.DictReader(open('GtP_to_UniProt_mapping.csv', 'r'), delimiter=',')
for item in reader:
    org = item.get('species')
    if org != 'Human':
        continue
    uid = item.get('uniprot_id')
    iid = item.get('iuphar_id')
    if uid.find('-') >= 0:
        uid = uid[:uid.find('-')]
    tup = unips.get(uid)
    if tup is None:
        #print('missing uid: {} {}'.format(uid,item.get('iuphar_name')))
        continue
    print("{}|P595|{}|S248|Q17091219|S813|2019-08-15T00:00:00Z/11".format(tup[0], iid))
