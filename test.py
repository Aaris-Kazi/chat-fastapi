# x,n = 5,2
# x,n = 4,3
# print(x, n)
x, n = map(int, input().split())
for i in range(n):
    x = x*2

print(x)
