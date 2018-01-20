from setuptools import setup

setup(
    name='speeddb',
    packages=['speeddb'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'flask_wtf',
        'flask-user',
        'pyembed'
    ],
)
