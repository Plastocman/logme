import os
from setuptools import setup, find_packages

WHERE = os.path.abspath(os.path.dirname(__file__))


setup(name = 'logme',
        version = '0.0',
        description = 'exhaustive exceptions logger',
        packages = find_packages(WHERE),
        zip_safe=False,
        entry_points = {
            'console_scripts' : 'cmd = cmd:do'
            },
        platforms='any',
        )

# TODO : add console entry point...