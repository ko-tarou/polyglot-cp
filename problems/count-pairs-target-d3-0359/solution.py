import sys
from collections import Counter
d=sys.stdin.read().split()
n,k=int(d[0]),int(d[1])
a=list(map(int,d[2:2+n]))
c=Counter()
ans=0
for x in a:
 ans+=c[k-x]
 c[x]+=1
print(ans)
