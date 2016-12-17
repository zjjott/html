# coding=utf-8
from __future__ import unicode_literals
import tensorflow as tf

from tensorflow.contrib.layers import real_valued_column
from apps.asynctask.tasks.base import MLBaseTask
from apps.taskapi.models import (MethodKwargs,
                                 MLMethod)
from apps.dataset.models import DatasetModel
from apps.dataset.utils import (load_dataset, flat_numpy)
from cPickle import loads, dumps, HIGHEST_PROTOCOL
from apps.asynctask import app
from cStringIO import StringIO
from tempfile import mkdtemp, mkstemp
import os
import tarfile
from shutil import rmtree
# Load datasets.


@app.task(bind=True, base=MLBaseTask, typing=False)
def CustomerTrainTask(self, dataset_id, model_id,
                      user_id, **kwargs):
    steps = 2000
    dataset = DatasetModel.query().get(dataset_id)
    csv_file = StringIO(dataset.data)
    training_set = load_dataset(csv_file)
    model_attrs = {}
    if "dimension" in kwargs:
        model_attrs["feature_columns"] = [
            real_valued_column("",
                               dimension=kwargs['dimension'])]
    if "hidden_units" in kwargs:
        model_attrs['hidden_units'] = map(int, kwargs['hidden_units'])
    if "n_classes" in kwargs:
        model_attrs['n_classes'] = kwargs['n_classes']
    model_db = MLMethod.query().get(model_id)
    model = loads(model_db.data)
    temp_folder = mkdtemp()
    fd, filepath = mkstemp(suffix="tar.gz")
    try:
        classifier = model(model_dir=temp_folder,
                           **model_attrs)
        classifier = classifier.fit(x=training_set.data,
                                    y=training_set.target,
                                    steps=steps
                                    )
        tar = tarfile.open(filepath, "w:gz")
        tar.add(temp_folder, arcname="model")
        tar.close()
        with open(filepath, "rb") as fout:
            trained = MLMethod(user_id=user_id,
                               name=model_db.name,
                               description="%s 在 %s 上的模型" % (
                                   model_db.name, dataset.name),
                               public=model_db.public,
                               trained=True,
                               data=dumps(
                                   (CustomerPredictTask,
                                    model,
                                    kwargs,
                                    fout.read()
                                    ),
                                   HIGHEST_PROTOCOL)
                               )
        trained.save_object()
        MethodKwargs(model_id=trained.id,
                     name="file",
                     label="数据文件",
                     description="数据文件和文本数据选其一即可",
                     required=False,
                     type="file",
                     ).save_object()
        MethodKwargs(model_id=trained.id,
                     name="data",
                     label="数据文本",
                     description="数据文件和文本数据选其一即可",
                     required=False,
                     type="str",
                     ).save_object()
    finally:
        # 删这个文件会报错，所以干脆不删好了。。
        pass
        # os.unlink(filepath)
        # rmtree(temp_folder)
        # MethodKwargs(model_id)
    return trained.id

@app.task(bind=True, base=MLBaseTask, typing=False)
def CustomerPredictTask(self, model_id, **kwargs):
    data = kwargs.get("data")
    file = kwargs.get("file")
    if not file and not data:
        raise ValueError("起码给我一个预测的数据吧")

    model_db = MLMethod.query().get(model_id)
    temp_folder = mkdtemp()
    fd, filepath = mkstemp(suffix="tar.gz")
    try:

        _, modelclass, model_kwargs, model_data = loads(model_db.data)
        with open(filepath, "wb") as fin:
            fin.write(model_data)
        model_attrs = {}

        if "dimension" in model_kwargs:
            model_attrs["feature_columns"] = [
                real_valued_column("",
                                   dimension=model_kwargs['dimension'])]
        if "hidden_units" in model_kwargs:
            model_attrs['hidden_units'] = model_kwargs['hidden_units']
        if "n_classes" in model_kwargs:
            model_attrs['n_classes'] = model_kwargs['n_classes']
        if file and not data:
            file.seek(0)
            dataset = load_dataset(file)
            data = dataset.data
        print data
        tar = tarfile.open(filepath, 'r:gz')
        tar.extractall(temp_folder)

        model = modelclass(model_dir=temp_folder + "/model",
                           **model_attrs)
        predictions = model.predict(data, as_iterable=False)

        return flat_numpy(predictions)

    finally:
        os.unlink(filepath)
        rmtree(temp_folder)
