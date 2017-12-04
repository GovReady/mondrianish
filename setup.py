from setuptools import setup, find_packages

# For Project Maintainers
# To publish a universal wheel to pypi:
# pip3 install twine
# rm -rf dist
# python3 setup.py bdist_wheel --universal
# twine upload dist/*
# git tag v1.0.XXX
# git push --tags

setup(name='mondrianish',
      version='0.5.2',
      description='Generate Piet Mondrian-style images.',
      url='https://github.com/GovReady/mondrianish',
      author=u'GovReady PBC',
      author_email=u'jt@occams.info',
      license='CC0 1.0 Universal',
      packages=find_packages(),
      install_requires=[
          'pillow',
          'colour',
      ],
      entry_points = {
        'console_scripts': ['mondrianish=mondrianish:main'],
      },
      zip_safe=False)
