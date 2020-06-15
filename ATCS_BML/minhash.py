import itertools
import math
import sys

from datasketch import MinHash
from dataset_provision import download_dataset_if_needed
from dataset_provision import DATA_DIR


def minhash(col1, col2):
    set_column1 = set(col1)
    set_column2 = set(col2)
    union = set_column1.union(set_column2)

    minhash = MinHash()
    for elem in col1:
        minhash.update(elem.encode('utf8'))
    hash1 = minhash

    minhash = MinHash()
    for elem in col2:
        minhash.update(elem.encode('utf8'))
    hash2 = minhash

    minhash = MinHash()
    for elem in union:
        minhash.update(elem.encode('utf8'))
    hash3 = minhash

    return hash1, hash2, hash3


def parse_line(line):
    key, col = line.split('\t')
    column = col.split(',')
    # remove \n from last element of column
    column[-1] = column[-1][:-1]

    return key, column


def calculate_actual_inclusion_coefficient(column_1, column_2):
    set_column1 = set(column_1)
    set_column2 = set(column_2)
    actual_inclusion_coefficient = len(set_column1.intersection(set_column2)) / len(set_column1)

    return actual_inclusion_coefficient


def compute_minhash(column_1, column_2):
    actual_inclusion_coefficient = calculate_actual_inclusion_coefficient(column_1, column_2)

    sx, sy, su = minhash(column_1, column_2)

    jaccard_col1_col2 = sx.jaccard(sy)
    jaccard_union_col1 = su.jaccard(sx)
    try:
        inclusion_coefficient = jaccard_col1_col2 / jaccard_union_col1
    except ZeroDivisionError:
        inclusion_coefficient = 0.0

    # print(inclusion_coefficient, actual_inclusion_coefficient)

    return inclusion_coefficient


def compute_cartesian_product(column_x_name, column_y_name):
    # open a stream with the first dataset of the pair
    with open(DATA_DIR + column_x_name) as column_x:
        # open a stream with the second dataset of the pair
        with open(DATA_DIR + column_y_name) as column_y:

            for line in column_x:
                key1, column_1 = parse_line(line)
                # save into this variable all the values for this column

                for line1 in column_y:
                    # save into this variable all the values for this column
                    key2, column_2 = parse_line(line1)

                    # compute the inclusion coefficent between these columns
                    print("I'll try to solve this in ", sys.getrecursionlimit(), " recursive iterations.")
                    inclusion_coefficent = compute_minhash(column_1, column_2)
                    print("Inclusion coefficent between column", key1, " and column ", key2, " is: ", inclusion_coefficent)


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

        compute_cartesian_product(column_x_name, column_y_name)


if __name__ == "__main__":
    main(sys.argv)
