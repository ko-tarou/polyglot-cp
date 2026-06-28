import sys
a,d,n=map(int,sys.stdin.read().split())
print(n*(2*a+(n-1)*d)//2)
