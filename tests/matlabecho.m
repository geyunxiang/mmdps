function matlabecho(varargin)
disp('In matlab');
disp(['Number of input arguments: ', int2str(nargin)]);
celldisp(varargin);
end