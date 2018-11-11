# THESDK class 
# Provides commmon methods  for other classes in TheSDK
# Created by Marko Kosunen
#
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 15.09.2018 18:02
##############################################################################
import sys
import os
import getpass
import time
import tempfile
import abc
from abc import *

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
    GLOBAL_PARAMETERS=['LSFSUBMISSION']

    #Appending all TheSDK python modules to system path (only ones, with set subtraction)
    #This could be done as oneliner with lambda,filter, map and recude, but due to name scope 
    #definitions, this is simpler method in class definition
    ENTITIES=[(x[1]) for x in os.walk( HOME + "/Entities")][0]
    
    MODULEPATHS=[]
    for i in ENTITIES:
        if os.path.isdir(HOME+"/Entities/" + i +"/py"):
            MODULEPATHS.append(HOME+"/Entities/" + i +"/py")
        if os.path.isfile(HOME+"/Entities/" + i +"/" + i + "/__init__.py"):
            MODULEPATHS.append(HOME+"/Entities/" + i)
    

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

    #Classmethod for getting global parameters
    @classmethod
    def getglobval(cls,**kwargs):
        # This is the sequence of string manipulations performed on a linege line
        name=kwargs.get('name','')
        str=kwargs.get('str','')
        MATCH='('+name+'=)(.*)'
        func_list=(
            lambda s: re.sub(MATCH,r'\2',s), 
            lambda s: re.sub(r'"','',s),
            lambda s: re.sub(r'\n','',s)
        )
        return reduce(lambda s, func: func(s), func_list, str)
    
    fid = open('./TheSDK.config','r')
    GLOBALS={}
    for name in GLOBAL_PARAMETERS:
        GLOBALS[name]=''
        for line in fid:
            MATCH='('+name+'=)(.*)'
            if re.match(MATCH,line):
                GLOBALS[name]=getglobval(**{'name':name,'str':line})
                print("GLOBALS[%s]=%s"%(name,GLOBALS[name])

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
    def print_log(self,argdict={'type': 'I', 'msg': "Print this to log"} ):
        if not os.path.isfile(thesdk.logfile):
            typestr="INFO at "
            msg="Inited logging in %s" %(thesdk.logfile)
            fid= open(thesdk.logfile, 'a')
            print("%s %s thesdk: %s" %(time.strftime("%H:%M:%S"), typestr , msg))
            fid.write("%s %s thesdk: %s\n" %(time.strftime("%H:%M:%S"), typestr, msg))
            fid.close()

        if argdict['type']== 'D':
            if self.DEBUG:
                typestr="DEBUG at"
                print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
                if hasattr(self,"logfile"):
                    fid= open(thesdk.logfile, 'a')
                    fid.write("%s %s %s: %s\n" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
            return
        elif argdict['type']== 'I':
           typestr="INFO at "
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
        elif argdict['type']=='W':
           typestr="WARNING! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
        elif argdict['type']=='E':
           typestr="ERROR! at"
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 

        elif argdict['type']=='F':
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
class refptr:
    def __init__(self): 
        #self.parent =[];
        #self.proplist = { 'Rs' };    #%properties that can be propagated from parent
        #self.Rs = 100e6;             #% sampling frequency
        self.Value = [];
        #self.model='matlab';

    #def get.Value(self):
    #    return self.Value
