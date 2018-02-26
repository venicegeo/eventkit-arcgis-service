import os
from distutils.core import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="eventkit_arcgis_service",
    version="0.1",
    author="Joseph Svrcek",
    author_email="joseph.svrcek@rgi-corp.com",
    description="A service to run on an ArcGIS Engine/Server host to handle requests from EventKit",
    long_description=(read('readme.md')),
    classifiers=[
        'Development Status :: 1 - Planning',
    ],
    license="BSD",
    keywords="django eventkit arcgis",
    packages=['eventkit_arcgis_service'],
    install_requires=[
        'Django>=1.11.1,<2',
        'pytz>=2018.1,<2019.1',
        'waitress>=1.1.0,<1.2'
    ]
)
