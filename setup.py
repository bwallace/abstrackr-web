try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='abstrackr',
    version='0.2.6',
    description='Web-based Citation Screening Tool',
    author='Byron Wallace',
    author_email='byron_wallace@brown.edu',
    url='https://research.brown.edu/myresearch/Byron_Wallace',
    install_requires=[
        "Pylons==1.0",
        "SQLAlchemy>=0.5",
        "TurboMail>=3.0.3,<=3.0.99",
        "repoze.what-quickstart>=1.0.8,<=1.0.99",
        "repoze.what_pylons>=1.0,<=1.0.99",
        "MySQL-python>=1.2.3,<=1.2.99",
        "elementtree>=1.2.7,<=1.2.99",
        "WebTest>=1.2.3,<=1.2.99",
        "WebOb>=1.0.7,<=1.0.99",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'abstrackr': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'abstrackr': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = abstrackr.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
