import itertools
import math
import sys

from datasketch import HyperLogLog


def create_hll_sketch_from_column_specific_m(column, m):
    hll = HyperLogLog()
    hll.m = m

    for x in column:
        hll.update(x.encode('utf8'))

    sketch = hll.digest()
    n = hll.count()

    return sketch, n


def print_lookup_internal_state(P, min, max, nx, ny, k, prob, nt, phi, nxx, nyy):
    print("P = ", P)
    print("min = ", min)
    print("max = ", max)
    print("nx = ", nx)
    print("ny = ", ny)
    print("k = ", k)
    print("prob = ", prob)
    print("nt = ", nt)
    print("phi = ", phi)
    print("nxx = ", nxx)
    print("nyy = ", nyy)


# [1 - 1/(2^k)]^n
def support_function_1(n, k):
    base = 1 - 1 / pow(2, k)
    return pow(base, n)


# { 1 - 1/[2^(k-1)] }^n
def support_function_2(n, k):
    base = 1 - 1 / pow(2, k - 1)
    return pow(base, n)


# (1 - 1/(2^k))^n
def support_function_3(n, k):
    return support_function_1(n, k) - support_function_2(n, k)


def equation_6(k, nx, ny):
    result = 0
    for i in range(0, k):
        result += support_function_1(nx, k) * support_function_3(ny, k)
    return result


def equation_7(k, nx, nt):
    result = 0
    for i in range(0, k):
        result += support_function_1(nx, k) * support_function_3(nt, k)
    return result


def equation_8(k, nx, ny, nt):
    result = 0
    for i in range(0, k):
        result += (support_function_1(nx, k) * support_function_2(nt, k) * support_function_3(ny, k)) + \
                  (support_function_1(nx, k) * support_function_3(nt, k) * support_function_2(ny, k)) + \
                  (support_function_1(nx, k) * support_function_3(nt, k) * support_function_3(ny, k))

    return result


def lookup(P, min, max, nx, ny, k):
    ########################################################### prolly this function is not ok
    err = 0.5
    nt = (min + max) / 2
    phi = nt / nx
    nxx, nyy = nx - nt, ny - nt                     # esponenti sono i complementari di nx e ny non nx e ny
    # print_lookup_internal_state(P, min, max, nx, ny, k, prob, nt, phi, nxx, nyy)

    if nt == nx and nt == ny:
        prob = 1.0
    elif nt == 0:               # equation 6
        prob = equation_6(k, nx, ny)
    elif nx > ny and nt == ny:  # equation 7
        prob = equation_7(k, nx, nt)
    else:                       # equation 8
        prob = equation_8(k, nx, ny, nt)

    if abs(prob - P) <= err:
        return phi
    if prob > P:
        return lookup(P, nt, max, nx, ny, k)
    if prob < P:
        return lookup(P, min, nt, nx, ny, k)


def estimate_distinct_values_for_sketch(s):
    hll = HyperLogLog()
    hll.reg = s
    return hll.count()


def estimate_distinct_values_for_column(c):
    hll = HyperLogLog()
    for value in c:
        hll.update(value.encode('utf8'))

    n = hll.count()    # estimated distinct values in column 1

    return n


def create_hll_sketch_from_column(column, m, l):
    hll = HyperLogLog()

    for x in column:
        hll.update(x.encode('utf8'))

    sketch = hll.digest()

    return sketch


def calculate_m(column_1, column_2):
    n_1 = estimate_distinct_values_for_column(column_1)
    n_2 = estimate_distinct_values_for_column(column_2)

    m = round(math.log(max(n_1, n_2) / 2))

    return m


def binomial_mean_lookup(column_1, column_2):
    m = calculate_m(column_1, column_2)
    l = 32

    s_x = create_hll_sketch_from_column(column_1, m, l)
    s_y = create_hll_sketch_from_column(column_2, m, l)

    buckets_number = len(s_x)
    k = l - m
    z = 0

    for i in range(0, buckets_number):
        # if the value in the i-bucket of the x sketch, is greater then the i-bucket value in the y sketch
        if s_x[i] <= s_y[i]:
            z = z+1

    P = z/pow(2, buckets_number)

    n_x = estimate_distinct_values_for_sketch(s_x)  # for sketch, or for column?
    n_y = estimate_distinct_values_for_sketch(s_y)  # for sketch, or for column?

    return lookup(P, 0, min(n_x, n_y), n_x, n_y, k)


def main(argv):
    sys.setrecursionlimit(10 ** 9)
    # for each pair of dataset names
    for pair in itertools.combinations(argv[1:], 2):
        with open('data/' + pair[0]) as column_x:       # open first dataset of the pair
            with open('data/' + pair[1]) as column_y:   # open second dataset of the pair
                column_1 = column_x.readlines()
                column_2 = column_y.readlines()
                print(binomial_mean_lookup(column_1, column_2))


if __name__ == "__main__":
    main(sys.argv)