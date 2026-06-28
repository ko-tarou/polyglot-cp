import sys
d=sys.stdin.read().split()
n=int(d[0])
a=list(map(int,d[1:1+n]))
b=list(map(int,d[1+n:1+2*n]))
print(sum(x*y for x,y in zip(a,b)))
