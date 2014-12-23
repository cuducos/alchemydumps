from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='Flask-AlchemyDumps',
      version='0.0.4',
      description='SQLAlchemy backup/dump tool for Flask',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Framework :: Flask',
          'Programming Language :: Python :: 2.7',
          'Intended Audience :: Developers',
          'Topic :: Database',
          'Topic :: System :: Archiving :: Backup',
          'Topic :: Utilities'
      ],
      keywords='backup, sqlalchemy, flask, restore, dumps, serialization',
      url='https://github.com/cuducos/alchemydumps',
      author='Eduardo Cuducos',
      author_email='cuducos@gmail.com',
      license='MIT',
      packages=find_packages(exclude=["tests",]),
      install_requires=[
          'Flask',
          'Flask-Script',
          'Flask-SQLAlchemy',
          'SQLAlchemy',
          'Unipath'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
