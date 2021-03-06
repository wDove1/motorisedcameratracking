from setuptools import find_packages, setup, Extension
from Cython import *
from Cython.Build import *


setup(
    #extensions = [Extension("Imaging", ["Imaging.pyx"])],
    #cmdclass={'build_ext': Cython.Build.new_build_ext},
    ext_modules = cythonize("motorisedcameratracking/Imaging.py",annotate=True ),
    name='motorisedcameratracking',
    packages=find_packages(include=['motorisedcameratracking','motorisedcameratracking.*']),
    package_dir={'motorisedcameratracking':'motorisedcameratracking'},
    package_data={'motorisedcameratracking':['data.*']},
    version='0.5.0.dev47',
    description='Used to create a tracking tripod head',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='William Dove',
    author_email='williamtdove@gmail.com',
    url='https://github.com/wDove1/motorisedcameratracking',
    license='Apache 2.0',
    install_requires=['cvlib','opencv-python','motorcontrollib'],
    classifiers=["Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent"],
    python_requires='>=3.7,<3.9'
)
