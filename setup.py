from setuptools import find_packages, setup

# "packages" tells Python what package directories (and its .py files) to
# include. "find_packages()" finds these directories automatically.
# "include_package_data" is set to "True" to include other files (like the
# "static" and "templates" directories). Thus, it's expected to have another
# file named "MANIFEST.in" to tell what these files are.
# For more info on the "MANIFEST.in", see
# https://packaging.python.org/en/latest/guides/using-manifest-in/
setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask'
    ],
)