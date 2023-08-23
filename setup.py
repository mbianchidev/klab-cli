from distutils.core import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='kubelab-cli',
    packages=['kubelab-cli'],
    version='0.1.6',
    license='MIT',
    description='kubelab-cli Kubernetes made easy - handle clusters and product with simple commands!',
    author='KubeLab team',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email='dev@kubelab.cloud',
    url='https://github.com/KubeLab-cloud/kubelab-cli',
    download_url='https://github.com/KubeLab-cloud/kubelab-cli/archive/kubelab-cli-0.1.tar.gz',
    keywords=['kubernetes', 'cli', 'iac', 'k9s', 'kubectl'],
    install_requires=[
        'boto3',
        'botocore',
        'click',
        'jmespath',
        'MarkupSafe',
        'python-dateuti',
        'PyYA',
        's3transfer',
        'six',
        'urllib3',
        'build',
        'wheel',
        'setuptools',
        'flake8',
        'mccabe',
        'pycodestyle',
        'pyflakes',
        'kubernetes',
        'requests',
        'pytest',
    ],
    # classifiers=[
    #     #   3 - Alpha
    #     #   4 - Beta
    #     #   5 - Production/Stable
    #     'Development Status :: 3 - Alpha',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: MIT License',
    #     'Programming Language :: Python :: 3.10',
    # ],
)
