# THESDK class 
# Provides commmon methods  for other classes TheSDK
# Created by Marko Kosunen
#
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 15.09.2018 17:58
##############################################################################
import sys
import os
import re
import glob
import getpass
import time
import tempfile
import abc
import numpy as np
#from refptr import *
#from inspect import currentframe, getframeinfo
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

    #Appending all TheSDK python modules to system path (only ones, with set subtraction)
    #This could be done as oneliner with lambda,filter, map and recude, but due to name scope 
    #definitions, this is simpler method in class definition
    ENTITIES=[(x[1]) for x in os.walk( HOME + "/Entities")][0]
    
    MODULEPATHS=[]
    for i in ENTITIES:
        if os.path.isdir(HOME+"/Entities/" + i +"/py"):
            MODULEPATHS.append(HOME+"/Entities/" + i +"/py")
    
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
        if not os.path.isfile(self.logfile):
            typestr="INFO at "
            msg="Inited logging in %s" %(self.logfile)
            fid= open(self.logfile, 'a')
            print("%s %s thesdk: %s" %(time.strftime("%H:%M:%S"), typestr , msg))
            fid.write("%s %s thesdk: %s\n" %(time.strftime("%H:%M:%S"), typestr, msg))
            fid.close()

        if argdict['type']== 'D':
            if self.DEBUG:
                typestr="DEBUG at"
                print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 
                if hasattr(self,"logfile"):
                    fid= open(self.logfile, 'a')
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
               fid= open(self.logfile, 'a')
               fid.write("%s Quitting due to fatal error in %s.\n" %( time.strftime("%H:%M:%S"), self.__class__.__name__))
               fid.close()
               quit()
        else:
           typestr="ERROR! at"
           msg="Incorrect message type. Choose one of 'D', 'I', 'E' or 'F'."
           print("%s %s %s: %s" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 

        #If logfile set, print also there 
        if hasattr(self,"logfile"):
            fid= open(self.logfile, 'a')
            fid.write("%s %s %s: %s\n" %(time.strftime("%H:%M:%S"), typestr, self.__class__.__name__ , argdict['msg'])) 


