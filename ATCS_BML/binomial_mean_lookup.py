import itertools
import math
import sys

from datasketch import HyperLogLog
from dataset_provision import download_dataset_if_needed
from dataset_provision import DATA_DIR

TOLERANCE = 10 ** -4


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


# this is the implementation of the equation 6 described in the paper
def equation_6(k, nx, ny):
    result = 0
    for i in range(0, k):
        result += support_function_1(nx, k) * support_function_3(ny, k)
    return result


# this is the implementation of the equation 7 described in the paper
def equation_7(k, nx, nt):
    result = 0
    for i in range(0, k):
        result += support_function_1(nx, k) * support_function_3(nt, k)
    return result


# this is the implementation of the equation 8 described in the paper
def equation_8(k, nx, ny, nt):
    result = 0
    for i in range(0, k):
        result += (support_function_1(nx, k) * support_function_2(nt, k) * support_function_3(ny, k)) + \
                  (support_function_1(nx, k) * support_function_3(nt, k) * support_function_2(ny, k)) + \
                  (support_function_1(nx, k) * support_function_3(nt, k) * support_function_3(ny, k))

    return result


# this function represents an implementation of algorithm 2 described in the paper.
def lookup(P, min, max, nx, ny, k):
    # n-tau
    nt = (min + max) / 2
    # inclusion coefficient estimated
    phi = nt / nx
    # exponents for the equations 6,7 and 8, as described in the paper
    nxx = nx - nt
    nyy = ny - nt

    # if distinct count estimations are the same (nx = ny)
    if nt == nx and nt == ny:
        prob = 1.0
    # case 1: TAU = (X intersection Y) is empty
    # n-tau = 0, nxx = nx, nyy = ny
    # X and Y are disjoint
    elif nt == 0:               # equation 6
        print("Case 1 - Equation 6")
        prob = equation_6(k, nxx, nyy)
    # case 2: Y is a subset of X
    # Y - T is empty
    # n-tau = ny, nxx = nx - ny, nyy = 0
    elif nx > ny and nt == ny:  # equation 7
        print("Case 2 - Equation 7")
        prob = equation_7(k, nxx, nt)
    # case 3:
    # X and Y are partially overlapped
    else:                       # equation 8
        print("Case 3 - Equation 8")
        prob = equation_8(k, nxx, nyy, nt)

    print_lookup_internal_state(P, min, max, nx, ny, k, prob, nt, phi, nxx, nyy)
    print("==============================")

    # convergence criteria
    if abs(prob - P) <= TOLERANCE:
        return phi
    # recursion 1
    if prob > P:
        return lookup(P, nt, max, nx, ny, k)
    # recursion 2
    if prob < P:
        return lookup(P, min, nt, nx, ny, k)


def estimate_distinct_values_for_column(c):
    # crete a HyperLogLog object
    hll = HyperLogLog()
    # for each value in the column

    for value in c:
        # add it in the HyperLogLog object
        hll.update(value.encode('utf8'))

    # estimate distinct values in column c
    n = hll.count()

    return n


# creates a HyperLogLog sketch based on the column, and with 2^m buckets.
def create_hll_sketch_from_column(column, m):
    # crete a HyperLogLog object with 2^m buckets
    hll = HyperLogLog(p=m)

    # for each value in the column
    for x in column:
        # add it in the HyperLogLog object
        hll.update(x.encode('utf8'))

    # calculate the sketch composed by 2^m buckets
    sketch = hll.digest()

    return sketch


# uses the method given in the paper to calculate the number of bits to use to bucketize, (and the number of buckets): m
def calculate_m(column_1, column_2):
    # estimate distinct counts for each column in the couple
    n_1 = estimate_distinct_values_for_column(column_1)
    n_2 = estimate_distinct_values_for_column(column_2)

    # calculate m as follow
    m = round(math.log(max(n_1, n_2) / 2))

    return m


# this function represents an implementation of the algorithm 1 described in the paper
def binomial_mean_lookup(column_1, column_2):
    # calculate the number of bits required to bucketize the values
    m = calculate_m(column_1, column_2)

    # HyperLogLog uses a hash function which returns a 32 bit value. l parameter results so 32.
    l = 32

    # calculate the HyperLogLog sketches
    s_x = create_hll_sketch_from_column(column_1, m)
    s_y = create_hll_sketch_from_column(column_2, m)

    # I used the same 'm' parameter to create sketch for X and for Y. Length of X and Y sketcher, are the same so:
    buckets_number = len(s_x)

    # this is the number of bits used to represent the value inside the sketch (m are used to bucketize)
    k = l - m
    # this is a counter used to count how many X buckets values (the l-m portion of the string) are not greater than Y
    z = 0

    for i in range(1, buckets_number):
        # if the value in the i-bucket of the x sketch, is greater then the i-bucket value in the y sketch
        if s_x[i] <= s_y[i]:
            # increase counter
            z = z+1

    # ration of number of buckets coming from X sketch with a value not greater then the Y sketch one.
    P = z/pow(2, buckets_number)

    # This count has been done in a function above. Optimizing this, may increase performance on big datasets
    n_x = estimate_distinct_values_for_column(column_1)
    n_y = estimate_distinct_values_for_column(column_2)

    # now execute the lookup phase of the algorithm
    result = lookup(P, 0, min(n_x, n_y), n_x, n_y, k)
    return result


def main(argv):
    # tuning on a python limit in recursive algorithms
    sys.setrecursionlimit(10 ** 3)
    # check if at least two dataset names are given
    if len(argv) < 3:
        print("I need at least two datasets representing columns to calculate the inclusion coefficent.")

    # for each pair of dataset names
    for pair in itertools.combinations(argv[1:], 2):
        column_x_name = download_dataset_if_needed(pair[0])
        column_y_name = download_dataset_if_needed(pair[1])

        # open a stream with the first dataset of the pair
        with open(DATA_DIR + column_x_name) as column_x:
            # open a stream with the second dataset of the pair
            with open(DATA_DIR + column_y_name) as column_y:

                # save into this variable all the values for this column
                column_1 = column_x.readlines()
                # save into this variable all the values for this column
                column_2 = column_y.readlines()

                # compute the inclusion coefficent between these columns
                print("I'll try to solve this in ", sys.getrecursionlimit(), " recursive iterations.")

                inclusion_coefficent = binomial_mean_lookup(column_1, column_2)
                print("Inclusion coefficent between ", column_x_name, " and ", column_y_name, " is: ", inclusion_coefficent)


if __name__ == "__main__":
    main(sys.argv)