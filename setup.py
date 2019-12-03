#!/usr/bin/env python
from info import get_version
import sys
from setuptools import setup, find_packages

# avoid networkx ImportError
sys.path.insert(0, 'netdiff')
sys.path.remove('netdiff')


if sys.argv[-1] == 'setup.py':
    print("To install, run 'python setup.py install'\n")


if sys.argv[-1] == 'publish':
    import os
    os.system('find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf')
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload -s dist/*")
    os.system("rm -rf dist build")
    args = {'version': get_version()}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()


def get_install_requires():
    """
    parse requirements.txt, ignore links, exclude comments
    """
    requirements = []
    for line in open('requirements.txt').readlines():
        # skip to next iteration if comment or empty line
        if line.startswith('#') or line == '' or line.startswith('http') or line.startswith('git'):
            continue
        if line.startswith("networkx") and get_version() < 3.5:
            line.replace("<", "=")
        # add line to requirements
        requirements.append(line.replace('\n', ''))
    return requirements


setup(
    name='netdiff',
    version=get_version(),
    description="Python library for parsing network topology data (eg: dynamic "
                "routing protocols, NetJSON, CNML) and detect changes.",
    long_description=open('README.rst').read(),
    author='Federico Capoano (nemesisdesign)',
    author_email='ninux-dev@ml.ninux.org',
    license='MIT',
    url='https://github.com/ninuxorg/netdiff',
    download_url='https://github.com/ninuxorg/netdiff/releases',
    keywords=['networking',
              'mesh-network',
              'netjson',
              'olsr',
              'batman',
              'bmx'],
    platforms=['Platform Indipendent'],
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Networking',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=get_install_requires(),
    test_suite='nose.collector'
)
