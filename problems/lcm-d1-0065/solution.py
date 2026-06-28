import sys,math
a,b=map(int,sys.stdin.read().split())
print(a//math.gcd(a,b)*b)
