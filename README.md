# Multi-Modal Data Processing System

## New Data Process Pipeline

1. Import Data

2. Process

	* T1: run `configpara_atlased_t1_project.json` and `configpara_unatlased_t1_project.json`. Remember to modify `FolderList`.

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