# THESDK io class 
# Provides io class and related methodology
#
# Created by Marko Kosunen
#
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 11.11.2018 10:02
##############################################################################
import sys
import os
import getpass
import time
import tempfile
import re
import abc
from abc import *
from functools import reduce

# As per Dec 2018, this is just a renamed refptr class with better
# property definition
class io(metaclass=abc.ABCMeta):

    def __init__(self): 
        self._data = None;

    @property
    def data(self):
        if hasattr(self,'_data'):
            return self._data
        else:
            self._data=None
        return self._data

    @data.setter
    def preserve_iofiles(self,value):
        self._preserve_iofiles=value

