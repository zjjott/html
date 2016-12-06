# coding=utf-8
from __future__ import unicode_literals
import tensorflow as tf
from tensorflow.contrib.learn import DNNClassifier

import csv
import os
from os import path
import tempfile


from tensorflow.contrib.framework import deprecated
from tensorflow.python.platform import gfile
from tensorflow.contrib.layers import real_valued_column
from apps.asynctask.tasks.base import MLBaseTask
from apps.dataset.utils import load_system_dataset
from celery.registry import tasks
from apps.asynctask import app
IRIS_TRAINING = "iris_training.csv"
IRIS_TEST = "iris_test.csv"

# Load datasets.


@app.task(bind=True, base=MLBaseTask)
def DNNClassifierTrainTask(self, datasource, train_path, test_path, **kwargs):
    steps = kwargs.pop("steps", 2000)
    if datasource == 'system':  # data from system
        training_set = load_system_dataset(train_path)
        if test_path:
            test_set = load_system_dataset(test_path)
        feature_columns = [real_valued_column("", dimension=4)]
        classifier = DNNClassifier(feature_columns=feature_columns,
                                   **kwargs
                                   # hidden_units=[10, 20, 10],
                                   # n_classes=3
                                   )
        if test_path:
            classifier.fit(x=training_set.data,
                           y=training_set.target, steps=steps
                           )
            accuracy_score = classifier.evaluate(x=test_set.data,
                                                 y=test_set.target)["accuracy"]
            return accuracy_score
        

