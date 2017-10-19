# THESDK class 
# Provides commmon methods  for other classes TheSDK
# Created by Marko Kosunen
#
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 15.09.2018 17:44
##############################################################################
import os
import getpass
import time
import tempfile
import abc
import numpy as np
from refptr import *
#from inspect import currentframe, getframeinfo
#Set 'must have methods' with abstractmethod
#@abstractmethod
#Using this decorator requires that the class’s metaclass is ABCMeta or is 
#derived from it. A class that has a metaclass derived from ABCMeta cannot 
#be instantiated unless all of its abstract methods and properties are overridden.

class thesdk(metaclass=abc.ABCMeta):
    
    #Define here the common attributes for the system

    #Default logfile. Override with initlog if you want something else
    #/tmp/TheSDK_randomstr_uname_YYYYMMDDHHMM.log
    logfile="/tmp/TheSDK_" + os.path.basename(tempfile.mkstemp()[1])+"_"+getpass.getuser()+"_"+time.strftime("%Y%m%d%H%M")+".log"
    if os.path.isfile(logfile):
        os.remove(logfile)
    print("Setting default logfile %s" %(logfile))
    #Do not create the logfile here
    #----logfile stuff ends here

    def __init__(self):
        pass

    #Clas methpd for setting the logfile
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
                    setattr(self,self.proplist[i-1],getattr(self.parent,self.proplist[i-1]))

                    #Its nice to see how things propagate
                    if  hasattr(self.parent,self.proplist[i-1]):
                        print("Setting %s: %s to %s" %(self, self.proplist[i-1], getattr(self.parent,self.proplist[i-1]) ))
                        setattr(self,self.proplist[i-1],getattr(self.parent,self.proplist[i-1]))


