from setuptools import setup

setup(
    name="awaredb",
    packages=["awaredb"],
    version="0.1.1",
    license="MIT",
    description="AwareDB: data modularity, simplified. Python API.",
    author="Nelson Monteiro",
    author_email="nelson@aware-db.com",
    url="https://github.com/nelsonmonteiro/awaredb-python-api",
    download_url="https://github.com/nelsonmonteiro/awaredb-python-api/archive/v_0_1_1.tar.gz",
    keywords=["AwareDB", "modularity"],
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Front-Ends",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
