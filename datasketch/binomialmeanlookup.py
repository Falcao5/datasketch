from datasketch.hashfunc import sha1_hash32, sha1_hash64


class BinomialMeanLookup(object):

    # TODO
    # support method to calculate n_x or n_y
    def estimate_distinct_values_from_sketch(self, sketch):
        # TODO ???
        return 0

    # TODO
    # support method for calculating rho
    def calculate_probability_that_hll_values_from_x_sketch_are_not_greater_than_y_sketch_hll_values(self, x_sketch, y_sketch):
        result = 0
        m = 0
        z = 0
        # TODO create buckets and calculate Z
        p = z/pow(2, m)
        return p

    # TODO
    # algorithm 1
    # takes in input two column sketches, and gives the inclusion coefficient as output
    def binomial_mean_lookup(self, x_sketch, y_sketch):
        p = self.calculate_probability_that_hll_values_from_x_sketch_are_not_greater_than_y_sketch_hll_values(self, x_sketch, y_sketch)
        n_x = self.estimate_distinct_values_from_sketch(self, x_sketch)  # TODO estimated number of distinct values from sketch X
        n_y = self.estimate_distinct_values_from_sketch(self, y_sketch)  # TODO estimated number of distinct values from sketch Y
        min_inc = 0
        max_inc = min(n_x, n_y)
        convergence = n_y

        inclusion_coefficient = self.lookup(self, p, min_inc, max_inc, n_x, n_y, convergence)
        return inclusion_coefficient

    # TODO
    # algorithm 2
    # p is the probability that the first HLL value is smaller than the second
    # min_inc is the minimum increment
    # max_inc is the maximum increment
    # n_x is the estimated number of distinct values in x sketch
    # n_y is the estimated number of distinct values in y sketch
    # convergence is a number to block the algorithm when a certain value is reached
    def lookup(self, p, min_inc, max_inc, n_x, n_y, convergence):
        return -1

    # TODO
    # algorithm 3
    # this method takes a column as input, and gives a sketch as output
    def create_sketch_from_column(self, column):
        return