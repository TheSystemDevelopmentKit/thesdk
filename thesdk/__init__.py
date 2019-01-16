# THESDK class 
# Provides commmon methods  for other classes in TheSDK
# Created by Marko Kosunen
#
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
    #Define here the common attributes for the system
    
    #Solve for the THESDKHOME
    #HOME=os.getcwd()
    HOME=os.path.realpath(__file__)
    for i in range(4):
        HOME=os.path.dirname(HOME)
    print("Home of TheSDK is %s" %(HOME))
    CONFIGFILE=HOME+'/TheSDK.config'
    print("Config file  of TheSDK is %s" %(CONFIGFILE))

    #This becomes redundant after the GLOBALS dictionary is removed
    global_parameters=['LSFSUBMISSION']

    #Appending all TheSDK python modules to system path (only ones, with set subtraction)
    #This could be done as oneliner with lambda,filter, map and recude, but due to name scope 
    #definitions, this is simpler method in class definition
    MODULEPATHS=[os.path.split(os.path.split(y)[0])[0] for y in [ filename for filename in glob.iglob( HOME+'/Entities/**/__init__.py',recursive=True)]] 
    for i in list(set(MODULEPATHS)-set(sys.path)):
        print("Adding %s to system path" %(i))
        sys.path.append(i)
    
    #Default logfile. Override with initlog if you want something else
    #/tmp/TheSDK_randomstr_uname_YYYYMMDDHHMM.log
    logfile="/tmp/TheSDK_" + os.path.basename(tempfile.mkstemp()[1])+"_"+getpass.getuser()+"_"+time.strftime("%Y%m%d%H%M")+".log"
    if os.path.isfile(logfile):
        os.remove(logfile)
    print("Setting default logfile %s" %(logfile))
    #Do not create the logfile here
    #----logfile stuff ends here

    # Parse the glopal parameters from a TheSDK.config to a dict
    # Delete parameter list as not needed any more
    GLOBALS={}
    with  open(CONFIGFILE,'r') as fid:
        for name in global_parameters:
            global match
            match='('+name+'=)(.*)'
            func_list=(
                lambda s: re.sub(match,r'\2',s),
                lambda s: re.sub(r'"','',s),
                lambda s: re.sub(r'\n','',s)
            )
            GLOBALS[name]=''
            for line in fid:
                if re.match(match,line):
                    GLOBALS[name]=reduce(lambda s, func: func(s), func_list, line)
            print("GLOBALS[%s]='%s'"%(name,GLOBALS[name]))
    del match
    del global_parameters
    #----Global parameter stuff ends here

    #Clas method for setting the logfile
    @classmethod
    def initlog(cls,*arg):
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


    #Common method to propagate system parameters
    def copy_propval(self,*arg):
        if len(arg)>=2:
            self.parent=arg[0]
            self.proplist=arg[1]
            for i in range(1,len(self.proplist)+1):
                if hasattr(self,self.proplist[i-1]):
                    #Its nice to see how things propagate
                    if  hasattr(self.parent,self.proplist[i-1]):
                        msg="Setting %s: %s to %s" %(self, self.proplist[i-1], getattr(self.parent,self.proplist[i-1]))
                        self.print_log({'type': 'I', 'msg':msg})
                        setattr(self,self.proplist[i-1],getattr(self.parent,self.proplist[i-1]))

    #Method for logging
    #This is a method because it uses the logfile property
    def print_log(self,**kwargs):
        type=kwargs.get('type','I')
        msg=kwargs.get('msg',"Print this to log")
        if not os.path.isfile(thesdk.logfile):
            typestr="INFO at "
            msg="Inited logging in %s" %(thesdk.logfile)
            fid= open(thesdk.logfile, 'a')
            print("%s %s thesdk: %s" %(time.strftime("%H:%M:%S"), typestr , msg))
            fid.write("%s %s thesdk: %s\n" %(time.strftime("%H:%M:%S"), typestr, msg))
            fid.close()

        if type== 'D':
            if self.DEBUG:
                typestr="DEBUG at"
                print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
                if hasattr(self,"logfile"):
                    fid= open(thesdk.logfile, 'a')
                    fid.write("%s %s %s: %s\n" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
            return
        elif type== 'I':
           typestr="INFO at "
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
        elif type=='W':
           typestr="WARNING! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
        elif type=='E':
           typestr="ERROR! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
        elif type=='O':
           typestr="[OBSOLETE]: at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 

        elif type=='F':
           typestr="FATAL ERROR! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
           print("Quitting due to fatal error in %s" %(self.__class__.__name__))
           if hasattr(self,"logfile"):
               fid= open(thesdk.logfile, 'a')
               fid.write("%s Quitting due to fatal error in %s.\n" %( time.strftime("%H:%M:%S"), self.__class__.__name__))
               fid.close()
               quit()
        else:
           typestr="ERROR! at"
           msg="Incorrect message type. Choose one of 'D', 'I', 'E' or 'F'."
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 

        #If logfile set, print also there 
        if hasattr(self,"logfile"):
            fid= open(thesdk.logfile, 'a')
            fid.write("%s %s %s: %s\n" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 

#Class definitions that inherently belong to TheSDK
class refptr(thesdk):
    def __init__(self): 
        self.print_log({'type':'O', 'msg':'refptr class is replaced by the IO class.\nSupport will be removed in future releases.\n\nRequired modification: change references from refptr to IO.and from refptr.Value to IO.Data'})
        self.Value = [];

# As per Dec 2018, this is just a renamed refptr class with better
# property definition
class IO(thesdk):
    def __init__(self): 
        self._Data = None;

    @property
    def Data(self):
        if hasattr(self,'_Data'):
            return self._Data
        else:
            self._Data=None
        return self._Data

    @Data.setter
    def Data(self,value):
        self._Data=value


# Bundle is a Dict of something
# Class is needed to define bundle operations
class Bundle(thesdk):
    def __init__(self): 
       self.Members=dict([])

    def new(self,**kwargs):
        name=kwargs.get('name','')
        val=kwargs.get('val','')
        self.Members[name]=val

