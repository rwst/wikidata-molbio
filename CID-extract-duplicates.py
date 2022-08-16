
import csv, os, json, argparse, sys

"""
wget -c https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-InChI-Key.gz
Print list of dupl. InChI keys with their set of CIDs
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument('filenames', metavar='filename', type=str, nargs='+',
                    help='file(s) containing CID-->InChI mapping')

# Read arguments from the command line
args = parser.parse_args()
#print(args)

iks = {}
dups = set()
for fn in args.filenames:
    print(fn, file=sys.stderr)
    with open(fn, 'r') as f:
        stripped_lines = lambda f : (l.rstrip("\n") for l in f)
        for l in stripped_lines(f):
            tab1 = l.find('\t')
            tab2 = l.find('\t', tab1+1)
            cid = int(l[:tab1])
            ik = l[tab2+1:]
            i = iks.get(ik)
            if i is not None:
                dups.add(ik)
                if type(i) is list:
                    i.append(cid)
                else:
                    iks[ik] = [i, cid]
            else:
                iks[ik] = cid

    print(len(iks.keys()), file=sys.stderr)
    print(len(dups), file=sys.stderr)

j = {}
for dup in dups:
    j[dup] = iks.get(dup)
print(json.dumps(j))

