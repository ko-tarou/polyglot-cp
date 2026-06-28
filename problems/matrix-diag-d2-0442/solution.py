import sys
data=sys.stdin.read().split()
n=int(data[0])
s=sum(int(data[1+i*n+i]) for i in range(n))
print(s)
