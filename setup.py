from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'animepahe-dlr',
    version = '0.1.16',
    description = "A python script to automate downloads from animepahe",
    url = "https://github.com/ed-archer/animepahe-dlr",
    author = "ed-archer",
    license = "MIT",
    py_modules = [
        'ap_dlr',
        'ap_dlr_modules.gecko_installer', 
        'ap_dlr_modules.inbuilt_dlr', 
        'ap_dlr_modules.initiate_driver',
    ],
    package_dir = {'':'animepahe_dlr'},
    entry_points ={
            'console_scripts': ['animepahe-dlr = ap_dlr:main']
    },

    include_package_data=True,
    package_data={"animepahe_dlr.driver_extensions": ["*.xpi"]},
    packages = ["driver_extensions", "ap_dlr_modules"],
    
    install_requires = [
        'beautifulsoup4 >= 4.9.3',
        'selenium >= 3.141.0',
        'requests >= 2.25.1',
        'clint >= 0.5.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
    ],

    long_description = long_description,
    long_description_content_type = "text/markdown",


)