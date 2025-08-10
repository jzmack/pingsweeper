from setuptools import setup, find_packages

setup(
    name="pingsweeper",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[""],
    entry_points={
        'console_scripts': [
            'pingsweeper=main.ps:main',
        ],
    },
    author="Jacob Mackin",
    author_email="mackinjz412@gmail.com",
    description="A tool for pinging subnets.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/jzmack/pingsweep",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.7',
)
