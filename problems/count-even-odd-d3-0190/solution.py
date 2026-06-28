import sys
d=sys.stdin.read().split()
n=int(d[0])
a=list(map(int,d[1:1+n]))
e=sum(1 for x in a if x%2==0)
print(e,n-e)
