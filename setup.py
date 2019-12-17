from setuptools import setup
 
setup(name='OrangeFieldEditor',
      version='0.1.2',
      description='100% Orange Field Editor',
      url='https://github.com/zirconium-n/OFE',
      author='lhw & sgk',
      license='MIT',
      packages=['OFE'],
      install_requires=[
          'PyQt5',
          'pillow'
      ],
      scripts=['bin/OFE.bat'],
      zip_safe=False,
      include_package_data=True)