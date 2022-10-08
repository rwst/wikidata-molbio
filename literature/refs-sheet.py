
import csv, json, argparse, os, sys, gc
from sys import *

def Len(obj):
    if obj is None:
        return 0
    else:
        return len(obj)

def add_to_slot(prot,data,title,pdate,pmid,pmcid,doi,foll,rev):
    l = data.get(prot)
    if l is None:
        l = set([(title,pdate,pmid,pmcid,doi,foll,rev)])
        data[prot] = l
    else:
        l.add((title,pdate,pmid,pmcid,doi,foll,rev))

def get_gtypes_str(prot_str, strains_lst):
    gtypes = { 'VP1': 'R', 'VP2': 'C', 'VP3': 'M', 'VP4': 'P', 'VP6': 'I', 'VP7': 'G',
            'NSP1': 'A', 'NSP2': 'N', 'NSP3': 'T', 'NSP4': 'E', 'NSP5': 'H', 'NSP6': 'H' }
    gt_fps = {
            'Q112242067': 'G3 P[3] I2 R2 C3 M3 A9 T3 E3 H6',
            'Q112242768': 'G3 P[1/2] I2 R2 C5 M5 A5 N2/N5 T5 E2 H5',
            'Q113380949': 'G6 P[1] I2 R2 C2 M2 A3 N2 T6 E2 H3',
            'Q113433734': 'G6 P[5] I2 R2 C2 M2 A3 N2 T7 E2 H3',
            'Q113434050': 'G6 P[1] I2 R2 C2 M2 N2 T6 E2',
            'Q113451268': 'G6 P[5] I2 R2 C2 M2 A3 N2 T6 E2 H3',
            'Q112246255': 'G5 P[7] I5 R1 C1 M1 A1 N1 T1 E1 H1',
            'Q112246336': 'G1 P[8] I1 R1 C1 M1 A1 N1 T1 E1 H1',
            'Q112252986': 'G2 P[4] N2 E2',
            'Q112262674': 'G3 P[7] I5',
            'Q112242465': 'G8 P[14]',
            'Q112252639': 'G2 P[4] I2 R2 C2 M2 A2 N2 T2 E2 H2',
            'Q112252484': 'G6 P[14] I2 R2 C2 M2 A3 N2 T6 E2 H3',
            'Q112252427': 'G3 P[12] I2 A10 E2',
            'Q112252150': 'G5 P[7] I5 A8 E1',
            'Q112703025': 'G2 P[4] E2 H2',
            'Q112252803': 'G11 P[7] I5 R1 C1 M1 A8 N1 T1 E1 H1',
            'Q112252774': 'G1 P[8] I1 R1 C1 M1 A1 N1 T1 E1 H1',
            'Q112252593': 'G4 P[6] I1 R1 C1 M1 A8 N1 T1 E1 H1',
            'Q112246056': 'G16 P[16] I7 A7 E7',
            'Q113380805': 'G3 P[14] A9 E5 H3',
            'Q113396346': 'G1 P[8] I1 R1 C1 M1 A1 N1 T1 E1 H1',
            'Q113354635': 'G3 P[1] I2 R2 C5 M5 A5 N5 T5 E2 H5',
            'Q113457173': 'G4 P[6] I1 R1 C1 M1 A1 N1 T1 E1 H1',
            'Q113468985': 'G3 P[8] E1',
            'Q113531324': 'G1 P[9] A1 H3',
            'Q113531390': 'G3 P[6] I1 E1',
            'Q113531550': 'G9 P[8] I1 R1 C1 M1 A1 N1 T1 E1 H1',
            }
    if Len(strains_lst) == 0:
        return ""
    res = ""
    gt_set = set()
    gt_char = gtypes.get(prot_str)
    if gt_char is None:
        return ""
    for s in strains_lst:
        gt = gt_fps.get(s)
        if gt is None:
            continue
        gt = gt + ' '
        t = gt.find(gt_char)
        tt = gt[t:].find(' ')
        gt_set.add(gt[t:t+tt])
    if len(gt_set) > 0:
        l = sorted(list(gt_set))
        return ' '.join(l)
    return ""


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
human_dois = set()
human_strains = ['Q112246336', 'Q112252986', 'Q112242465', 'Q112252639', 'Q112252484', 'Q112703025', 'Q112252774', 'Q113396346', 'Q113457173', 'Q113468985', 'Q113531324', 'Q113531390', 'Q113531550', 'Q113531739']
strains = {}
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
    foll = item.get('foll')
    rev = item.get('rev')
    entry = item.get('entry')
    uses = item.get('uses')
    if uses in human_strains:
        human_dois.add(doi)
    s = strains.get(doi)
    if s is None:
        strains[doi] = [uses]
    else:
        s.append(uses)
    is_added = False
    if Len(rev) > 0:
        rev = '✔'
    else:
        rev = ''
    prot = item.get('protLabel')
    if prot == 'replication/transcription complex':
        prot = 'RTC'
    # exclusive topics
    for topic in ['fusion', 'glyc', 'entry']:
        if Len(item.get(topic)) > 0:
            is_added = True
            add_to_slot(topic,data,title,pdate,pmid,pmcid,doi,foll,rev)
            prots.add(topic)
    if not is_added and Len(prot) > 0:
        is_added = True
        prots.add(prot)
        add_to_slot(prot,data,title,pdate,pmid,pmcid,doi,foll,rev)
    # inclusive topics
    for topic in ['autoi', 'omics', 'rna', 'rev', 'kerat']:
        if Len(item.get(topic)) > 0:
            is_added = True
            add_to_slot(topic,data,title,pdate,pmid,pmcid,doi,foll,rev)
            prots.add(topic)
    if item.get('top') == 'Q128406':
        is_added = True
        prot = 'drugs'
        prots.add(prot)
        add_to_slot(prot,data,title,pdate,pmid,pmcid,doi,foll,rev)
    if not is_added and item.get('top') == 'Q7202':
        prot = 'Misc'
        prots.add(prot)
        add_to_slot(prot,data,title,pdate,pmid,pmcid,doi,foll,rev)

ret = os.popen('rm -f refs-*.csv')

for p in prots:
    with open('refs-{}.csv'.format(p), 'w', newline='') as csvfile:
        fieldnames = ['Title', 'SHost', 'SGenotypes', 'Rev', 'Published', 'PMID', 'PMC', 'DOI']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        dataset = data.get(p)
        if dataset is None:
            print('Closed {}'.format(p))
            csvfile.close()
            continue
        dois = set([doi for title,pdate,pmid,pmcid,doi,foll,rev in dataset])
        dataset = set([(title,pdate,pmid,pmcid,doi,foll,rev) for title,pdate,pmid,pmcid,doi,foll,rev in dataset if Len(foll)==0 or foll not in dois])
        sortedset = sorted(dataset, key=lambda tup : tup[1], reverse=True)
        print('writing "{}" ({})'.format(p, len(sortedset)), flush=True)
        for title,pdate,pmid,pmcid,doi,foll,rev in sortedset:
            if Len(pmid) > 0:
                pmid = "https://pubmed.ncbi.nlm.nih.gov/"+pmid
            else:
                pmid = ''
            if Len(pmcid) > 0:
                pmcid = "https://www.ncbi.nlm.nih.gov/pmc/articles/"+pmcid
            else:
                pmcid = ''
            if doi in human_dois:
                shost = 'human'
            else:
                shost = ''
            sgtypes = ''
            if doi is not None:
                sgtypes = get_gtypes_str(p, strains.get(doi))
                if p == 'entry':
                    sgtypes = get_gtypes_str('VP7', strains.get(doi)) + ' ' + get_gtypes_str('VP4', strains.get(doi))
                doi = "https://doi.org/"+doi
            else:
                doi = ''
            try:
                d = {'Title':title, 'SHost':shost, 'SGenotypes':sgtypes, 'Rev':rev, 'Published':pdate, 'PMID':pmid, 'PMC':pmcid, 'DOI':doi }
            except TypeError:
                print(title)
                raise
            ret = writer.writerow(d)
            #print("{}: {}".format(ret, d), flush=True)
        del writer
        gc.collect()
        csvfile.close()

alldata = set()
for v in data.values():
    alldata = alldata.union(v)
print(len(alldata))
