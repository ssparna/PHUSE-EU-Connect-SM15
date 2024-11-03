from setuptools import setup, find_packages

VERSION = "1.0.0"
DESCRIPTION = "Export eCRF annotations to Excel"
LONG_DESCRIPTION = "Automates migrating between data levels (in this case CRF and STDM spec)"

setup(
    name="annotation_exporter",
    version=VERSION,
    author="Salomo Sparna",
    author_email="SalomoSparna@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["openpyxl", "PyPDF2", "FreeSimpleGUI"],
    keywords=["python", "CRF", "CDISC"],
    classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ],
        license="MIT",
        python_requires=">=3.11",
)