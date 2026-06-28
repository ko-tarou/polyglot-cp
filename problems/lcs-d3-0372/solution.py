import sys
l=sys.stdin.read().split('\n')
s,t=l[0],l[1]
m,n=len(s),len(t)
dp=[0]*(n+1)
for i in range(m):
 nd=[0]*(n+1)
 for j in range(n):
  nd[j+1]=dp[j]+1 if s[i]==t[j] else max(dp[j+1],nd[j])
 dp=nd
print(dp[n])
