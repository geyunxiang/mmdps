# Multi-Modal Data Processing System

## Environment setter

On Linux and macOS, one should set environment variable `MMDPS_ROOTDIR` at `~/.bashrc` or similar profile file. The `MMDPS_ROOTDIR` should point to the root dir of mmdps system. 

## New Data Process Pipeline

1. Import Data

2. Process

	* T1: run `configjob_main_t1.json`. Note: one should modify `configpara_unatlased_t1_project.json` and `configpara_atlased_t1_project.json` for the appropriate folder list.

	* DWI: run `configjob_main_dwi.json`. Note: one should modify `configpara_dwi_project.json` and `configpara_atlased_dwi_project.json` for the appropriate folder list.

	* BOLD: run `configpara_bold_project.json`. Remember to modify `FolderList`.

## Parallel mechanism

* Set env `set MMDPS_CPU_COUNT=n` to force the cpu count to n.

## Featured functionalities

### mmdps.util.loadsave

* Use `loadsave.load_txt` to read in a txt file line by line and obtain a list of strings. Each string is one row in the txt file. 

* Use `loadsave.load_csvmat` to read in a matrix saved as csv format. 

### mmdps.proc.loader

* Use this module to load networks/graph metrics or other features of a list of subjects/scans

* `loader.Loader.generate_mriscans` is used to generate a list of mriscans from a list of subject names. This is useful if one want to load all (up to) first/second... scans of some subjects.

* `loader.Loader.loadvstackmulti` is used to load attributes for a list of scans. The returned value is a list of Attrs.

## Dependencies

The python module `mmdps` requires the following python dependencies:

* `nibabel` for reading nii files. The version does not seem to influence result. Version `3.1.0` is tested. 

* `dipy` for DWI and DTI processing and feature extraction. This module has changed since the development of mmdps, which relied on version `0.11.0`. Several modules and functions have been deprecated and removed.

* `pydicom` for reading dicom files. 

* `anytree` for GUI related modules.

* `numpy`, `scipy` etc that are installed with `anaconda`

The process pipeline also needs other toolboxes, including:

* `DPARSFA` for fMRI preprocessing. Its version does not seems to influence result. 

* `spm` for fMRI preprocessing and T1 feature extraction. Its version INFLUENCE process result (be careful). The version on HPC at the lab is `spm12_v6470`. When using `spm12_v6906`, the BOLD network result can have a maximum of `1e-5` difference. When using `spm12_v7771`, however, the difference of BOLD network result would reach `0.05 - 0.10`, which would influence network analysis result. 

* `fsl` for DWI/DTI preprocessing and feature extraction. `fsl 5.0` or `fsl 6.0` does not seem to influence feature extraction result. 
