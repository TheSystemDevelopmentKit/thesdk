"""
Thesdk
======

Superclass class of TheSyDeKick - universal System Development Kit  
Provides commmon methods and utility classes for other classes in TheSyDeKic

Created by Marko Kosunen, mrko.kosunen@aalto.fi, 2017.

Documentation instructions
--------------------------
Current docstring documentation style is Numpy
https://numpydoc.readthedocs.io/en/latest/format.html

This text here is to remind you that documentation is imortant.
However, you may find it out the even the documentation of this
entity may be outdated and incomplete. Regardless of that, every day
and in every way we are getting better and better :).


Class Attributes
================

Following class attribute are set when this class imported

Attributes
__________


    HOME : strl
        Directory ../../../ counting from location __init__.py file of thesdkclass. Used as a reference point for other locations
    
    CONFIGFILE : str
        HOME/TheSDK.config.
    
    MODULEPATHS : str
        List of directories under HOME/Entities  that contain __init__.py file. Appended to sys.path to locate TheSyDeKick system modules

    logfile : str
       Default logfile:  /tmp/TheSDK_randomstr_uname_YYYYMMDDHHMM.log
       Override with initlog if you want something else

    global_parameters : list(str)
       List of global parameters to be read to GLOBALS dictionary from CONFIGFILE

    GLOBALS : Dict
       Dictionary of global parameters, keys defined by global_parameters, values defined in CONFIGFILE


"""
import sys
import os
import glob
import getpass
import time
import tempfile
import re
import abc
from abc import *
from functools import reduce

#Set 'must have methods' with abstractmethod
#@abstractmethod
#Using this decorator requires that the class’s metaclass is ABCMeta or is 
#derived from it. A class that has a metaclass derived from ABCMeta cannot 
#be instantiated unless all of its abstract methods and properties are overridden.

class thesdk(metaclass=abc.ABCMeta):
    ''' Defines the common attributes  and locations 
    for ThsSydeKick environment

    '''

    #Solve for the THESDKHOME
    #HOME=os.getcwd()
    HOME=os.path.realpath(__file__)
    for i in range(4):
        HOME=os.path.dirname(HOME)
    print("Home of TheSDK is %s" %(HOME))
    CONFIGFILE=HOME+'/TheSDK.config'
    print("Config file  of TheSDK is %s" %(CONFIGFILE))

    #This becomes redundant after the GLOBALS dictionary is created
    global_parameters=['LSFSUBMISSION','LSFINTERACTIVE','ELDOLIBFILE','SPECTRELIBFILE']

    #Appending all TheSDK python modules to system path (only ones, with set subtraction)
    #This could be done as oneliner with lambda,filter, map and recude, but due to name scope 
    #definitions, this is simpler method in class definition
    MODULEPATHS=[os.path.split(os.path.split(y)[0])[0] for y in [ filename for filename in 
        glob.iglob( HOME+'/Entities/**/__init__.py',recursive=True)]] 
    for i in list(set(MODULEPATHS)-set(sys.path)):
        print("Adding %s to system path" %(i))
        sys.path.append(i)
    
    logfile=("/tmp/TheSDK_" + os.path.basename(tempfile.mkstemp()[1])+"_"+getpass.getuser()
        +"_"+time.strftime("%Y%m%d%H%M")+".log")
    if os.path.isfile(logfile):
        os.remove(logfile)
    print("Setting default logfile %s" %(logfile))
    #Do not create the logfile here
    #----logfile stuff ends here

    # Parse the glopal parameters from a TheSDK.config to a dict
    # Delete parameter list as not needed any more
    GLOBALS={}
    for name in global_parameters:
        with  open(CONFIGFILE,'r') as fid:
            global match
            match='('+name+'=)(.*)'
            func_list=(
                lambda s: re.sub(match,r'\2',s),
                lambda s: re.sub(r'"','',s),
                lambda s: re.sub(r'\n','',s)
            )
            for line in fid:
                if re.match(match,line):
                    GLOBALS[name]=reduce(lambda s, func: func(s), func_list, line)
                    print("GLOBALS[%s]='%s'"%(name,GLOBALS[name]))
        fid.close()
    del match
    del global_parameters
    del name
    #----Global parameter stuff ends here

    @classmethod
    def initlog(cls,*arg):
        '''
        Initializes logging. logfile passed as a parameter

        '''
        if len(arg) > 0:
            __class__.logfile=arg[0]

        if os.path.isfile(__class__.logfile):
            os.remove(__class__.logfile)
        typestr="INFO at "
        msg="Default logfile override. Inited logging in %s" %(__class__.logfile)
        fid= open(__class__.logfile, 'a')
        print("%s %s  %s: %s" %(time.strftime("%H:%M:%S"),typestr, __class__.__name__ , msg))
        fid.write("%s %s %s: %s\n" %(time.strftime("%H:%M:%S"),typestr, __class__.__name__ , msg))
        fid.close()

    #Common properties
    @property
    def DEBUG(self):
        if not hasattr(self,'_DEBUG'):
            return 'False'
        else:
            return self._DEBUG
    @DEBUG.setter
    def DEBUG(self,value):
        self._DEBUG=value

    @property
    @abstractmethod
    def _classfile(self):
        ''' Abstract property of thesdk class. Defines the location of the classfile 

            Define in every child class of thesdk as :: 

                def _classfile(self):
                    return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__


        '''
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__
    
    @property
    def entitypath(self):
        ''' Path to entity. Extracted from the location of __init__.py file.

        '''
        if not hasattr(self, '_entitypath'):
            self._entitypath= os.path.dirname(os.path.dirname(self._classfile))
        return self._entitypath
    #No setter, no deleter.


    @property
    def model(self):
        ''' Simulation model to be used 

        'py' |  'sv' |  'vhdl' |  'eldo' |  'spectre'   

        '''
        if not hasattr(self,'_model'):
            self.print_log(type='F', msg='You MUST set the simulation model.')
        else:
            return self._model
    @model.setter
    def model(self,val):
        if val in [ 'py', 'sv', 'vhdl', 'eldo', 'spectre' ]:
            self._model=val
        else:
            self.print_log(type='W', msg= 'Simulator model %s not supported.' %(val))
            self._model=val

        return self._model

    @property 
    def simpath(self):
        ''' Simulation directory according to model

            Default: Self.entitypath/Simulations/<simulator>sim
            For verilog and vhdl <simulator> is 'rtl'.

        '''
        if not hasattr(self,'_simpath'):
            if self.model=='py':
                self._simpath=self.entitypath+self.name
            elif (self.model=='sv') or (self.model=='vhdl'):
                self._simpath=self.entitypath+'/Simulations/rtlsim'
            elif (self.model=='eldo'):
                self._simpath=self.entitypath+'/Simulations/' +self.model + 'sim'
        return self._simpath

    @simpath.setter
    def simpath(self,val):
        self._simpath=val
        return self._simpath
    
    #Common method to propagate system parameters
    def copy_propval(self,*arg):
        ''' Method to copy attributes form parent. 
        
        Example ::

           a=some_thesdk_class(self)

        Attributes listed in proplist attribute of 'some_thesdkclass' are copied from
        self to a. Impemented by including following code at the end of __init__ method 
        of every entity ::
        
            if len(arg)>=1:
                parent=arg[0]
                self.copy_propval(parent,self.proplist)
                self.parent =parent;

        '''
           
        if len(arg)>=2:
            self.parent=arg[0]
            self.proplist=arg[1]
            for i in range(1,len(self.proplist)+1):
                if hasattr(self,self.proplist[i-1]):
                    #Its nice to see how things propagate
                    if  hasattr(self.parent,self.proplist[i-1]):
                        msg="Setting %s: %s to %s" %(self, self.proplist[i-1], getattr(self.parent,self.proplist[i-1]))
                        self.print_log(type= 'I', msg=msg)
                        setattr(self,self.proplist[i-1],getattr(self.parent,self.proplist[i-1]))

    #Method for logging
    #This is a method because it uses the logfile property
    def print_log(self,**kwargs):
        ''' Method to print messages to 'logfile'

        Parameters
        ----------
         **kwargs :  
                 type : str  
                    'I' = Information 
                    'D' = Debug. Enabled by setting the Debug-attribute of an instance to true
                    'W' = Warnig
                    'E' = Error
                    'F' = Fatal, quits the execution



                 msg : str
                     The messge to be printed

        '''

        type=kwargs.get('type','I')
        msg=kwargs.get('msg',"Print this to log")
        if not os.path.isfile(thesdk.logfile):
            typestr="INFO at"
            msg="Inited logging in %s" %(thesdk.logfile)
            fid= open(thesdk.logfile, 'a')
            print("%s %s thesdk: %s" %(time.strftime("%H:%M:%S"), typestr , initmsg))
            fid.write("%s %s thesdk: %s\n" %(time.strftime("%H:%M:%S"), typestr, initmsg))
            fid.close()

        if type== 'D':
            if self.DEBUG:
                typestr="DEBUG at"
                print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, 
                    self.__class__.__name__ , msg)) 
                if hasattr(self,"logfile"):
                    fid= open(thesdk.logfile, 'a')
                    fid.write("%s %s %s: %s\n" %(time.strftime("%H:%M:%S"), 
                        typestr, self.__class__.__name__ , msg)) 
                    fid.close()
            return
        elif type== 'I':
           typestr="INFO at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, 
               self.__class__.__name__ , msg)) 
        elif type=='W':
           typestr="WARNING! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), 
               typestr, self.__class__.__name__ , msg)) 
        elif type=='E':
           typestr="ERROR! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, 
               self.__class__.__name__ , msg)) 
        elif type=='O':
           typestr="[OBSOLETE]: at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, 
               self.__class__.__name__ , msg)) 

        elif type=='F':
           typestr="FATAL ERROR! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, 
               self.__class__.__name__ , msg)) 
           print("Quitting due to fatal error in %s" %(self.__class__.__name__))
           if hasattr(self,"logfile"):
               fid= open(thesdk.logfile, 'a')
               fid.write("%s Quitting due to fatal error in %s.\n" 
                       %( time.strftime("%H:%M:%S"), self.__class__.__name__))
               fid.close()
               quit()
        else:
           typestr="ERROR! at"
           msg="Incorrect message type. Choose one of 'D', 'I', 'E' or 'F'."
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, 
               self.__class__.__name__ , msg)) 

        #If logfile set, print also there 
        if hasattr(self,"logfile"):
            fid= open(thesdk.logfile, 'a')
            fid.write("%s %s %s: %s\n" %(time.strftime("%H:%M:%S"), 
                typestr, self.__class__.__name__ , msg)) 
            fid.close()

class IO(thesdk):
    ''' TheSyDeKick IO class. Child of thesdk to utilize logging method.

    The IOs of an entity must be defined as :: 
        self.IOS=Bundle()
        self.IOS.Members['a']=IO() 
        
    and referred to as :: 
        self.IOS.Members['a'].Data

    '''
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,**kwargs): 
        ''' Parameters
            ----------
            **kwargs :  

               Data : numpy_array, None
                   Sets the Data attribute during the initialization

       '''

        self._Data = kwargs.get('Data',None)

    @property
    def Data(self):
        '''Data value of this IO
        
        ''' 
        if hasattr(self,'_Data'):
            return self._Data
        else:
            self._Data=None
        return self._Data

    @Data.setter
    def Data(self,value):
        self._Data=value

    @property
    def data(self):
        if hasattr(self,'_Data'):
            return self._Data
        else:
            self._Data=None

        self.print_log(type='O',msg='IO attribute \'data\' is obsoleted by attribute \'Data\' Will be removed in release 1.4' )
        return self._Data

    @data.setter
    def data(self,value):
        self._Data=value

# Bundle is a Dict of something
# Class is needed to define bundle operations
class Bundle(metaclass=abc.ABCMeta):
    '''Bundle class of named things.
    
    '''
    def __getattr__(self,name):
        '''Access the attribute <name> directly
        Not tested.
        
        Returns
        -------
            type of dict member
                self.Members['name']

        '''
        return self.Members[name]

    def __init__(self): 
        '''Attributes
           ----------

           Members: dict, dict([])

        '''
        self.Members=dict([])

    def new(self,**kwargs):
        '''Parameters
           ----------

           **kwargs:
               name: str, optional
               val: str, optional

        '''
        name=kwargs.get('name','')
        val=kwargs.get('val','')
        self.Members[name]=val

