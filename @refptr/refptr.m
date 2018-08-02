% REFPTR class 
% Provides pointer access to properties of other classes
%
% See (referenced 2.8.2017)
% https://stackoverflow.com/questions/7085588/matlab-create-reference-handle-to-variable
% Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 02.08.2018 11:35
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  
classdef refptr < handle
    properties
        sourceHandle
        sourceFieldName
    end
    properties (Dependent = true)
         Value
    end

    methods                
        function obj = refptr(source, fieldName)            
            if iscell(source)
                obj.sourceHandle = source{1};
            else
                obj.sourceHandle = source;
            end
            obj.sourceFieldName = char(fieldName);
        end
        function value = get.Value( obj )
                if iscell(obj.sourceHandle)
                   value = obj.sourceHandle{1}.(obj.sourceFieldName);
                else 
                   value = obj.sourceHandle.(obj.sourceFieldName);
                end
        end
        function set.Value( obj, value )
            obj.sourceHandle.(obj.sourceFieldName) = value;
        end
    end              
end
