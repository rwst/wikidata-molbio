from sys import *

for i in set(open('t', 'r').readlines()):
    print('{}|P361|Q423042|S887|Q75728677'.format(i.rstrip()))
    print('-{}|P279|Q8054'.format(i.rstrip()))
