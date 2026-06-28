import sys
s=sys.stdin.read().strip()
print('Yes' if s==s[::-1] else 'No')
