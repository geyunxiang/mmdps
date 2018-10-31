Install nginx.
Copy htpasswd .crt, .key, .conf to conf folder.
Start nginx.
You should generate the .crt and .key youself.
The root folder is ../Data with the structure:
Data
  MRIData
    patient0
      T1.nii.gz, T2.nii.gz, BOLD.nii.gz, DWI.nii.gz
    parient1
      T1.nii.gz, T2.nii.gz, DWI.nii.gz
    ...
