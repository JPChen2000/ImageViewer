from setuptools import setup, find_packages

setup(
    name="ImageViewer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'imageview=imgv.imageview:main',  # "my_command" 是命令名，"my_tool.my_script:main" 是执行入口
        ],
    },
    author="JPChen",
    author_email="1757870133@qq.com",
    description="A simple command line tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
