
import csv, os, json, argparse, sys
import pronto, six

"""
use with wd ce
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
CHEMICAL_COMPOUND = 'Q11173'
ION = 'Q36496'
PEPTIDE = 'Q172847'
MAPPING_TYPE = 'P4390'
SKOS_EXACT = 'Q39893449'
STATED_IN = 'P248'
CHEBI_RELEASE = 'Q105965742'

reader = csv.DictReader(open('pcm.tab', 'r'), delimiter='\t')
cids = {}
for item in reader:
    ch = item.get('CHEBI')
    if ch is None:
        continue
    ch = ch[6:]
    cid = item.get('CID')
    if cid is not None and len(cid) > 0:
        cids[ch] = cid

print('Reading ontology...', file=sys.stderr)
ont = pronto.Ontology('chebi.obo')

ent = {}
desc = { 'en': 'chemical compound',
        'fr': 'composé chimique',
        'de': 'chemische Verbindung',
        'ru': 'химическое соединение'
        }
file = open('missing')
for line in file.readlines():
    ID = line.rstrip()
    if len(ID) == 0 or ID[:6] != 'CHEBI:':
        continue
    term = ont.get(ID)
    if term is None:
        print("not found: {}".format(ID), file=sys.stderr)
        continue
    ik = None
    inchi = None
    charge = None
    if len(term.name) < 240:
        ent['labels'] = { 'en': term.name }
    else:
        ent['labels'] = { 'en': term.id }

    claims = {}
    syns = []
    for syn in term.synonyms:
        if syn.scope == 'EXACT':
            if len(syn.description) < 240:
                syns.append(syn.description)
    if len(syns) > 0:
        ent['aliases'] = { 'en': syns }
    ent['descriptions'] = desc
    claims['P683'] = [ { 'value': term.id[6:],
        'qualifiers': { MAPPING_TYPE: SKOS_EXACT },
        'references': { STATED_IN: CHEBI_RELEASE } }] 
    P31claims = []
    for ann in term.annotations:
        if ann.property == 'http://purl.obolibrary.org/obo/chebi/inchikey':
            ik = ann.literal
        if ann.property == 'http://purl.obolibrary.org/obo/chebi/inchi':
            inchi = ann.literal
            if len(inchi) > 1490:
                inchi = None
        if ann.property == 'http://purl.obolibrary.org/obo/chebi/charge':
            charge = ann.literal
    if ik is None:
        continue
    claims['P235'] = [{ 'value': ik, 'references': { STATED_IN: CHEBI_RELEASE } }]
    if inchi is not None:
        claims['P234'] = [{ 'value': inchi, 'references': { STATED_IN: CHEBI_RELEASE } }]
    if charge == '0':
        P31claims.append({'value': CHEMICAL_COMPOUND, 'references': { STATED_IN: CHEBI_RELEASE } })
    else:
        P31claims.append({'value': ION, 'references': { STATED_IN: CHEBI_RELEASE } })
    for rel in term.relationships:
        if rel.name == 'is_a' and term.relationships.get(rel).id == 'CHEBI:16670':
            P31claims.append({'value': PEPTIDE, 'references': { STATED_IN: CHEBI_RELEASE } })
    claims['P31'] = P31claims
    cid = cids.get(term.id[6:])
    if cid is not None:
        claims['P662'] = [{ 'value': cid, 'references': { STATED_IN: CHEBI_RELEASE } }]
    
    ent['claims'] = claims
    print(json.dumps(ent), flush=True)

