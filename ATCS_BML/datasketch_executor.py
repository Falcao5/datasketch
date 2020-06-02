import getopt

from datasketch.hyperloglog import HyperLogLog
from datasketch.minhash import MinHash

from dataset_provision import download_dataset_if_needed
from dataset_provision import DATA_DIR

import sys
import time
import itertools

MINHASH_NAME = "minhash"
JACCARD_MINHASH_NAME = "minhash-jaccard"
HYPERLOGLOG_NAME = "hyperloglog"

ALGORITHMS = [MINHASH_NAME, HYPERLOGLOG_NAME, JACCARD_MINHASH_NAME]


def check_input_validity(argv):
    # check
    if len(argv) < 3:  # verify if at least one dataset filename is given
        print("You need to say me what's the dataset to work on.")  # print a message
        print("Usage: " + str(argv[0]) + "<algorithm_name> <dataset_filename1> <dataset_filename2> ... <dataset_filenameN>")  # print a message
        print("You can choose between these algoritms: " + str(ALGORITHMS))
        sys.exit()

    if not argv[1] in ALGORITHMS:
        print("You can choose between these algoritms: " + str(ALGORITHMS))
        print("Hint: type 'python " + argv[0] + " <algorithm_name> <dataset_filename1> <dataset_filename2> ... <dataset_filenameN>")


def data_scout(dataset_filenames):
    valid_and_downloaded_dataset_filenames = []

    for dataset_filename in dataset_filenames:                                                      # for each argument (except this file name)
        downloaded_and_valid_dataset_filename = download_dataset_if_needed(dataset_filename)
        if downloaded_and_valid_dataset_filename:
            valid_and_downloaded_dataset_filenames.append(downloaded_and_valid_dataset_filename)    # download datasets if needed

    return valid_and_downloaded_dataset_filenames


def select_algorithm(algorithm_name):
    algorithm_name = algorithm_name.lower()

    if algorithm_name == MINHASH_NAME or algorithm_name == JACCARD_MINHASH_NAME:
        return MinHash()
    if algorithm_name == HYPERLOGLOG_NAME:
        return HyperLogLog()
    return None


def print_dataset_filename_and_message(message):
    print("******************** [ " + message + " ] ********************")


def calculate_and_print_cardinality(dataset_filename, dataset, algorithm_object, algorithm_name):
    start_time = time.time()

    dataset_lines = dataset.readlines()  # read a line from the dataset
    for dataset_line in dataset_lines:
        dataset_line = str(dataset_line)
        algorithm_object.update(dataset_line.encode('utf8'))  # push the data in the HyperLogLog buffer

    print_dataset_filename_and_message(dataset_filename + " - cardinality")

    calculated_cardinality = algorithm_object.count()
    print(algorithm_name + " calculated this cardinality: ", calculated_cardinality)  # calculate cardinality with HyperLogLog

    set_for_dataset = set(open(DATA_DIR + dataset_filename))  # source dataset for compare
    print("exact cardinality is: ", len(set_for_dataset))  # calculating real cardinality

    print("accuracy is: ", round((100 * calculated_cardinality) / len(set_for_dataset), 2))  # calculating accuracy

    print("cardinality execution time: %s seconds" % (time.time() - start_time))


def calculate_and_print_jaccard(dataset_filename1, dataset_filename2):
    print_dataset_filename_and_message("jaccard " + dataset_filename1 + " - " + dataset_filename2)
    start_time = time.time()
    m1 = MinHash()
    m2 = MinHash()

    # read the first dataset
    with open(DATA_DIR + dataset_filename1) as dataset1:
        dataset_lines = dataset1.readlines()  # read a line from the dataset
        for dataset_line in dataset_lines:
            dataset_line = str(dataset_line)
            m1.update(dataset_line.encode('utf8'))  # push the data in the HyperLogLog buffer

    # read the second dataset
    with open(DATA_DIR + dataset_filename2) as dataset2:
        dataset_lines = dataset2.readlines()  # read a line from the dataset
        for dataset_line in dataset_lines:
            dataset_line = str(dataset_line)
            m2.update(dataset_line.encode('utf8'))  # push the data in the HyperLogLog buffer

    jaccard = m1.jaccard(m2)
    print("jaccard similarity estimated: ", 100 *jaccard)

    s1 = set(open(DATA_DIR + dataset_filename1))
    s2 = set(open(DATA_DIR + dataset_filename2))
    print("true jaccard similarity: ", round(100 * float(len(s1.intersection(s2))) / float(len(s1.union(s2))), 2))

    print("jaccard execution time: %s seconds" % (time.time() - start_time))


def main(argv):
    check_input_validity(argv)
    algorithm_name = argv[1]
    algorithm_object = select_algorithm(algorithm_name)
    valid_and_downloaded_dataset_filenames = data_scout(argv[2:])

    # computation
    for dataset_filename in valid_and_downloaded_dataset_filenames:                                 # for each valid and downloaded dataset
        with open(DATA_DIR + dataset_filename) as dataset:                                          # open a stream with dataset file and iterate over it
            calculate_and_print_cardinality(dataset_filename, dataset, algorithm_object, algorithm_name)

    if algorithm_name == JACCARD_MINHASH_NAME and len(valid_and_downloaded_dataset_filenames) > 1:
        for pair in itertools.combinations(valid_and_downloaded_dataset_filenames, 2):
            calculate_and_print_jaccard(*pair)


if __name__ == "__main__":
    main(sys.argv)