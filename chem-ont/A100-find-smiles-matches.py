import csv, os, json, argparse, sys, re
from rdkit import Chem

"""
Print tree of proper chemclasses
"""
def is_compound(mol):
    return len(Chem.FindPotentialStereo(mol)) == len(re.findall('@@?', Chem.MolToSmiles(mol)))

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-p", "--pattern", help="SMARTS to match",
        required=True)
parser.add_argument("-i", "--ident", help="report identical SMILES only",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V [] \,\$
dontquery = not args.query
#pat = Chem.MolFromSmarts(args.pattern)
script = os.path.basename(sys.argv[0])[:-3]

if args.ident:
    q = Chem.MolFromSmiles(args.pattern)
    try:
        idsm = Chem.MolToSmiles(q, isomericSmiles=False)
    except Exception:
        idsm = args.pattern
    idstereo = len(Chem.FindPotentialStereo(q))
    print('{}'.format(idstereo))
    ps = Chem.AdjustQueryParameters()
    ps.adjustDegreeFlags = Chem.AdjustQueryWhichFlags.ADJUST_IGNOREDUMMIES
    pat = Chem.AdjustQueryProperties(q, ps)
else:
    pat = Chem.MolFromSmarts(args.pattern)


reader = csv.DictReader(open('smiles.tsv', 'r'), delimiter='\t')
labels = {}
smiles = {}
for d in reader:
    iturl = d.get('item')
    it = iturl[iturl.rfind('/')+1:] 
    lab = d.get('itemLabel')
    labels[it] = lab
    #smiles[it] = d.get('smiles')

c = 0
reader = csv.DictReader(open('inchi.tsv', 'r'), delimiter='\t')
for d in reader:
#    c = c + 1
#    if (c % 10000) == 0:
#        print(c)
    iturl = d.get('item')
    it = iturl[iturl.rfind('/')+1:]
    inchi = None
    inchi = d.get('inchi')
    s = smiles.get(it)
    mol = None
    if s is not None:
        mol = Chem.MolFromSmiles(s)
    elif inchi is not None:
        mol = Chem.MolFromInchi(inchi)
    if mol is None:
        if it == 'Q425152':
            print('======={} {} {}'.format(it, s, inchi))
            exit()
        continue
    if args.ident:
        sm = Chem.MolToSmiles(mol, isomericSmiles=False)
        #print('{} {}'.format(it, sm))
        if sm == idsm:
            ism = Chem.MolToSmiles(mol)
            nst = len(re.findall('@@?', ism))
            print('{} {} {}'.format(idstereo-nst, it, labels.get(it)))
        continue
    #if it == 'Q425152':
    #    print('======={} {} {}'.format(it, s, inchi))
    #    print(Chem.MolToSmiles(mol))
    #    print(smiles.get(it))
    #    exit()
    if mol.HasSubstructMatch(pat):
        print('{} {}'.format(it, labels.get(it)))

"""hits = mol.GetSubstructMatches(pat)
    if len(hits) > 3:
        if Chem.MolToSmiles(mol).count('C') == len(hits):
            print('{} {} {} {}'.format(it, labels.get(it), len(hits), Chem.MolToSmiles(mol).count('C')))
            """
