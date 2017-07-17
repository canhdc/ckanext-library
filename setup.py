# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
version = '0.1.0'

setup(
    name='ckanext-libraries',
    version=version,
    description="Libraries and Archives Canada CKAN extension",
    long_description="""
    """,
    classifiers=[],
    keywords='',
    author='Government of Canada',
    author_email='',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    [ckan.plugins]
    canada_libraries=ckanext.libraries.plugins:LibrariesPlugin
    """,
)
