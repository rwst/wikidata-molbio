import csv
from sys import *

reader = csv.DictReader(open('t.tab', 'r'), delimiter='\t')
for item in reader:
    ipr = item.get('ipr')
    iturl = item.get('item1')
    it = iturl[iturl.rfind('/')+1:]
    lab = item.get('item1Label').strip()
    nlab = lab
    l = len(lab)
    ll = lab.lower()
    if (ll.rfind('family') >=0 and ll.rfind('family') >= l-16):
        label = lab
    elif (ll.rfind('protein') >=0 and ll.rfind('protein') >= l-16 or
        ll.rfind('transporter') == l-9 or
        ll.rfind('inhibitor') == l-9 or
        ll.rfind('peptide') >=0 and ll.rfind('peptide') >= l-16 or
        ll.rfind('toxin') >=0 and ll.rfind('toxin') >= l-14 or
        ll.rfind('enzyme') >=0 and ll.rfind('enzyme') >= l-15 or
        ll.rfind('ase') >=0 and ll.rfind('ase') >= l-8):
        label = lab + ' family'
    elif (ll.rfind('domain') == l-6):
        label = lab + ', protein family'
    elif (ll.rfind('binding') >=0 and ll.rfind('binding') >= l-11 or
        ll.rfind('transmembrane') >=0 and ll.rfind('transmembrane') >= l-16 or
        ll.rfind('terminal') == l-8 or
        ll.rfind('central') == l-7 or
        ll.rfind('processing') == l-10 or
        ll.rfind('associated') == l-10 or
        ll.rfind('catalytic') == l-9 or
        ll.rfind('periplasmic') == l-11 or
        ll.rfind('extracellular') == l-13 or
        ll.rfind('core') == l-4):
        label = lab + ' domain, protein family'
    else:
        label = lab + ', protein family'
    #label = label[0].lower() + label[1:]

    print('CREATE\nLAST|Len|"{}"\nLAST|Den|"protein family"\nLAST|Aen|"{}"\nLAST|P31|Q81505329|P642|{}|S248|Q81384305|S2926|"{}"\nLAST|P527|{}|S248|Q81384305|S2926|"{}"\nLAST|P2926|"{}"|S248|Q81384305'.format(label, ipr, it, ipr, it, ipr, ipr))
