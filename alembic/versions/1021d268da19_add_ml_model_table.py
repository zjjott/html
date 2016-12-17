# coding=utf-8
from __future__ import unicode_literals
"""add ml model table

Revision ID: 1021d268da19
Revises: aa0931683486
Create Date: 2016-12-11 17:38:51.276132

"""
from alembic import op
import sqlalchemy as sa
import sys
import os
dirname = os.path.dirname
abspath = os.path.abspath
app_path = abspath(dirname(dirname(dirname(__file__))))
sys.path.insert(0, app_path)
# revision identifiers, used by Alembic.
from apps.core.models.fields import NoConstraintEnum
from tensorflow.contrib.learn import (
    LinearRegressor,
    LinearClassifier,
    DNNRegressor,
    DNNClassifier,
)
from cPickle import dumps, HIGHEST_PROTOCOL
revision = '1021d268da19'
down_revision = 'aa0931683486'
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    methodkwargs_tbl = op.create_table('methodkwargs_tbl',
                                       sa.Column('id', sa.Integer(),
                                                 nullable=False),
                                       sa.Column(
                                           'model_id', sa.Integer(), nullable=True),
                                       sa.Column('name', sa.VARCHAR(
                                           length=20), nullable=True),
                                       sa.Column('label', sa.VARCHAR(
                                           length=50), nullable=True),
                                       sa.Column('required', sa.Boolean(),
                                                 nullable=True),
                                       sa.Column('description',
                                                 sa.Text(), nullable=True),
                                       sa.Column('type', NoConstraintEnum(
                                           u'int', u'list', u'image', native_enum=False), nullable=True),
                                       sa.PrimaryKeyConstraint('id'),
                                       mysql_charset=u'utf8',
                                       mysql_engine=u'InnoDB'
                                       )
    mlmethods_tbl = op.create_table('mlmethods_tbl',
                                    sa.Column('id', sa.Integer(),
                                              nullable=False),
                                    sa.Column('user_id', sa.Integer(),
                                              nullable=True),
                                    sa.Column('name', sa.VARCHAR(
                                        length=20), nullable=True),
                                    sa.Column('description',
                                              sa.Text(), nullable=True),
                                    sa.Column('public', sa.Boolean(),
                                              nullable=True),
                                    sa.Column('trained', sa.Boolean(),
                                              nullable=True),
                                    sa.Column('data', sa.BLOB(),
                                              nullable=True),
                                    sa.PrimaryKeyConstraint('id'),
                                    mysql_charset=u'utf8',
                                    mysql_engine=u'InnoDB'
                                    )
    data = [
        {
            "user_id": None,
            "name": modelclass.__name__,
            "description": modelclass.__doc__,
            "public": True,
            "trained": False,
            "data": dumps(modelclass, HIGHEST_PROTOCOL)
        }
        for modelclass in [
            LinearRegressor,
            LinearClassifier,
            DNNRegressor,
            DNNClassifier,
        ]
    ]
    from apps.asynctask.tasks import ClassifyImageTask
    data.append({
        "user_id": None,
        "name": "imagenet",
        "description": "图像(100x100)分类,类别1000",
        "public": True,
        "trained": True,
        "data": dumps(ClassifyImageTask, HIGHEST_PROTOCOL),
    })
    op.bulk_insert(mlmethods_tbl,
                   data
                   )

    op.bulk_insert(methodkwargs_tbl,
                   [
                       {
                           "model_id": i + 1,
                           "name": "dimension",
                           "label": "特征维数",
                           "type": "int",
                           "required": True,
                       } for i in range(4)
                   ] +
                   [
                       {
                           "model_id": 2,
                           "name": "n_classes",
                           "label": "目标类别数量",
                           "type": "int",
                           "required": True,
                       },
                       {
                           "model_id": 4,
                           "name": "n_classes",
                           "label": "目标类别数量",
                           "type": "int",
                           "required": True,
                       }
                   ]
                   )
    op.bulk_insert(methodkwargs_tbl,
                   [
                       {
                           "model_id": i + 3,
                           "name": "hidden_units",
                           "label": "隐含层各层数量",
                           "type": "list",
                           "required": True,
                       } for i in range(2)
                   ]
                   )
    op.bulk_insert(methodkwargs_tbl, [
        {"model_id": 5,
         "name": "image",
         "label": "图片",
         "description": "需要进行分类的图片",
         "required": True,
         "type": "image"
         }
    ])

    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mlmethods_tbl')
    op.drop_table('methodkwargs_tbl')
    ### end Alembic commands ###
