# coding=utf-8
from __future__ import unicode_literals
import tensorflow as tf
from apps.asynctask.tasks.base import MLBaseTask
from apps.asynctask import app
import os
import re
import numpy as np
from PIL import Image
from cStringIO import StringIO
MODEL_DIR = "data/imagenet"
NUM_TOP_PREDICTIONS = 5


class NodeLookup(object):
    """Converts integer node ID's to human readable labels."""

    def __init__(self,
                 label_lookup_path=None,
                 uid_lookup_path=None):
        if not label_lookup_path:
            label_lookup_path = os.path.join(
                MODEL_DIR, 'imagenet_2012_challenge_label_map_proto.pbtxt')
        if not uid_lookup_path:
            uid_lookup_path = os.path.join(
                MODEL_DIR, 'imagenet_synset_to_human_label_map.txt')
        self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

    def load(self, label_lookup_path, uid_lookup_path):
        """Loads a human readable English name for each softmax node.

        Args:
          label_lookup_path: string UID to integer node ID.
          uid_lookup_path: string UID to human-readable string.

        Returns:
          dict from integer node ID to human-readable string.
        """
        if not tf.gfile.Exists(uid_lookup_path):
            tf.logging.fatal('File does not exist %s', uid_lookup_path)
        if not tf.gfile.Exists(label_lookup_path):
            tf.logging.fatal('File does not exist %s', label_lookup_path)

        # Loads mapping from string UID to human-readable string
        proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
        uid_to_human = {}
        p = re.compile(r'[n\d]*[ \S,]*')
        for line in proto_as_ascii_lines:
            parsed_items = p.findall(line)
            uid = parsed_items[0]
            human_string = parsed_items[2]
            uid_to_human[uid] = human_string

        # Loads mapping from string UID to integer node ID.
        node_id_to_uid = {}
        proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
        for line in proto_as_ascii:
            if line.startswith('  target_class:'):
                target_class = int(line.split(': ')[1])
            if line.startswith('  target_class_string:'):
                target_class_string = line.split(': ')[1]
                node_id_to_uid[target_class] = target_class_string[1:-2]

        # Loads the final mapping of integer node ID to human-readable string
        node_id_to_name = {}
        for key, val in node_id_to_uid.items():
            if val not in uid_to_human:
                tf.logging.fatal('Failed to locate: %s', val)
            name = uid_to_human[val]
            node_id_to_name[key] = name

        return node_id_to_name

    def id_to_string(self, node_id):
        if node_id not in self.node_lookup:
            return ''
        return self.node_lookup[node_id]


@app.task(bind=True, base=MLBaseTask, typing=False)
def ClassifyImageTask(self, image, **kwargs):
    image.seek(0)
    new_image = Image.open(image)
    if new_image.size != (100, 100):  # resize
        width, height = new_image.size
        if width > height:
            left = (width - height) / 2
            right = width - left
            top = 0
            bottom = height
        else:
            top = (height - width) / 2
            bottom = height - top
            left = 0
            right = width
        new_image = new_image.crop((left, top, right, bottom))
        new_image = new_image.resize([100, 100],
                                     Image.ANTIALIAS)
    s = StringIO()
    new_image.save(s, "jpeg")
    s.seek(0)
    image_data = s.read()
    with tf.gfile.FastGFile(
            os.path.join(MODEL_DIR, 'classify_image_graph_def.pb'),
            'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    with tf.Session() as sess:
        softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
        predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
        predictions = np.squeeze(predictions)
        node_lookup = NodeLookup()

        top_k = predictions.argsort()[NUM_TOP_PREDICTIONS:][::-1]
        result = []
        for node_id in top_k:
            human_string = node_lookup.id_to_string(node_id)
            score = predictions[node_id]
            if score > 0.01:
                result.append({
                    "human_string": human_string,
                    "score": float(score)
                })
        return result
