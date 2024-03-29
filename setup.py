1# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

name = 'nva.psyquizz'
version = '0.1'
readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()


install_requires = [
    'BeautifulSoup',
    'backports.tempfile',
    'cromlech.sessions.jwt',
    'cromlech.sqlalchemy',
    'dolmen.breadcrumbs',
    'dolmen.clockwork',
    'dolmen.message',
    'html2text',
    'js.jqueryui',
    'nva.password[uvclight]',
    'openpyxl',
    'psycopg2',
    'psycopg2-binary',
    'nva.password',
    'pyPdf',
    'qrcode',
    'reportlab',
    'routes',
    'setuptools',
    'shortid',
    'svglib',
    'ul.auth',
    'ul.sql',
    'uvc.composedview',
    'uvc.protectionwidgets',
    'uvc.validation',
    'uvc.validation',
    'uvclight',
    'uvclight[auth]',
    'uvclight[sql]',
    'xlsxwriter',
    'zope.cachedescriptors',
    'zope.i18n[compile]',
    ]

tests_require = [
    'zope.testbrowser >= 5.2',
    'z3c.etestbrowser',
    ]

setup(name=name,
      version=version,
      description=(""),
      long_description=readme + '\n\n' + history,
      keywords='',
      author='',
      author_email='',
      url='',
      license='Proprietary',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['nva'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      install_requires=install_requires,
      extras_require={'test': tests_require},
      classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_app_factory]
      file_session = nva.psyquizz.session:file_session_wrapper

      [paste.app_factory]
      app = nva.psyquizz.wsgi:routing

      [fanstatic.libraries]
      nva.psyquizz=nva.psyquizz:library
      """,
      )
