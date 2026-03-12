from setuptools import setup, find_packages

setup(
    name="grimoire-wordlist",
    version="2.2.2",
    packages=find_packages(),
    include_package_data=True,
    package_data={"grimoire": ["data/*.csv", "data/locales/*.txt"]},
    entry_points={"console_scripts": ["grimoire=grimoire.cli:main"]},
)
