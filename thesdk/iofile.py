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
from verilog.connector import intend

class iofile(IO):
    """
    Class to provide file IO for external simulatiors. 
    
    When created, adds an iofile object to the parents iofile_bundle attribute.
    Accessible as iofile_bundle.Members['name'].

    Example
    -------
    Initiated in parent as: 
        _=iofile(self,name='foobar')
    
    Parameters
    -----------
    parent : object 
        The parent object initializing the iofile instance. Default None
    
    **kwargs :  
            name : str  
                Name of the file. Appended with 
                random string during the simulation.
            param : str,  -g g_file
                The string defining the testbench parameter to be be 
                passed to the simulator at command line.
    """
    def __init__(self,parent=None,**kwargs):
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
    @property  # in | out
    def dir(self):
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
        if hasattr(self,'_iotype'):
            return self._iotype
        else:
            self._iotype='sample'
        return self._iotype

    @property
    def datatype(self):  # complex | int | scomplex | sint
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
        if hasattr(self,'_ionames'):
            return self._ionames
        else:
            self._ionames=[]
        return self._ionames

    @ionames.setter
    def ionames(self,value):
        self._ionames=value


    @abstractproperty
    def file(self):
        self._file=self.parent.vlogsimpath +'/' + self.name \
                + '_' + self.rndpart +'.txt'
        return self._file



    # Relocate i.e. change parent. 
    # probably this could be automated
    # by using properties
    def adopt(self,parent=None,**kwargs):
        if parent==None:
            self.print_log(type='F', msg='Parent must be given for relocation')
        self.parent=parent
        if hasattr(self.parent,'iofile_bundle'):
            self.parent.iofile_bundle.new(name=self.name,val=self)

    # File writing
    def write(self,**kwargs):
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
            if datatype is [ 'int', 'sint', 'complex', 'scomplex' ]:
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

            df=pd.DataFrame(parsed,dtype=datatype)
            if self.hasheader:
                df.to_csv(path_or_buf=self.file,sep="\t",index=False,header=header_line)
            else:
                df.to_csv(path_or_buf=self.file,sep="\t",index=False,header=False)
        # This is to compensate filesystem delays
        time.sleep(10)
        
    # Reading
    def read(self,**kwargs):
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
        if self.preserve:
            self.print_log(type="I", msg="Preserve_value is %s" %(self.preserve))
            self.print_log(type="I", msg="Preserving file %s" %(self.file))
        else:
            try:
                os.remove(self.file)
            except:
                pass

