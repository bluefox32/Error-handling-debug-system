"""
setup.py - Comprehensive Debug Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="comprehensive-debug-framework",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Comprehensive Debug Framework for Null Reference Hang, Memory Exhaustion, and Retry Loop Prevention",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/comprehensive-debug-framework",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
    },
    keywords="debug framework null reference memory exhaustion retry circuit-breaker",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/comprehensive-debug-framework/issues",
        "Source": "https://github.com/yourusername/comprehensive-debug-framework",
        "Documentation": "https://github.com/yourusername/comprehensive-debug-framework/blob/main/README.md",
    },
)
