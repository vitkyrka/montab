from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='montab',
    description='Like Alt-Tab, but for monitors',
    long_description=readme(),
    license='MIT',
    url='https://github.com/rabinv/montab',
    author='Rabin Vincent',
    author_email='rabin@rab.in',
    version='0.1.0',
    entry_points={
        'console_scripts': 'montab = montab.montab:main'
    },
    packages=['montab'],
    classifiers=[
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Desktop Environment :: Window Managers',
    ],
)
