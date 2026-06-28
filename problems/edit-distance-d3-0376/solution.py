import sys
l=sys.stdin.read().split('\n')
s,t=l[0],l[1]
m,n=len(s),len(t)
dp=list(range(n+1))
for i in range(1,m+1):
 prev=dp[0]
 dp[0]=i
 for j in range(1,n+1):
  cur=dp[j]
  dp[j]=prev if s[i-1]==t[j-1] else 1+min(prev,dp[j],dp[j-1])
  prev=cur
print(dp[n])
