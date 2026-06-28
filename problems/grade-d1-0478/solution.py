import sys
x=int(sys.stdin.read())
print('A' if x>=90 else 'B' if x>=70 else 'C' if x>=50 else 'D')
