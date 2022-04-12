from collections import Counter

with open('nginx_access.log', 'r') as f:
    c = Counter(f.read().splitlines())
    if len(c) != 2:
        print('num of redirection targets unexpected:')
        print(list(c.elements()))
        exit(1)
    num_redirrections = []
    for redirrection in c:
        print(f'to {redirrection}: {c[redirrection]}')
        num_redirrections.append(c[redirrection])
    ratio = num_redirrections[0] / num_redirrections[1]
    print(f'balancing ratio: {ratio}')
    if abs(ratio - 1) > 0.2:
        exit(1)
