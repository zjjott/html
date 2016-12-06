from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import csv


import numpy as np
from tensorflow.python.platform import gfile
from collections import namedtuple
Dataset = namedtuple('Dataset', ['data', 'target'])
Datasets = namedtuple('Datasets', ['train', 'validation', 'test'])


CATOGORY2FILENAME = {
    "iris0": ("data/iris0.csv", np.int, np.float32),
    "iris1": ("data/iris1.csv", np.int, np.float32),
}


class LoadError(Exception):
    pass


def load_system_dataset(catogory, target_column=-1):
    attrs = CATOGORY2FILENAME.get(catogory)
    if attrs is None:
        raise LoadError("there have no catogory:%s" % catogory)
    filename, target_dtype, features_dtype = attrs

    with gfile.Open(filename) as csv_file:
        data_file = csv.reader(csv_file)
        header = next(data_file)
        n_samples = int(header[0])
        n_features = int(header[1])
        data = np.zeros((n_samples, n_features), dtype=features_dtype)
        target = np.zeros((n_samples,), dtype=target_dtype)
        for i, row in enumerate(data_file):
            target[i] = np.asarray(row.pop(target_column), dtype=target_dtype)
            data[i] = np.asarray(row, dtype=features_dtype)
        return Dataset(data=data, target=target)
