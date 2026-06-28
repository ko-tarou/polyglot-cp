import sys
n=int(sys.stdin.read())
if n<2:
 print(0)
else:
 s=[True]*(n+1)
 s[0]=s[1]=False
 i=2
 while i*i<=n:
  if s[i]:
   for j in range(i*i,n+1,i):s[j]=False
  i+=1
 print(sum(s))
