"""Setup configuration for MyMT5 package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from __version__.py
version = {}
with open("mymt5/__version__.py") as f:
    exec(f.read(), version)

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = version['__description__']

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]
else:
    requirements = [
        'MetaTrader5>=5.0.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'python-dateutil>=2.8.0',
    ]

# Development requirements
dev_requirements = [
    'pytest>=7.0.0',
    'pytest-cov>=3.0.0',
    'black>=22.0.0',
    'flake8>=4.0.0',
    'mypy>=0.950',
    'sphinx>=5.0.0',
    'sphinx-rtd-theme>=1.0.0',
    'myst-parser>=0.18.0',
]

setup(
    # Package metadata
    name=version['__title__'],
    version=version['__version__'],
    description=version['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    # Author information
    author=version['__author__'],
    author_email=version['__author_email__'],
    
    # URLs
    url=version['__url__'],
    project_urls={
        'Documentation': 'https://github.com/yourusername/mymt5/docs',
        'Source': 'https://github.com/yourusername/mymt5',
        'Bug Reports': 'https://github.com/yourusername/mymt5/issues',
        'Changelog': 'https://github.com/yourusername/mymt5/blob/main/CHANGELOG.md',
    },
    
    # License
    license=version['__license__'],
    
    # Package discovery
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'docs']),
    include_package_data=True,
    
    # Requirements
    python_requires='>=3.8',
    install_requires=requirements,
    
    # Optional dependencies
    extras_require={
        'dev': dev_requirements,
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=0.18.0',
            'sphinx-autobuild>=2021.3.14',
        ],
        'test': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'pytest-asyncio>=0.18.0',
        ],
    },
    
    # Classifiers
    classifiers=[
        # Development Status
        'Development Status :: 5 - Production/Stable',
        
        # Intended Audience
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        
        # Topic
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        
        # License
        'License :: OSI Approved :: MIT License',
        
        # Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        
        # Operating Systems
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        
        # Additional classifiers
        'Natural Language :: English',
        'Typing :: Typed',
    ],
    
    # Keywords
    keywords=[
        'metatrader5',
        'mt5',
        'trading',
        'forex',
        'algorithmic-trading',
        'automated-trading',
        'trading-bot',
        'financial-markets',
        'technical-analysis',
        'risk-management',
    ],
    
    # Entry points (if any command-line tools)
    entry_points={
        'console_scripts': [
            # Add command-line tools here if needed
            # 'mymt5-cli=mymt5.cli:main',
        ],
    },
    
    # Package data
    package_data={
        'mymt5': [
            'py.typed',  # For type checking
        ],
    },
    
    # Zip safe
    zip_safe=False,
)
