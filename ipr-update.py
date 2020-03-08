import csv
from sys import *
import gzip                                                            
import xml.etree.ElementTree as ET                                     

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
reader = csv.DictReader(open('wd-ipr.tab', 'r'), delimiter='\t')
for item in reader:
    iturl = item.get('item')
    qit = iturl[iturl.rfind('/')+1:]
    ipr = item.get('ip')
    if ipr not in its.keys():
#        print('{}|P31|Q81408532|S248|Q81384305|S2926|"{}"\n-{}|P31|Q417841\n-{}|P2926|"{}"'.format(qit,
#            ipr,qit,qit,ipr))
        continue
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
    if type == 'Family':
        continue
        print('CREATE\nLAST|Len|"{}"\nLAST|Den|"InterPro protein family"\nLAST|Aen|"{}"\nLAST|Aen|"{}"\nLAST|P31|Q417841|S248|Q81384305\nLAST|P2926|"{}"|S248|Q81384305'.format(
            name, entry.attrib.get('short_name'), nipr, nipr))
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    print('LAST|P279|{}|S248|Q81384305'.format(qits.get(ref)))
        else:
            print('LAST|P279|Q8054|S248|Q81384305')
        if ct is not None and len(ct) > 0:
            for p in ct:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    print('LAST|P527|{}|S248|Q81384305'.format(qits.get(ref)))
    if type == 'Domain':
        continue
        print('CREATE\nLAST|Len|"{}"\nLAST|Den|"InterPro domain"\nLAST|Aen|"{}"\nLAST|Aen|"{}"\nLAST|P31|Q898273|S248|Q81384305\nLAST|P2926|"{}"|S248|Q81384305'.format(
            name, entry.attrib.get('short_name'), nipr, nipr))
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    print('LAST|P279|{}|S248|Q81384305'.format(qits.get(ref)))
    if type == 'Conserved_site':
        continue
        print('CREATE\nLAST|Len|"{}"\nLAST|Den|"InterPro Conserved Site"\nLAST|Aen|"{}"\nLAST|Aen|"{}"\nLAST|P31|Q7644128|S248|Q81384305\nLAST|P2926|"{}"|S248|Q81384305'.format(
            name, entry.attrib.get('short_name'), nipr, nipr))
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    print('LAST|P279|{}|S248|Q81384305'.format(qits.get(ref)))
        if fi is not None and len(fi) > 0:
            for p in fi:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    print('LAST|P361|{}|S248|Q81384305'.format(qits.get(ref)))
    if type == 'Repeat':
        print('CREATE\nLAST|Len|"{}"\nLAST|Den|"InterPro Repeat"\nLAST|Aen|"{}"\nLAST|Aen|"{}"\nLAST|P31|Q3273544|S248|Q81384305\nLAST|P2926|"{}"|S248|Q81384305'.format(
            name, entry.attrib.get('short_name'), nipr, nipr))
        if pl is not None and len(pl) > 0:
            for p in pl:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    print('LAST|P279|{}|S248|Q81384305'.format(qits.get(ref)))
        if fi is not None and len(fi) > 0:
            for p in fi:
                if p.tag == 'rel_ref':
                    ref = p.attrib.get('ipr_ref')
                    print('LAST|P361|{}|S248|Q81384305'.format(qits.get(ref)))
