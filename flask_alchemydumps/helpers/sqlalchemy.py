# coding: utf-8

from flask import current_app


def get_sa_mapped_classes(sqlalachemy_db=False):
    """
    :param sqlalachemy_db: (optional) SQLAlchemy database (if not passed, it is loaded from AlchemyDumps() instance)
    :return: list of SQLALchemy mapped classes
    """
    if not sqlalachemy_db:
        sqlalachemy_db = current_app.extensions['alchemydumps'].db
    do_not_backup = []
    sa_models = list()
    for m in sqlalachemy_db.Model.__subclasses__():
        if m not in do_not_backup:
            sa_models.append(m)
    return sa_models
