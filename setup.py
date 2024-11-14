from setuptools import setup, find_packages

setup(
    name='python-xml-json-explorecourses',
    version='0.1.0',
    author='Your Name',
    author_email='you@example.com',
    description='A package to transform explorecourses from XML to JSON',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/agsdot/python_xml_json_explorecourses',  # Update with your repo link
    packages=find_packages(),
    install_requires=[
        #'itertools',  # This is a built-in module, no need to include it
        'pandas',
        'pendulum',
        'requests',
        'xmltodict',
        'furl'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)
