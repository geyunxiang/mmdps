## 一、预处理部分
sh脚本，用于FSL预处理。

* **dwi_preprocess.sh** 预处理，去颅骨，涡流校正

* **dwi_calc_normalize.sh** 配准到标准空间，flirt

## 二、特征计算
python脚本和config文件，在FSL预处理之后进行。

一共有5个用于计算的python脚本和4个config文件，可以依次运行python脚本以进行纤维束追踪及追踪结果分析。

### config文件说明
* **basic_config**：数据的基本信息，每个个体的DWI，mask，bvec，bval的文件名。

* **tracking_config**：追踪需要的config文件。
    tracking_method表示追踪方法选择，1：EuDX追踪；2：概率性追踪；3：确定性追踪；4：SFM追踪；5：mSFM追踪。
    evals_map_name和index_map_name是只有mSFM追踪才需要的，如果没有就写"None"，如果已经有计算过应该在和DWI在同一文件夹，写"XXX.nii.gz"；seed_mask_file可以指定某个mask文件(.nii.gz)作为种子生发区域，即只得到经过该区域的追踪结果。

*   **eval_config**：
评价追踪结果需要的config文件。track_root是追踪结果所在的根目录(下面应该有以每个个体名字命名的子文件夹)，tracking_method是"EuDX","deterministic","probabilistic","sfm"或"sfmnew"，是需要评价的追踪方法。eval_method是0(LiFE)或1(mLiFE),evals_map_name如果没有就写"None"，如果已经有计算过应该在和DWI在同一文件夹，写"XXX.nii.gz"，output_file是在哪个文件夹输出结果。

* **atlas_config**：计算连接矩阵和通过ROI纤维束数量的向量需要的config文件。

### python脚本说明
1. **dwi_dtifit_job.py**
需要basic_config配置文件，计算得到FA并保存，用于后续的追踪。

2. **dwi_tracking_job.py**
需要basic_config和tracking_config，追踪得到纤维束并保存。

3. **dwi_eval_job.py**
需要basic_config和eval_config和追踪结果，得到误差(.nii.gz文件)并保存。

4. **dwi_atlas_job.py**
需要basic_config和atlas_config和追踪结果，得到通过每个脑区的纤维束数量并保存为向量（.mat文件）。

5. **dwi_connectivity_matrix.py**
需要basic_config和atlas_config和追踪结果，得到连接矩阵并保存为.mat文件。


### sfm_new方法运行过慢解决
get_evals_map()运行过慢，增大loc_range为3可以加快运行速度
/home/mmdp/Zhangziliang/GitWorkspace/mmdps/mmdps/sigProcess/DWI/tracking_plus/eval_.py
