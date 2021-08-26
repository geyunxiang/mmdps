python脚本和config文件，在FSL预处理之后进行

一共有5个python脚本和4个config文件，可以依次运
行python脚本以进行纤维束追踪及追踪结果分析。

basic_config
数据的基本信息，包括data_root(下面应该有以每个个
体名字命名的子文件夹)，name_list(一个有每个个体的
名字的txt文件，每个名字占据一行)，和每个个体的DWI，
mask，bvec，bval的文件名。

tracking_config
追踪需要的config文件。
tracking_method表示追踪方法选择，
1：EuDX追踪；2：概率性追踪；3：确定性追踪；4：
SFM追踪；5：mSFM追踪
evals_map_name和index_map_name是只有mSFM
追踪才需要的，如果没有就写"None"，如果已经有计
算过应该在和DWI在同一文件夹，写"XXX.nii.gz"
seed_mask_file可以指定某个mask文件(.nii.gz)作为种
子生发区域，即只得到经过该区域的追踪结果。

eval_config
评价追踪结果需要的config文件。track_root是
追踪结果所在的根目录(下面应该有以每个个体
名字命名的子文件夹)，tracking_method是"Eu
DX","deterministic","probabilistic","sfm"或"sfm
new"，是需要评价的追踪方法。
eval_method是0(LiFE)或1(mLiFE),
evals_map_name如果没有就写"None"，如果已
经有计算过应该在和DWI在同一文件夹，写"XXX.
nii.gz"，output_file是在哪个文件夹输出结果。

atlas_config
计算连接矩阵和通过ROI纤维束数量的向量需要的
config文件。


1. dwi_dtifit.py
需要basic_config配置文件，计算得到FA并保存，用于
后续的追踪。

2.dwi_tracking.py
需要basic_config和tracking_config，追踪得到纤维束
并保存。

3.dwi_eval.py
需要basic_config和eval_config和追踪结果，得到误差
(.nii.gz文件)并保存。

4.dwi_atlas.py
需要basic_config和atlas_config和追踪结果，得到通过
每个脑区的纤维束数量并保存为向量（.mat文件）。

5.dwi_connectivity_matrix.py
需要basic_config和atlas_config和追踪结果，得到连接
矩阵并保存为.mat文件。