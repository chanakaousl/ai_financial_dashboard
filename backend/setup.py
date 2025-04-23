from setuptools import setup, find_packages

setup(
    name="jkh-financial-dashboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask",
        "pandas",
        "scikit-learn",
        "camelot-py",
        "pdfminer.six",
        "numpy",
        "SQLAlchemy",
        "python-dotenv",
        "pytest",
        "opencv-python",
        "Pillow",
        "ghostscript",
    ],
    python_requires=">=3.10",
) 