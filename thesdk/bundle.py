# Bundle is a Dict of something
# Class is needed to define bundle operations
import abc
from abc import *
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

    def __init__(self,**kwargs): 
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

    def __getstate__(self):
        return self.__dict__.copy()
    def __setstate__(self,state):
        self.__dict__.update(state)

