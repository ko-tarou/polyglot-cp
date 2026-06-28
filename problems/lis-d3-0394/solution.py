import sys,bisect
d=sys.stdin.read().split()
n=int(d[0])
a=list(map(int,d[1:1+n]))
t=[]
for x in a:
 i=bisect.bisect_left(t,x)
 if i==len(t):t.append(x)
 else:t[i]=x
print(len(t))
