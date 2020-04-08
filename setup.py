import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='fireservice', 
    version='0.0.2',
    author='Kaustubh Pratap Chand',
    author_email='contact@kausalitylabs.com',
    description='FireService is a simple library to create Python Services',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kpchand/fireservice',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)