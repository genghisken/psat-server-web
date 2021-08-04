from setuptools import setup, find_packages
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))

def readme():
    with open(moduleDirectory + '/README.md') as f:
        return f.read()

setup(
    name="psat-server-web",
    description='Pan-STARRS and ATLAS web interface.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    version="0.0.17",
    author='genghisken',
    author_email='ken.w.smith@gmail.com',
    license='MIT',
    url='https://github.com/genghisken/psat-server-web',
    packages=find_packages(),
    classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Utilities',
    ],
    install_requires=[
          'numpy',
          'mysqlclient',
          'django',
          'django_tables2',
          'pyyaml',
          'docopt',
          'python-dotenv',
          'gkhtm',
          'gkutils',
      ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False
)
