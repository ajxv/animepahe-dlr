from setuptools import setup

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'animepahe-dlr',
    version = '0.1.1',
    description = "A python script to automate downloads from animepahe",
    license = "MIT",
    py_modules = [
        'ap_dlr',
        'custom_modules.gecko_installer', 
        'custom_modules.inbuilt_dlr', 
        'custom_modules.initiate_driver',
    ],
    package_dir = {'':'animepahe_dlr'},
    entry_points ={
            'console_scripts': [
                'animepahe-dlr = ap_dlr:main'
            ]
    },
    include_package_data=True,
    
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