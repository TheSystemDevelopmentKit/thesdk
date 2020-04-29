"""
======================
Iofile package 
======================

Provides Common file-io related attributes and methods 
for TheSyDeKinck

This package defines the CSF IO-file format and methods for all supported simulators.
Intention is to keep as much of the file io as general adn common as possible.
The simulator specific file-io functions should be written in simulator specific file-io
packages.

Initially written for Verilog file-io by Marko Kosunen, marko.kosunen@aalto.fi,
Yue Dai, 2018

Generalized for common file-io by Marko Kosunen, marko.kosunen@aalto.fi,
2019.

"""

import os
import sys
from abc import * 
from thesdk import *
import numpy as np
import pandas as pd

class iofile(IO):
     '''
     Class to provide file IO for external simulators. 
     
     When created, adds an iofile object to the parents iofile_bundle attribute.
     Accessible as iofile_bundle.Members['name'].
 
     Example
     -------
     Initiated in parent as: 
         _=iofile(self,name='foobar')
     
     '''
     def __init__(self,parent=None,**kwargs):
         '''
         Parameters
         -----------
         parent : object, None 
             The parent object initializing the iofile instance. Default None
         
         **kwargs :  
                 name : str  
                     Name of the file. Appended with 
                     random string during the simulation.
                 param : str,  -g g_file
                     The string defining the testbench parameter to be be 
                     passed to the simulator at command line.
         '''
         if parent==None:
             self.print_log(type='F', msg="Parent of Verilog input file not given")
         try:  
             super(iofile,self).__init__(**kwargs)
             self.parent=parent
             self.rndpart=os.path.basename(tempfile.mkstemp()[1])
             self.name=kwargs.get('name') 
 
             # IO's are output by default
             # Currently less needed for Python, but used in Verilog
             self._dir=kwargs.get('dir','out')
             self._datatype=kwargs.get('datatype','int')
 
             self._iotype=kwargs.get('iotype','sample') # The file is a data file by default 
                                                   # Option: sample, event. file 
                                                   # Events are presented in time-value combinatios 
                                                   # time in the column 0
             self._ionames=kwargs.get('ionames',[]) #list of signal names associated with this io
             self._ioformat=kwargs.get('ioformat','%d') #by default, the io values are decimal integer numbers
 
             self.hasheader=kwargs.get('hasheader',False) # Headers False by default. 
                                                          # Do not generate things just 
                                                          # to remove them in the next step

             if hasattr(self.parent,'preserve_iofiles'):
                 self.preserve=parent.preserve_iofiles
             else:
                 self.preserve=False
         except:
             self.print_log(type='F', msg="IO-file definition failed")
 
         #TODO: Needs a check to eliminate duplicate entries to iofiles
         if hasattr(self.parent,'iofiles'):
             self.print_log(type='O',msg="Attribute iofiles has been replaced by iofile_bundle")
 
         if hasattr(self.parent,'iofile_bundle'):
             self.parent.iofile_bundle.new(name=self.name,val=self)
 
     # These propertios "extend" IO class, but do not need ot be member of it,
     # Furthermore IO._Data _must_ me bidirectional. Otherwise driver and target 
     # Must be defined separately
     @property 
     def dir(self):
         ''' Direction of the iofile, in | out

         '''
         if hasattr(self,'_dir'):
             return self._dir
         else:
             self._dir=None
         return self._dir
 
     @dir.setter
     def dir(self,value):
         self._dir=value
 
     @property
     def iotype(self):  # sample | event
         ''' Type of the IO: sample | event

             sample
                 IO is synchronized with a sampling clock. Each of the rows represents the data valua at known sample insatnce

             event
                 IO is asynchronous. The first colums of the file should be the time of the event

         '''
         if hasattr(self,'_iotype'):
             return self._iotype
         else:
             self._iotype='sample'
         return self._iotype
 
     @property
     def datatype(self):  #          
         ''' Type of the data. Controls the reading and writing of the data
              'complex' | 'int' | 'scomplex' | 'sint' | object

              int | sint :
                  Valeus of the data are handled as unsigned or signed integers

              complex | scomplex : 
                  It is assumed that each column of the Data represents a complex number with
                  integer real and imaginary parts.  This is typical for RTL simulations.
                  when the data is read or written, the columns are treated as Real Imag pairs. 
                  When writing, columns are split to two, when reading, adjacent colums are merged

              object:
                  Values are read and written as defined by the 'dtype' parameter 
                  of the read method. Default is object. 

         '''
         if hasattr(self,'_datatype'):
             return self._datatype
         else:
             self._datatype=None
         return self._datatype
 
     @datatype.setter
     def datatype(self,value):
         self._datatype=value
 
     @property
     def ionames(self): # list of associated ionames
         ''' Names of the DUT signals represented by the colums of the data. 
             Two elements per colums should be given, if the type is complex or scomplex.

         '''
         if hasattr(self,'_ionames'):
             return self._ionames
         else:
             self._ionames=[]
         return self._ionames
 
     @ionames.setter
     def ionames(self,value):
         self._ionames=value
 
 
     @property
     def file(self):
         ''' Name of the IO file to be read or written.

         '''
         if not hasattr(self,'_file'):
             self._file=self.parent.simpath +'/' + self.name \
                     + '_' + self.rndpart +'.txt'
         return self._file
     @file.setter
     def file(self,val):
         self._file=val
         return self._file
 
 
 
     # Relocate i.e. change parent. 
     # probably this could be automated
     # by using properties
     def adopt(self,parent=None,**kwargs):
         '''Redefine the parent entity of the file. Afrects where the file is written during the simulation

         '''
         if parent==None:
             self.print_log(type='F', msg='Parent must be given for relocation')
         self.parent=parent
         if hasattr(self.parent,'iofile_bundle'):
             self.parent.iofile_bundle.new(name=self.name,val=self)
 
     # File writing
     def write(self,**kwargs):
         '''Method to write the file

         Sets the 'dir' attribute to 'in', because only input files are written.
         
         Parameters
         ----------
         
         **kwargs:
             data: numpy_array, self.Data
             datatype: str, self.Datatype
             iotype: str, self.iotype


         '''
         self.dir='in'  # Only input files are written
         #Parse the rows to split complex numbers
         data=kwargs.get('data',self.Data)
         datatype=kwargs.get('datatype',self.datatype)
         iotype=kwargs.get('iotype',self.iotype)
         header_line = []
         parsed=[]
         # Default is the data file
         if iotype=='sample':
             for i in range(data.shape[1]):
                 if i==0:
                    if np.iscomplex(data[0,i]) or np.iscomplexobj(data[0,i]) :
                        parsed=np.r_['1',np.real(data[:,i]).reshape(-1,1),
                                np.imag(data[:,i].reshape(-1,1))]
                        header_line.append('%s_%s_Real' %(self.name,i))
                        header_line.append('%s_%s_Imag' %(self.name,i))
                    else:
                        parsed=np.r_['1',data[:,i].reshape(-1,1)]
                        header_line.append('%s_%s' %(self.name,i))
                 else:
                    if np.iscomplex(data[0,i]) or np.iscomplexobj(data[0,i]) :
                        parsed=np.r_['1',parsed,np.real(data[:,i]).reshape(-1,1),
                                np.imag(data[:,i].reshape(-1,1))]
                        header_line.append('%s_%s_Real' %(self.name,i))
                        header_line.append('%s_%s_Imag' %(self.name,i))
                    else:
                        parsed=np.r_['1',parsed,data[:,i].reshape(-1,1)]
                        header_line.append('%s_%s' %(self.name,i))
 
             # Numbers are printed as intergers
             # These are verilog related, do not belong here
             if datatype in [ 'int', 'sint', 'complex', 'scomplex' ]:
                 df=pd.DataFrame(parsed,dtype='int')
             else:
                 df=pd.DataFrame(parsed,dtype=datatype)
 
             if self.hasheader:
                 df.to_csv(path_or_buf=self.file,sep="\t",
                         index=False,header=header_line)
             else:
                 df.to_csv(path_or_buf=self.file,sep="\t",
                         index=False,header=False)
         # Control file is a different thing
         elif iotype=='event':
             for i in range(data.shape[1]):
                 if i==0:
                    if np.iscomplex(data[0,i]) or np.iscomplexobj(data[0,i]) :
                        self.print_log(type='F', msg='Timestamp can not be complex.')
                    else:
                        parsed=np.r_['1',data[:,i].reshape(-1,1)]
                        header_line.append('Timestamp')
                 else:
                    if np.iscomplex(data[0,i]) or np.iscomplexobj(data[0,i]) :
                        parsed=np.r_['1',parsed,np.real(data[:,i]).reshape(-1,1),
                                np.imag(data[:,i].reshape(-1,1))]
                        header_line.append('%s_%s_Real' %(self.name,i))
                        header_line.append('%s_%s_Imag' %(self.name,i))
                    else:
                        parsed=np.r_['1',parsed,data[:,i].reshape(-1,1)]
                        header_line.append('%s_%s' %(self.name,i))
 
             if datatype in [ 'int', 'sint', 'complex', 'scomplex' ]:
                 df=pd.DataFrame(parsed,dtype='int')
             else:
                 df=pd.DataFrame(parsed,dtype=datatype)

             if self.hasheader:
                 df.to_csv(path_or_buf=self.file,sep="\t",index=False,header=header_line)
             else:
                 df.to_csv(path_or_buf=self.file,sep="\t",index=False,header=False)
         # This is to compensate filesystem delays
         time.sleep(10)
         
     # Reading
     def read(self,**kwargs):
         ''' Method to read the file

         Parameters
         ----------
         **kwargs:
            datatype: str, self.datatype
                Controls if the data is read in as complex or real
            dtype   : str, 'object'
                The datatype of the actual file. Default is object, 
                i.e data is first read to internal variable as string. 
                This is a help parameter to give more control over reading.

         '''
         fid=open(self.file,'r')
         self.datatype=kwargs.get('datatype',self.datatype)
         dtype=kwargs.get('dtype',object)
         readd = pd.read_csv(fid,dtype=dtype,sep='\t',header=None)
         #read method for complex signal matrix
         if self.datatype is 'complex' or self.datatype is 'scomplex':
             self.print_log(type="I", msg="Reading complex")
             rows=int(readd.values.shape[0])
             cols=int(readd.values.shape[1]/2)
             for i in range(cols):
                 if i==0:
                     self.Data=np.zeros((rows, cols),dtype=complex)
                     self.Data[:,i]=readd.values[:,2*i].astype('int')\
                             +1j*readd.values[:,2*i+1].astype('int')
                 else:
                     self.Data[:,i]=readd.values[:,2*i].astype('int')\
                             +1j*readd.values[:,2*i+1].astype('int')
 
         else:
             self.Data=readd.values
         fid.close()
 
     # Remove the file when no longer needed
     def remove(self):
         '''Remove the file

         '''
         if self.preserve:
             self.print_log(type="I", msg="Preserve_value is %s" %(self.preserve))
             self.print_log(type="I", msg="Preserving file %s" %(self.file))
         else:
             try:
                 os.remove(self.file)
             except:
                 pass
 
 
