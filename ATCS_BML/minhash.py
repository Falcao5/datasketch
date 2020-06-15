import itertools
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


def calculate_actual_inclusion_coefficient(column_1, column_2):
    set_column1 = set(column_1)
    set_column2 = set(column_2)
    actual_inclusion_coefficient = len(set_column1.intersection(set_column2)) / len(set_column1)

    return actual_inclusion_coefficient


def compute_minhash(column_1, column_2):
    estimated_values = ()

    # calculate actual inclusion coefficient for evaluation purposes
    actual_inclusion_coefficient = calculate_actual_inclusion_coefficient(column_1, column_2)

    # computing minhash for both columns
    sx, sy, su = minhash(column_1, column_2)

    # calculating jaccard similarity
    jaccard_col1_col2 = sx.jaccard(sy)
    jaccard_union_col1 = su.jaccard(sx)

    # estimated inclusion coefficient
    try:
        inclusion_coefficient = jaccard_col1_col2 / jaccard_union_col1
    except ZeroDivisionError:
        inclusion_coefficient = 0.0
    if round(actual_inclusion_coefficient, 1) == round(inclusion_coefficient, 1):
        estimated_values = inclusion_coefficient, actual_inclusion_coefficient

    return inclusion_coefficient, estimated_values


def parse_line(line):
    key, col = line.split('\t')
    column = col.split(',')
    # remove \n from last element of column
    column[-1] = column[-1][:-1]

    return key, column


def parse_dataset(dataset_1, dataset_2):
    dataset_1_list = []
    dataset_2_list = []
    # open a stream with the first dataset of the pair
    with open(DATA_DIR + dataset_1) as column_x:
        for line in column_x:
            # save into this variable all the values for this column
            key1, column_1 = parse_line(line)
            dataset_1_list.append((key1, column_1))

    # open a stream with the second dataset of the pair
    with open(DATA_DIR + dataset_2) as column_y:
        for line1 in column_y:
            # save into this variable all the values for this column
            key2, column_2 = parse_line(line1)
            dataset_2_list.append((key2, column_2))

    return dataset_1_list, dataset_2_list


def evaluate_results(values_list, lenght):
    count = 0
    for elem in values_list:
        if len(elem) > 0:
            count += 1

    precision = count / lenght

    print('Minhash Precision: ', precision)


def compute_cartesian_product(dataset_1, dataset_2):
    predictions_list = []
    dataset_x_list, dataset_y_list = parse_dataset(dataset_1, dataset_2)

    for couple in itertools.product(dataset_x_list, dataset_y_list):
        key1 = couple[0][0]
        key2 = couple[1][0]
        column_x = couple[0][1]
        column_y = couple[1][1]

        # compute the inclusion coefficent between these columns
        inclusion_coefficent, predictions = compute_minhash(column_x, column_y)
        predictions_list.append(predictions)
        print("Inclusion coefficent between column", key1, " and column ", key2, " is: ", inclusion_coefficent)

    lenght = len(list(itertools.product(dataset_x_list, dataset_y_list)))
    evaluate_results(predictions_list, lenght)


def main(argv):
    # tuning on a python limit in recursive algorithms
    sys.setrecursionlimit(10 ** 3)
    # check if at least two dataset names are given
    if len(argv) < 3:
        print("I need at least two datasets representing columns to calculate the inclusion coefficent.")

    # for each pair of dataset names
    for pair in itertools.combinations(argv[1:], 2):
        dataset_x = download_dataset_if_needed(pair[0])
        dataset_y = download_dataset_if_needed(pair[1])

        compute_cartesian_product(dataset_x, dataset_y)


if __name__ == "__main__":
    main(sys.argv)
