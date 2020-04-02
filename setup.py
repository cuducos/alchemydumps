# coding: utf-8

from setuptools import find_packages, setup


URL = 'https://github.com/cuducos/alchemydumps'
LONG_DESCRIPTION = 'Check `Flask-AlchemyDumps at GitHub <{}>`_.'.format(URL)

setup(
    name='Flask-AlchemyDumps',
    version='0.0.10',
    description='SQLAlchemy backup/dump tool for Flask',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Framework :: Flask',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: Utilities'
    ],
    keywords='backup, sqlalchemy, flask, restore, dumps, serialization, ftp',
    url=URL,
    author='Eduardo Cuducos',
    author_email='cuducos@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'Flask-SQLAlchemy',
        'Flask-Script',
        'Flask==1.0.3',
        'SQLAlchemy',
        'Unipath',
        'python-decouple',
    ],
    include_package_data=True,
    zip_safe=False
)
