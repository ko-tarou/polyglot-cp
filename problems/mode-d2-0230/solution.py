import sys
from collections import Counter
d=sys.stdin.read().split()
n=int(d[0])
a=list(map(int,d[1:1+n]))
c=Counter(a)
m=max(c.values())
print(min(k for k,v in c.items() if v==m))
