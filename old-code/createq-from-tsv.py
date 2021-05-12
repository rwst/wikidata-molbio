
import csv
from sys import *

reader = csv.DictReader(open('tt.tsv', 'r'), delimiter='\t')
for item in reader:
    ch = item.get('CHEBI')
    na = item.get('name')
    s1 = item.get('sub1')
    ik = item.get('ik')
    s2 = None
    s3 = None
    print('CREATE\nLAST|Len|"{}"\nLAST|Den|"chemical compound"\nLAST|P31|Q11173|S248|Q69633402\nLAST|P31|{}|S248|Q69633402\nLAST|P235|"{}"|S248|Q69633402\nLAST|P683|"{}"|S248|Q69633402'.format(na,s1,ik,ch))
    re = item.get('Reaxys')
    if re is not None and len(re)>0:
        print('LAST|P1579|"{}"|S248|Q69633402'.format(re[7:]))
    s2 = item.get('sub2')
    if s2 is not None and len(s2)>0:
        print('LAST|P31|{}|S248|Q69633402'.format(s2))
    s3 = item.get('sub3')
    if s3 is not None and len(s3)>0:
        print('LAST|P31|{}|S248|Q69633402'.format(s3))

