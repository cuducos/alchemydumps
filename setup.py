# coding: utf-8

from setuptools import setup, find_packages

url = 'https://github.com/cuducos/alchemydumps'
long_description = 'Check `Flask-AlchemyDumps at GitHub <{}>`_.'.format(url)

setup(name='Flask-AlchemyDumps',
      version='0.0.10',
      description='SQLAlchemy backup/dump tool for Flask',
      long_description=long_description,
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: MIT License',
                   'Framework :: Flask',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Intended Audience :: Developers',
                   'Topic :: Database',
                   'Topic :: System :: Archiving :: Backup',
                   'Topic :: Utilities'],
      keywords='backup, sqlalchemy, flask, restore, dumps, serialization, ftp',
      url=url,
      author='Eduardo Cuducos',
      author_email='cuducos@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      install_requires=['Flask',
                        'Flask-Script',
                        'Flask-SQLAlchemy',
                        'SQLAlchemy',
                        'Unipath'],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
