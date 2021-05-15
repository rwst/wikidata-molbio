import os, json, argparse, sys, datetime, time
import xml.etree.ElementTree as ET, gzip

"""
Loads all items with IPR except domain families and checks InterPro release for additions.
Checks also for duplicate IPR. Use with wd ce.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument('-i', '--iprel', help='InterPro release item', required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
INTERPRO_RELEASE = args.iprel

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

input = gzip.open('interpro.xml.gz')                                   
tree = ET.parse(input)
root = tree.getroot() 

its = {}
delids = set()
for child in root:
    if child.tag == 'interpro':
        its[child.attrib.get('id')] = child
    if child.tag == 'deleted_entries':
        for dc in child:
            delids.add(dc.attrib.get('id'))

#print(set(its.keys()).intersection(delids))

qits = {}
for d in jol:
    ipr = d.get('ipr')
    qit = d.get('item')
    if ipr in qits.keys():
        print('duplicate: {}'.format(ipr))
        exit()
    else:
        qits[ipr] = qit

for nipr in set(its.keys()).difference(set(qits.keys())):
    entry = its.get(nipr)
    type = entry.attrib.get('type')
    pl = None
    ct = None
    fi = None
    name = ''
    for ch in entry:
        if ch.tag == 'name':
            name = ch.text
        if ch.tag == 'parent_list':
            pl = ch.getchildren()
        if ch.tag == 'contains':
            ct = ch.getchildren()
        if ch.tag == 'found_in':
            fi = ch.getchildren()
        ref = { "P248": INTERPRO_RELEASE }
        refipr = { "P248": INTERPRO_RELEASE, "P2926": nipr }
        refnam = { "P248": INTERPRO_RELEASE, "P1810": name }
        j = {}
        claims = { 'P2926': { 'value': nipr, 'references': refnam } }
       
    if type == 'Family':
        elab,flab,dlab = "InterPro protein family", "famille InterPro", "InterPro Proteinfamilie"
        claims['P31'] = { 'value': 'Q417841', 'references': refipr }
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    if qits.get(ref) is not None:
                        claims['P279'] = { 'value': qits.get(ref), 'references': refipr }
        else:
            claims['P279'] = { 'value': 'Q8054', 'references': refipr }
        if ct is not None and len(ct) > 0:
            for p in ct:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    if qits.get(ref) is not None:
                        claims['P527'] = { 'value': qits.get(ref), 'references': refipr }
    elif type == 'Domain':
        elab,flab,dlab = "InterPro domain", "Domaine InterPro", "InterPro Proteindomäne"
        claims['P31'] = { 'value': 'Q898273', 'references': refipr }
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    if qits.get(ref) is not None:
                        claims['P279'] = { 'value': qits.get(ref), 'references': refipr }
    elif type == 'Conserved_site':
        elab,flab,dlab = "InterPro conserved site", "Site Conservé InterPro", "InterPro Proteindomäne"
        claims['P31'] = { 'value': 'Q7644128', 'references': refipr }
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    if qits.get(ref) is not None:
                        claims['P279'] = { 'value': qits.get(ref), 'references': refipr }
        if fi is not None and len(fi) > 0:
            for p in fi:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    if qits.get(ref) is not None:
                        claims['P361'] = { 'value': qits.get(ref), 'references': refipr }
    elif type == 'Repeat':
        elab,flab,dlab = "InterPro motif", "motif structurel", "Strukturmotiv"
        claims['P31'] = { 'value': 'Q3273544', 'references': refipr }
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    if qits.get(ref) is not None:
                        claims['P279'] = { 'value': qits.get(ref), 'references': refipr }
        if fi is not None and len(fi) > 0:
            for p in fi:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    if qits.get(ref) is not None:
                        claims['P361'] = { 'value': qits.get(ref), 'references': refipr }
    else:
        continue
    j['labels'] = { "en": name }
    j["descriptions"] = { "en": elab, "fr": flab, "de": dlab }
    j['aliases'] = { "en": [ entry.attrib.get('short_name'), nipr ] }
    j['claims'] = claims
    print(json.dumps(j), flush=True)
