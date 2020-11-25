from setuptools import setup, find_packages

import rabbitmq_admin

setup(
    name='rabbitmq-api-admin',
    version=rabbitmq_admin.__version__,
    description='A python interface for the RabbitMQ Admin HTTP API',
    long_description=open('README.rst').read(),
    url='https://github.com/Uma-Tech/rabbitmq-api-admin',
    author='UMA.TECH',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    install_requires=['requests>=2.7.0']
)
