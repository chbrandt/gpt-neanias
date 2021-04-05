from setuptools import setup

import versioneer

setup(entry_points = {
        'console_scripts': ['npt=npt.cli:main']
      },
      version = versioneer.get_version(),
      cmdclass = versioneer.get_cmdclass()
)
