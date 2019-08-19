from setuptools import setup, find_packages

setup(
  name='scheduler',
  version='0.0.1',
  description='Converting a set of job constraints into a schedule',
  author='armandli',
  author_email='armand.li@hotmail.com',
  packages=find_packages(),
  package_data={},
  data_files=[],
  install_requires=['ortools', 'py3-ortools'],
  entry_points={},
  scripts=[],
)
