import sys
d=sys.stdin.read().split()
n,x=int(d[0]),int(d[1])
a=list(map(int,d[2:2+n]))
ans=-1
for i,v in enumerate(a):
 if v==x:ans=i+1;break
print(ans)
