from setuptools import find_packages, setup
setup(
    name='motorisedcameratracking',
    packages=find_packages(),
    version='0.3.0',
    description='Used to create a tracking tripod head',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='William Dove',
    author_email='williamtdove@gmail.com',
    url='https://github.com/wDove1/Camera-Tracking-Python',
    license='Apache 2.0',
    install_requires=['cvlib','opencv-python','motorcontrollib'],
    classifiers=["Programming language :: Python :: 3",
                 "License :: OSI Approved :: Apache License 2.0",
                 "Operating System :: OS Independent"],
    python_requires='>=3.7'
)
