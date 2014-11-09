import sys
from setuptools import setup, find_packages
from netdiff import get_version


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': get_version()}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()


setup(
    name='netdiff',
    version=get_version(),
    description="Calculates a diff of a network topology",
    long_description=open('README.rst').read(),
    author='Federico Capoano (nemesisdesign)',
    author_email='ninux-dev@ml.ninux.org',
    license='MIT',
    url='https://github.com/ninuxorg/netdiff',
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    install_requires=[
        'networkx',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Networking',
    ],
    test_suite='nose.collector'
)
