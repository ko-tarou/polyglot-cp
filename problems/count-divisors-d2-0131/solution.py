import sys
n=int(sys.stdin.read())
c=0
i=1
while i*i<=n:
 if n%i==0:
  c+=1 if i*i==n else 2
 i+=1
print(c)
