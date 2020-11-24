from setuptools import find_packages, setup

setup(
    name='weather_girl',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask','gzip','json','pandas',
        'datetime',
        'sys','os', 'io','urllib','python3'
    ],
)