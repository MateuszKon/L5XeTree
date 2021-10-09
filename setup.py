from distutils.core import setup
import py2exe


setup(console=['test1.py'],
      options={
            "py2exe": {
                  "includes": ["lxml.etree", 'lxml._elementpath', 'gzip']
                   }
      }, requires=['PySide6']
      )

#python setup.py py2exe
