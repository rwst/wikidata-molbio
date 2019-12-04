from sys import *
import csv

reader = csv.DictReader(open('gene-diseaseassoc.tab', 'r'), delimiter='\t')
genes = {}
for item in reader:
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    disurl = item.get('dis')
    dis = disurl[disurl.rfind('/')+1:]
    gitem = genes.get(it)
    if gitem is None:
        s = set()
        s.add(dis)
        genes[it] = s
    else:
        gitem.add(dis)
reader = csv.DictReader(open('diseaseid-omim.tab', 'r'), delimiter='\t')
mims = {}
for item in reader:
    iturl = item.get('item')
    it = iturl[iturl.rfind('/')+1:]
    mimid = item.get('omim')
    mim = mims.get(mimid)
    if mim is None:
        s = set()
        s.add(it)
        mims[mimid] = s
    else:
        mim.add(it)
dupkeys = []
for tup in mims.items():
    if len(tup[1]) > 1:
        #print('more than one OMIM ID: {} ({})'.format(tup[0], tup[1]))
        dupkeys.append(tup[0])
for k in dupkeys:
    mims.pop(k)

reader = csv.DictReader(open('uniprot-geneid.tab', 'r'), delimiter='\t')
unips = {}
dups = set()
for item in reader:
    uid = item.get('uid')
    iturl = item.get('gid')
    it = iturl[iturl.rfind('/')+1:]
    git = unips.get(uid)
    if git is None or git == it:
        unips[uid] = it
    else:
        #print('more than one value: {} ({}, {})'.format(uid, git, it))
        dups.add(uid)
for k in dups:
    unips.pop(k)

reader = csv.DictReader(stdin, delimiter='\t')
for item in reader:
    uid = item.get('Entry')
    dstr = item.get('Involvement in disease')
    pos = dstr.find('[MIM:')
    while pos > 0:
        mimid = dstr[pos+5:pos+11]
        dstr = dstr[pos+11:]
        dis = mims.get(mimid)
        if dis is not None:
            dgenes = genes.get(list(dis)[0])
            git = unips.get(uid)
            if git is not None:
                if dgenes is None or git not in dgenes:
                    #print('{}|P2293|{}'.format(list(dis)[0], git))
                    print('{}|P2293|{}|S248|Q905695|S813|+2019-08-13T00:00:00Z/11|S352|"{}"'.format(list(dis)[0], git, uid))
    #print('{}|P492|"{}"|S248|Q241953|S813|+2019-08-19T00:00:00Z/11'.format(it, mimid))
        else:
            pass #print(mimid)
        pos = dstr.find('[MIM:')

