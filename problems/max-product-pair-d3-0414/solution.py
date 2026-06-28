import sys
d=sys.stdin.read().split()
n=int(d[0])
a=sorted(map(int,d[1:1+n]))
print(max(a[-1]*a[-2],a[0]*a[1]))
