from setuptools import setup, find_packages
import sys, os

def read(*names):
    values = dict()
    for name in names:
        filename = name+'.md'
        if os.path.isfile(filename):
            value = open(filename).read()
        else:
            value = ''
        values[name] = value
    return values

long_description="""
%(README)s

""" % read('README')

version = '0.1'

setup(name='swgallery',
      version=version,
      description="A gallery export tool for shotwell",
      long_description=long_description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='shotwell',
      author='Guyzmo',
      author_email='guyzmo@leloop.org',
      url='',
      license='AGPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      #package_data={'negar': ['data/*.dat']},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'docopt',
          'PIL'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      swgallery = swgallery.swgallery:run
      """,
      )
