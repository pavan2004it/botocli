from setuptools import setup

setup(
    name='botocli',
    version='1.2',
    author="Pavan",
    author_email="pavan_2004it@icloud.com",
    description="botocli is a tool to manage AWS Services",
    license="GPLv3+",
    packages=['awssnapelb'],
    url="https://github.com/pavan2004it/snapshotanalyzer",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        botocli=awssnapelb:cli
    ''',
)
