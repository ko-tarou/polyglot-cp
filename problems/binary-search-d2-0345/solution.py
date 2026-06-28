import sys,bisect
d=sys.stdin.read().split()
n,x=int(d[0]),int(d[1])
a=list(map(int,d[2:2+n]))
i=bisect.bisect_left(a,x)
print('Yes' if i<n and a[i]==x else 'No')
