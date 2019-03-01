% Function: convert datatype from single to unsigned 
%			int (uint32), and save it as a .nii file
% Input: filename (string), prefix
% Output: uiwT1_brain.nii

data = load_nii('irT2_brain.nii');
img = data.img;
x = uint32(img);
y = make_nii(x);
new_filename = 'uirT2_brain.nii';
save_nii(y, new_filename);