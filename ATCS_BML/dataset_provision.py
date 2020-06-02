import os.path
import platform
import gzip

DATA_DIR = "data/"

DATASETS_REFERENCES = {
    "BMS-POS_dup_dr.inp.gz": "https://storage.googleapis.com/set-similarity-search/BMS-POS_dup_dr.inp.gz",
    "KOSARAK_dup_dr.inp.gz": "https://storage.googleapis.com/set-similarity-search/KOSARAK_dup_dr.inp.gz",
    "FLICKR-london2y_dup_dr.inp.gz": "https://storage.googleapis.com/set-similarity-search/FLICKR-london2y_dup_dr.inp.gz",
    "NETFLIX_dup_dr.inp.gz": "https://storage.googleapis.com/set-similarity-search/NETFLIX_dup_dr.inp.gz",
    "orkut_ge10.inp.gz": "https://storage.googleapis.com/set-similarity-search/orkut_ge10.inp.gz",
    "canada_us_uk_opendata.inp.gz": "https://storage.googleapis.com/set-similarity-search/canada_us_uk_opendata.inp.gz",
    "canada_us_uk_opendata_queries_1k.inp.gz": "https://storage.googleapis.com/set-similarity-search/canada_us_uk_opendata_queries_1k.inp.gz",
    "canada_us_uk_opendata_queries_10k.inp.gz": "https://storage.googleapis.com/set-similarity-search/canada_us_uk_opendata_queries_10k.inp.gz",
    "canada_us_uk_opendata_queries_100k.inp.gz": "https://storage.googleapis.com/set-similarity-search/canada_us_uk_opendata_queries_100k.inp.gz",
    "wdc_webtables_2015_english_relational.inp.gz": "https://storage.googleapis.com/set-similarity-search/wdc_webtables_2015_english_relational.inp.gz",
    "wdc_webtables_2015_english_relational_queries_100.inp.gz": "https://storage.googleapis.com/set-similarity-search/wdc_webtables_2015_english_relational_queries_100.inp.gz",
    "wdc_webtables_2015_english_relational_queries_1.inp.gz": "https://storage.googleapis.com/set-similarity-search/wdc_webtables_2015_english_relational_queries_1k.inp.gz",
    "wdc_webtables_2015_english_relational_queries_10.inp.gz": "https://storage.googleapis.com/set-similarity-search/wdc_webtables_2015_english_relational_queries_10k.inp.gz",
}


def check_if_dataset_exists(dataset_filename):
    fn = dataset_filename
    result = os.path.exists(DATA_DIR + fn)
    if result:
        return result
    print(fn + " doesn't exist in " + DATA_DIR)
    return result


def check_if_dataset_filename_is_valid(dataset_filename):
    if dataset_filename in DATASETS_REFERENCES.keys():
        return True
    print(dataset_filename + " is not a valid reference. Check DATASET_REFERENCES")
    return False


def download_dataset(dataset_filename):
    if platform.system() == "Windows":
        os.chdir(DATA_DIR)
        print("Using curl for downloading dataset dataset_filename")
        os.system('curl ' + DATASETS_REFERENCES[dataset_filename] + ' --output ' + dataset_filename)
        os.chdir("..")
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.chdir(DATA_DIR)
        print("Using wget for downloading dataset dataset_filename")
        os.system('wget ' + DATASETS_REFERENCES[dataset_filename])
        os.chdir("..")

    if check_if_dataset_exists(dataset_filename):
        return dataset_filename
    return None


def extract_dataset(dataset_filename):
    decompressed_dataset_filename = dataset_filename[:len(dataset_filename) - 3]  # remove .gz

    print("Extracting data...")

    os.chdir(DATA_DIR)
    os.system('gzip -d ' + dataset_filename)
    os.chdir("..")

    return decompressed_dataset_filename


def download_dataset_if_needed(dataset_filename):
    decompressed_dataset_filename = dataset_filename[:len(dataset_filename) - 3]
    if not check_if_dataset_exists(decompressed_dataset_filename) and check_if_dataset_filename_is_valid(dataset_filename):
        print("Dataset " + dataset_filename + " wasn't downloaded, i'll try to download it right now...")

        if download_dataset(dataset_filename) == dataset_filename:
            return extract_dataset(dataset_filename)

    if check_if_dataset_exists(decompressed_dataset_filename):
        return decompressed_dataset_filename

    return None
