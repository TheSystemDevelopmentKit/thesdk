<<<<<<< HEAD
# THESDK class 
# Provides commmon methods  for other classes TheSDK
#
##############################################################################
import abc
import numpy as np
from refptr import *

class thesdk(metaclass=abc.ABCMeta):
    def copy_propval(self,*arg):
        if len(arg)>=2:
            self.parent=arg[0]
            self.proplist=arg[1]
            for i in range(1,len(self.proplist)+1):
                if hasattr(self,self.proplist[i-1]):
                    setattr(self,self.proplist[i-1],getattr(self.parent,self.proplist[i-1]))

# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 15.09.2018 16:46
#classdef (Abstract) thesdk < handle
#    methods    
#        %To copy the properties from the parent
#        function obj=copy_propval(obj,varargin)
#            parent=varargin{1};
#            proplist=varargin{2};
#            for i = 1:length(proplist);
#                if isprop(parent,char(proplist{i}))==1 && isprop(obj,char(proplist{i}))==1
#                    obj.(char(proplist{i})) = parent.(char(proplist{i}));
#                end
#            end
#        end
#    end
#end

