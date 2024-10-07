from setuptools import setup, find_packages

setup(
    name='JoDBS_Tools',
    version='0.2.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pymongo',
        'nextcord',
        'python-dotenv',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            # Add command line scripts here if needed
        ],
    },
    author='JoDBS',
    author_email='',
    description='A utility library by JoDBS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/JoDBS/JoDBS_Tools',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)