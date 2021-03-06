## Run this as: python3 setup_sched_py3.py install --home=./

from distutils.core import setup, Extension

setup(name="Py_sched", 
      version='0.00', 
      ext_modules=[Extension('Py_sched',['C/Py_Sched.c', 'C/orbit_wrappers.c', 'C/cache.c', 'C/memory.c', 
                    'C/misc_at_utilities.c', 'C/attitude_wrappers.c','C/solar_system_wrappers.c'],
                   include_dirs=['/Users/axsh/include'],
                   library_dirs=['/Users/axsh/ChrisToyProject/pytako/atFunctions/3.3/'],  #,'/home/baluta/lib/'],
                   libraries=['atFunctions', 'cfitsio']
      )]
)


