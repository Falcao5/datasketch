# Advanced Topics in Computer Science
This project is for university purposes. The scope is to write the algorithm described [this paper](https://dl.acm.org/doi/10.14778/3231751.3231759).
This project is being developed by **Marte Valerio Falcone**, and **Ebtheal El Marzouki**.

## Prerequisites
Mandatory for everyone:
- Python 3.x
- Install datasketch: `pip install datasketch`

### If you want to use dataset download feature 

**Windows** users:
- gzip (look [here](http://gnuwin32.sourceforge.net/packages/gzip.htm))
- curl

**Unix** users:
- wget

## Usage
Open a terminal in the root folder of this project, then

1. Move in ATCS_BML directory: `cd ATCS_BML`
2. Make the data directory: `mkdir data`
3. Execute the python script: `python binomial_mean_lookup.py <dataset_1> <dataset_2> ... <dataset_n>`

### Datasets explanation

The _datasets_ required in the third point, must be values of a vector (maybe the values of a column in a database) separated by newline: each value is a line.

There is a list of datasets that our teacher told us to use, this list is reachable at [this repo](https://github.com/ekzhu/set-similarity-search-benchmarks)
Instead of manually downloading these datasets, you can easily write the name of the dataset you wish to use (including .gz), and the script will automatically download it.

## Algorithm parameters tuning

The only parameter on which you can do tuning, is the tolerance, or error (see the [paper](https://dl.acm.org/doi/10.14778/3231751.3231759) for more details).
You can tune it by editing the script binomial_mean_lookup.py in the top of the file.