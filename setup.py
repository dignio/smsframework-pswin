#! /usr/bin/env python

from setuptools import setup

setup(
    # http://pythonhosted.org/setuptools/setuptools.html
    name='smsframework-pswin',
    version='0.0.1-4',
    author='Dignio',

    url='https://github.com/dignio/py-smsframework-pswin',
    license='MIT',
    description="SMS framework: PSWin provider",
    long_description=open('README.rst').read(),
    keywords=['sms', 'message', 'notification', 'receive', 'send', 'pswin'],

    packages=['smsframework_pswin'],
    scripts=[],

    install_requires=[
        'smsframework >= 0.0.1',
        'requests == 2.4.3'
    ],
    extras_require={
        'receiver': [  # sms receiving
            'flask >= 0.10',
        ],
        '_dev': ['wheel', 'nose', 'flask'],
    },
    test_suite='nose.collector',
    include_package_data=True,

    platforms='any',
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
)
