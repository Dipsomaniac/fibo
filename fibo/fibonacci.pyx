def fibo(a, b, todo=1000):
    result = []
    for _ in range(todo):
        result.append(a)
        a, b = b, a + b
    return a, b, result
