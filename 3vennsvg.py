from sys import *
from matplotlib_venn import venn3, venn3_circles
from matplotlib import pyplot as plt

s1 = set(open('wd-inst-of-prot', 'r').readlines())
s2 = set(open('wd-subc-of-prot', 'r').readlines())
s3 = set(open('wd-refseqp', 'r').readlines())
#s4 = set(open('t4', 'r').readlines())
venn3([s3,s2,s1], ('RefSeq', 'subc', 'inst of protein'))
c = venn3_circles([s3,s2,s1])
c[0].set_lw(1.0)
plt.show()
#plt.savefig('venn.svg')
