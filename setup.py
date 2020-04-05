import io
import re
from setuptools import setup, find_packages


with io.open("README.md", "r", encoding="utf8") as f:
    readme = f.read()


with io.open("liqueur/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name='liqueur',
    version=version,
    keywords='Taiwan trading framework',
    description='A lightweight python framework for Capital API',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url='https://github.com/kiraxie/liqueur',
    license='MIT',
    author='Kira Hsieh',
    author_email="kiraxie11287@gmail.com",
    zip_safe=False,
    install_requires=[
        'comtypes >= 1.1.7; platform_system=="Windows"',
        'pywin32 >= 227; platform_system=="Windows"'
    ],
    include_package_data=True,
    platforms=[
        'win_amd64'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows :: Windows 10'
    ],
    python_requires='>=3.7'
)
