from setuptools import setup, find_packages
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/psat_server_web/__version__.py").read())

def readme():
    with open(moduleDirectory + '/README.md') as f:
        return f.read()

setup(
    name="psat-server-web",
    description='Pan-STARRS and ATLAS web interface.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    version=__version__,
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
          'django<4.2',
          'django_tables2',
          'djangorestframework',
          'pyyaml',
          'docopt',
          'python-dotenv',
          'gkhtm',
          'gkutils>=0.2.27',
          'requests',
          'lasair',
          'dustmaps',
      ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False
)

# 2023-10-24 Added 'djangorestframework'.

