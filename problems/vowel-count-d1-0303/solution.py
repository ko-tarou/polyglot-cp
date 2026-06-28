import sys
s=sys.stdin.read().strip()
print(sum(1 for c in s if c in 'aeiou'))
