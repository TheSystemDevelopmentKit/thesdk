# THESDK class 
# Provides commmon methods  for other classes TheSDK
# Created by Marko Kosunen
#
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 15.09.2018 17:31
##############################################################################
import abc
import numpy as np
from refptr import *

class thesdk(metaclass=abc.ABCMeta):
    #self.logfile

    def copy_propval(self,*arg):
        if len(arg)>=2:
            self.parent=arg[0]
            self.proplist=arg[1]
            for i in range(1,len(self.proplist)+1):
                if hasattr(self,self.proplist[i-1]):
                    #Its nice to see how things propagate
                    if  hasattr(self.parent,self.proplist[i-1]):
                        msg="Setting %s: %s to %s" %(self, self.proplist[i-1], getattr(self.parent,self.proplist[i-1]))
                        #print("Setting %s: %s to %s" %(self, self.proplist[i-1], getattr(self.parent,self.proplist[i-1]) ))
                        self.print_log({'type': 'I', 'msg':msg})
                        setattr(self,self.proplist[i-1],getattr(self.parent,self.proplist[i-1]))

    #This is a method because it uses the logfile property
    def print_log(self,argdict={'type': 'I', 'msg': "Print this to log"} ):

        if argdict['type']== 'D':
            if self.DEBUG==True:
               typestr="DEBUG at "
        elif argdict['type']== 'I':
           typestr="INFO at "
        elif argdict['type']=='W':
           typestr="WARNING! at "
        elif argdict['type']=='E':
           typestr="ERROR! at "
        elif argdict['type']=='F':
           typestr="FATAL ERROR! at "

        print("%s,  %s: %s" %(typestr, self.__class__.__name__ , argdict['msg'])) 

        if argdict['type']=='F':
            print("Quitting due to fatal error in %s" %(self.__class__.__name__))
            quit()

