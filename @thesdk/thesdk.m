% THESDK class 
% Provides commmon methods  for other classes TheSDK
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 06.09.2017 13:37
classdef (Abstract) thesdk < handle
    properties (Abstract, SetAccess = public )
        parent
        proplist
    end
    methods    
        %To copy the properties from the parent
        function obj=copy_propval(obj,varargin)
            parent=varargin{1};
            proplist=varargin{2};
            for i = 1:length(proplist);
                if isprop(parent,char(proplist{i}))==1 && isprop(obj,char(proplist{i}))==1
                    obj.(char(proplist{i})) = parent.(char(proplist{i}));
                end
            end
        end
    end
end

