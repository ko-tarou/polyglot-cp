import sys
d=sys.stdin.read().split()
n,k=int(d[0]),int(d[1])
a=list(map(int,d[2:2+n]))
seen=set()
ok=False
for x in a:
 if k-x in seen:ok=True;break
 seen.add(x)
print('Yes' if ok else 'No')
