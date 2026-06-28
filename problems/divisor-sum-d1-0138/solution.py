import sys
n=int(sys.stdin.read())
s=0
i=1
while i*i<=n:
 if n%i==0:
  s+=i
  if i*i!=n:s+=n//i
 i+=1
print(s)
