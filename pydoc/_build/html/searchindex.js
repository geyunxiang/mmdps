Search.setIndex({docnames:["index","mmdps","mmdps.common","mmdps.dms","mmdps.gui","mmdps.proc","mmdps.util","mmdps.vis"],envversion:53,filenames:["index.rst","mmdps.rst","mmdps.common.rst","mmdps.dms.rst","mmdps.gui.rst","mmdps.proc.rst","mmdps.util.rst","mmdps.vis.rst"],objects:{"":{mmdps:[1,0,0,"-"]},"mmdps.dms":{apicore:[3,0,0,"-"],batchget:[3,0,0,"-"],converter:[3,0,0,"-"],dbgen:[3,0,0,"-"],exporter:[3,0,0,"-"],importer:[3,0,0,"-"],mridata:[3,0,0,"-"],storage:[3,0,0,"-"],tables:[3,0,0,"-"]},"mmdps.dms.apicore":{ApiCore:[3,1,1,""],name_date:[3,3,1,""]},"mmdps.dms.apicore.ApiCore":{download:[3,2,1,""],feature_full_url:[3,2,1,""],feature_get:[3,2,1,""],full_url:[3,2,1,""],get:[3,2,1,""],get_mriscan_by_namedate:[3,2,1,""],get_mriscan_data_iter_r:[3,2,1,""],get_namedate_by_mriscanid:[3,2,1,""],get_person_by_name:[3,2,1,""],getdict:[3,2,1,""],getobjdict:[3,2,1,""],gettabledict:[3,2,1,""],valid:[3,2,1,""]},"mmdps.dms.batchget":{BatchGet:[3,1,1,""]},"mmdps.dms.batchget.BatchGet":{proc_mriscan:[3,2,1,""],run:[3,2,1,""]},"mmdps.dms.converter":{NiftiGetter:[3,1,1,""],convert_dicom_to_nifti:[3,3,1,""]},"mmdps.dms.converter.NiftiGetter":{fnmatch_all:[3,2,1,""],fnmatch_one:[3,2,1,""],get_BOLD:[3,2,1,""],get_DWI:[3,2,1,""],get_T1:[3,2,1,""],get_T2:[3,2,1,""]},"mmdps.dms.dbgen":{DatabaseGenerator:[3,1,1,""],name_date:[3,3,1,""]},"mmdps.dms.dbgen.DatabaseGenerator":{insert_grouptable:[3,2,1,""],insert_grouptables:[3,2,1,""],insert_motionscorerow:[3,2,1,""],insert_motionscoretable:[3,2,1,""],insert_mrirow:[3,2,1,""],insert_mritable:[3,2,1,""],insert_strokescorerow:[3,2,1,""],insert_strokescoretable:[3,2,1,""],run:[3,2,1,""]},"mmdps.dms.exporter":{MRIScanTableExporter:[3,1,1,""]},"mmdps.dms.exporter.MRIScanTableExporter":{add_row:[3,2,1,""],checkmodals:[3,2,1,""],gen_csv:[3,2,1,""],run:[3,2,1,""]},"mmdps.dms.importer":{MRIScanImporter:[3,1,1,""]},"mmdps.dms.importer.MRIScanImporter":{copy_nifti:[3,2,1,""],copy_nifti_one:[3,2,1,""],copy_nifti_one_modal:[3,2,1,""],run:[3,2,1,""],update_db:[3,2,1,""]},"mmdps.dms.mridata":{FeatureDataAccessor:[3,1,1,""],MRIDataAccessor:[3,1,1,""]},"mmdps.dms.mridata.FeatureDataAccessor":{build_uri:[3,2,1,""],get_iter_r_mriscan:[3,2,1,""]},"mmdps.dms.mridata.MRIDataAccessor":{build_uri:[3,2,1,""],get_iter_r:[3,2,1,""],modal_to_file:[3,2,1,""]},"mmdps.dms.storage":{HTTPStorage:[3,1,1,""],Storage:[3,1,1,""]},"mmdps.dms.storage.HTTPStorage":{CHUNK_SIZE:[3,4,1,""],PROGRESSBAR_LENGTH:[3,4,1,""],error:[3,2,1,""],full_url:[3,2,1,""],get:[3,2,1,""],get_file:[3,2,1,""],get_file_iter_r:[3,2,1,""],get_file_progress:[3,2,1,""]},"mmdps.dms.tables":{BaseModel:[3,1,1,""],Group:[3,1,1,""],MRIScan:[3,1,1,""],MotionScore:[3,1,1,""],Person:[3,1,1,""],StrokeScore:[3,1,1,""]},"mmdps.dms.tables.Group":{description:[3,4,1,""],id:[3,4,1,""],name:[3,4,1,""],people:[3,4,1,""]},"mmdps.dms.tables.MRIScan":{date:[3,4,1,""],get_folder:[3,2,1,""],hasBOLD:[3,4,1,""],hasDWI:[3,4,1,""],hasT1:[3,4,1,""],hasT2:[3,4,1,""],id:[3,4,1,""],motionscores:[3,4,1,""],person:[3,4,1,""],person_id:[3,4,1,""],strokescores:[3,4,1,""]},"mmdps.dms.tables.MotionScore":{date:[3,4,1,""],id:[3,4,1,""],mriscan:[3,4,1,""],mriscan_id:[3,4,1,""],person:[3,4,1,""],person_id:[3,4,1,""],scMAS:[3,4,1,""],scMotor:[3,4,1,""],scSCIM:[3,4,1,""],scSensory:[3,4,1,""],scTSI:[3,4,1,""],scVAS:[3,4,1,""],scWISCI2:[3,4,1,""]},"mmdps.dms.tables.Person":{birth:[3,4,1,""],gender:[3,4,1,""],groups:[3,4,1,""],id:[3,4,1,""],motionscores:[3,4,1,""],mriscans:[3,4,1,""],name:[3,4,1,""],strokescores:[3,4,1,""]},"mmdps.dms.tables.StrokeScore":{date:[3,4,1,""],id:[3,4,1,""],mriscan:[3,4,1,""],mriscan_id:[3,4,1,""],person:[3,4,1,""],person_id:[3,4,1,""],scARAT:[3,4,1,""],scFMA:[3,4,1,""],scWOLF:[3,4,1,""]},"mmdps.gui":{configfield:[4,0,0,"-"],field:[4,0,0,"-"],guiframe:[4,0,0,"-"],tktools:[4,0,0,"-"]},"mmdps.gui.configfield":{ConfigFieldConnector:[4,1,1,""],DefaultSimpleConnector:[4,1,1,""],find_by_name:[4,3,1,""]},"mmdps.gui.configfield.ConfigFieldConnector":{config_to_field:[4,2,1,""],field_to_config:[4,2,1,""]},"mmdps.gui.configfield.DefaultSimpleConnector":{config_to_field:[4,2,1,""],default_config:[4,2,1,""],field_to_config:[4,2,1,""]},"mmdps.gui.field":{BoolField:[4,1,1,""],ComboboxField:[4,1,1,""],CompositeField:[4,1,1,""],ConnectFieldVar:[4,1,1,""],Field:[4,1,1,""],FileEditField:[4,1,1,""],FileField:[4,1,1,""],FileJobConfigField:[4,1,1,""],FloatField:[4,1,1,""],FolderField:[4,1,1,""],IntField:[4,1,1,""],StringField:[4,1,1,""],create:[4,3,1,""],dump:[4,3,1,""],load:[4,3,1,""],setbyname:[4,3,1,""]},"mmdps.gui.field.BoolField":{build_widget:[4,2,1,""]},"mmdps.gui.field.ComboboxField":{build_widget:[4,2,1,""],from_dict:[4,5,1,""],to_dict:[4,2,1,""]},"mmdps.gui.field.CompositeField":{build_widget:[4,2,1,""],from_dict:[4,5,1,""],to_config:[4,2,1,""],to_dict:[4,2,1,""]},"mmdps.gui.field.ConnectFieldVar":{cb_var_change:[4,2,1,""]},"mmdps.gui.field.Field":{from_dict:[4,5,1,""],to_config:[4,2,1,""],to_dict:[4,2,1,""]},"mmdps.gui.field.FileEditField":{build_widget:[4,2,1,""],cb_button_Edit:[4,2,1,""],cb_button_Select:[4,2,1,""]},"mmdps.gui.field.FileField":{build_widget:[4,2,1,""],cb_button_Select:[4,2,1,""]},"mmdps.gui.field.FileJobConfigField":{cb_button_Edit:[4,2,1,""]},"mmdps.gui.field.FloatField":{build_widget:[4,2,1,""]},"mmdps.gui.field.FolderField":{build_widget:[4,2,1,""],cb_button_Select:[4,2,1,""]},"mmdps.gui.field.IntField":{build_widget:[4,2,1,""]},"mmdps.gui.field.StringField":{build_widget:[4,2,1,""]},"mmdps.gui.guiframe":{MainWindow:[4,1,1,""]},"mmdps.gui.guiframe.MainWindow":{add_action:[4,2,1,""],create_scrolledmain:[4,2,1,""],create_toolbar:[4,2,1,""],create_unscrolledmain:[4,2,1,""],mainframe:[4,4,1,""],on_frame_configure:[4,2,1,""],set_mainwidget:[4,2,1,""]},"mmdps.gui.tktools":{askdirectory:[4,3,1,""],askopenfilename:[4,3,1,""],asksaveasfilename:[4,3,1,""],button:[4,3,1,""],checkbutton:[4,3,1,""],combobox:[4,3,1,""],entry:[4,3,1,""],frame:[4,3,1,""],label:[4,3,1,""],labeled_widget:[4,3,1,""],labelframe:[4,3,1,""],listbox:[4,3,1,""]},"mmdps.proc":{atlas:[5,0,0,"-"],dataexport:[5,0,0,"-"],fusion:[5,0,0,"-"],job:[5,0,0,"-"],jobconfigfield:[5,0,0,"-"],loader:[5,0,0,"-"],netattr:[5,0,0,"-"],para:[5,0,0,"-"],parabase:[5,0,0,"-"],paraconfigfield:[5,0,0,"-"]},"mmdps.proc.atlas":{Atlas:[5,1,1,""],get:[5,3,1,""],getbyenv:[5,3,1,""],getbywd:[5,3,1,""]},"mmdps.proc.atlas.Atlas":{add_volumes:[5,2,1,""],adjust_mat:[5,2,1,""],adjust_mat_col:[5,2,1,""],adjust_mat_row:[5,2,1,""],adjust_ticks:[5,2,1,""],adjust_vec:[5,2,1,""],create_sub:[5,2,1,""],fullpath:[5,2,1,""],get_volume:[5,2,1,""],indexes_to_ticks:[5,2,1,""],regions_to_indexes:[5,2,1,""],ticks_to_indexes:[5,2,1,""],ticks_to_regions:[5,2,1,""]},"mmdps.proc.dataexport":{MRIScanProcExporter:[5,1,1,""],MRIScanProcMRIScanAtlasExporter:[5,1,1,""],create_by_files:[5,3,1,""],create_by_folder:[5,3,1,""]},"mmdps.proc.dataexport.MRIScanProcExporter":{run:[5,2,1,""],run_mriscan_atlas:[5,2,1,""]},"mmdps.proc.dataexport.MRIScanProcMRIScanAtlasExporter":{fullinfolder:[5,2,1,""],fulloutfolder:[5,2,1,""],run:[5,2,1,""],run_feature:[5,2,1,""]},"mmdps.proc.fusion":{ForeachBase:[5,1,1,""],ForeachMRIScan:[5,1,1,""],ForeachPerson:[5,1,1,""],Fusion:[5,1,1,""],create_by_files:[5,3,1,""],create_by_folder:[5,3,1,""],load_json_nonraise:[5,3,1,""],merge_dicts:[5,3,1,""]},"mmdps.proc.fusion.ForeachBase":{run:[5,2,1,""],work:[5,2,1,""]},"mmdps.proc.fusion.Fusion":{init_all:[5,2,1,""],init_groups:[5,2,1,""],init_netattr:[5,2,1,""],init_scores:[5,2,1,""]},"mmdps.proc.job":{BatchJob:[5,1,1,""],Chdir:[5,1,1,""],ExecutableJob:[5,1,1,""],Job:[5,1,1,""],MatlabJob:[5,1,1,""],PythonJob:[5,1,1,""],ShellJob:[5,1,1,""],call_in_wd:[5,3,1,""],call_logged2:[5,3,1,""],call_logged:[5,3,1,""],create:[5,3,1,""],dump:[5,3,1,""],genlogfilename:[5,3,1,""],load:[5,3,1,""],runjob:[5,3,1,""]},"mmdps.proc.job.BatchJob":{run:[5,2,1,""],run_configfile:[5,2,1,""],run_joblist:[5,2,1,""]},"mmdps.proc.job.Job":{build_cmdlist:[5,2,1,""],build_fullcmd:[5,2,1,""],build_fullconfig:[5,2,1,""],build_rootcmd:[5,2,1,""],from_dict:[5,5,1,""],run:[5,2,1,""],to_dict:[5,2,1,""]},"mmdps.proc.job.MatlabJob":{build_cmdlist:[5,2,1,""],build_matlab_logfile:[5,2,1,""],build_matlab_wd:[5,2,1,""],matlab_path_to_add:[5,2,1,""]},"mmdps.proc.job.PythonJob":{build_rootcmd:[5,2,1,""]},"mmdps.proc.jobconfigfield":{JobConfigFieldConnector:[5,1,1,""],OneJobConnector:[5,1,1,""]},"mmdps.proc.jobconfigfield.JobConfigFieldConnector":{config_to_field:[5,2,1,""],default_config:[5,2,1,""],field_to_config:[5,2,1,""]},"mmdps.proc.jobconfigfield.OneJobConnector":{JobConfigField:[5,4,1,""]},"mmdps.proc.loader":{AttrLoader:[5,1,1,""],GroupLoader:[5,1,1,""],Loader:[5,1,1,""],NetLoader:[5,1,1,""],ScoreLoader:[5,1,1,""]},"mmdps.proc.loader.AttrLoader":{load:[5,2,1,""]},"mmdps.proc.loader.GroupLoader":{build_internals:[5,2,1,""],load_mriscanstxt:[5,2,1,""],person_to_mriscans:[5,2,1,""]},"mmdps.proc.loader.Loader":{csvfilename:[5,2,1,""],fullfile:[5,2,1,""],load:[5,2,1,""],loaddata:[5,2,1,""],loadfilepath:[5,2,1,""],loadvstack:[5,2,1,""],names:[5,2,1,""]},"mmdps.proc.loader.NetLoader":{load:[5,2,1,""]},"mmdps.proc.loader.ScoreLoader":{load_scorecsvfile:[5,2,1,""],loadvstack:[5,2,1,""]},"mmdps.proc.netattr":{Attr:[5,1,1,""],Mat:[5,1,1,""],Net:[5,1,1,""]},"mmdps.proc.netattr.Attr":{copy:[5,2,1,""],gensub:[5,2,1,""],save:[5,2,1,""]},"mmdps.proc.netattr.Net":{copy:[5,2,1,""],gensub:[5,2,1,""],save:[5,2,1,""]},"mmdps.proc.para":{Para:[5,1,1,""],load:[5,3,1,""]},"mmdps.proc.para.Para":{from_dict:[5,5,1,""],run:[5,2,1,""],run_para:[5,2,1,""],run_seq:[5,2,1,""],to_dict:[5,2,1,""]},"mmdps.proc.parabase":{FWrap:[5,1,1,""],callfunc:[5,3,1,""],callrun:[5,3,1,""],get_processes:[5,3,1,""],run1:[5,3,1,""],run:[5,3,1,""],run_callfunc:[5,3,1,""],run_callrun:[5,3,1,""],run_in_background:[5,3,1,""],run_simple:[5,3,1,""]},"mmdps.proc.parabase.FWrap":{run:[5,2,1,""]},"mmdps.proc.paraconfigfield":{ParaConfigFieldConnector:[5,1,1,""]},"mmdps.proc.paraconfigfield.ParaConfigFieldConnector":{ParaConfigField:[5,4,1,""]},"mmdps.rootconfig":{dms:[1,1,1,""],path:[1,1,1,""],server:[1,1,1,""]},"mmdps.rootconfig.dms":{folder_dicom:[1,4,1,""],folder_mridata:[1,4,1,""],folder_rawnii:[1,4,1,""],folder_working:[1,4,1,""]},"mmdps.rootconfig.path":{atlas:[1,4,1,""],bnvdata:[1,4,1,""],data:[1,4,1,""],dcm2nii:[1,4,1,""],niiviewer:[1,4,1,""],proc:[1,4,1,""],pyroot:[1,4,1,""],python:[1,4,1,""],pythonw:[1,4,1,""],root:[1,4,1,""],texteditor:[1,4,1,""],tools:[1,4,1,""]},"mmdps.rootconfig.server":{api:[1,4,1,""],featurestorage:[1,4,1,""],storage:[1,4,1,""]},"mmdps.util":{clock:[6,0,0,"-"],dataop:[6,0,0,"-"],dwi:[6,0,0,"-"],fileop:[6,0,0,"-"],loadsave:[6,0,0,"-"],mattool:[6,0,0,"-"],path:[6,0,0,"-"],run:[6,0,0,"-"],toolman:[6,0,0,"-"]},"mmdps.util.clock":{iso_to_simple:[6,3,1,""],iso_to_time:[6,3,1,""],isofmt:[6,3,1,""],now:[6,3,1,""],simple_to_time:[6,3,1,""],simplefmt:[6,3,1,""],time_to_iso:[6,3,1,""]},"mmdps.util.dataop":{sub_list:[6,3,1,""],sub_mat:[6,3,1,""],sub_vec:[6,3,1,""]},"mmdps.util.dwi":{get_dwi_file_path:[6,3,1,""],get_dwi_img_gtab:[6,3,1,""],get_fvtk_streamlines_actor:[6,3,1,""],load_TrkFile:[6,3,1,""],load_streamlines_from_trk:[6,3,1,""],reslice_img:[6,3,1,""],save_streamlines_to_trk:[6,3,1,""]},"mmdps.util.fileop":{edit:[6,3,1,""],edit_json:[6,3,1,""],edit_text:[6,3,1,""],getfirstpart:[6,3,1,""],gz_unzip:[6,3,1,""],gz_zip:[6,3,1,""],open_nii:[6,3,1,""]},"mmdps.util.loadsave":{load_csvmat:[6,3,1,""],load_json:[6,3,1,""],load_json_ordered:[6,3,1,""],load_nii:[6,3,1,""],load_txt:[6,3,1,""],save_csvmat:[6,3,1,""],save_json:[6,3,1,""],save_json_ordered:[6,3,1,""],save_txt:[6,3,1,""]},"mmdps.util.mattool":{pearsonr:[6,3,1,""]},"mmdps.util.path":{builtinpathlist:[6,3,1,""],curatlas:[6,3,1,""],curatlasname:[6,3,1,""],curparent:[6,3,1,""],cwd:[6,3,1,""],defaultpathlist:[6,3,1,""],findfile:[6,3,1,""],fullfile:[6,3,1,""],getfilepath:[6,3,1,""],makedirs:[6,3,1,""],makedirs_file:[6,3,1,""],name_date:[6,3,1,""],path_tolist:[6,3,1,""],path_tovar:[6,3,1,""],projectpathlist:[6,3,1,""],rmtree:[6,3,1,""],searchpathlist:[6,3,1,""],splitext:[6,3,1,""]},"mmdps.util.run":{call:[6,3,1,""],call_py:[6,3,1,""],popen:[6,3,1,""],popen_py:[6,3,1,""],pyexe:[6,3,1,""],pyshellexe:[6,3,1,""]},"mmdps.util.toolman":{Tool:[6,1,1,""],ToolManager:[6,1,1,""],get_default_manager:[6,3,1,""]},"mmdps.util.toolman.Tool":{build_widget:[6,2,1,""],opentool:[6,2,1,""]},"mmdps.util.toolman.ToolManager":{find:[6,2,1,""],get:[6,2,1,""],load:[6,2,1,""],tools:[6,4,1,""]},"mmdps.vis":{attrprocs:[7,0,0,"-"],bnv:[7,0,0,"-"],heatmap:[7,0,0,"-"],line:[7,0,0,"-"],matprocs:[7,0,0,"-"],netprocs:[7,0,0,"-"],report:[7,0,0,"-"]},"mmdps.vis.attrprocs":{get:[7,3,1,""],reload:[7,3,1,""]},"mmdps.vis.bnv":{AbsThresholdProc:[7,1,1,""],BNVEdge:[7,1,1,""],BNVNode:[7,1,1,""],BNVPlot:[7,1,1,""],MatProc:[7,1,1,""],ScaleProc:[7,1,1,""],ThresholdProc:[7,1,1,""],fullfile_bnvdata:[7,3,1,""],gen_matlab:[7,3,1,""],get_cfg:[7,3,1,""],get_mesh:[7,3,1,""],sub_list:[7,3,1,""]},"mmdps.vis.bnv.AbsThresholdProc":{proc:[7,2,1,""]},"mmdps.vis.bnv.BNVEdge":{write:[7,2,1,""]},"mmdps.vis.bnv.BNVNode":{change_column:[7,2,1,""],change_label:[7,2,1,""],change_modular:[7,2,1,""],change_value:[7,2,1,""],copy:[7,2,1,""],copy_sub:[7,2,1,""],reset:[7,2,1,""],write:[7,2,1,""]},"mmdps.vis.bnv.BNVPlot":{fullpath:[7,2,1,""],gen_edge:[7,2,1,""],gen_node:[7,2,1,""],get_cfg:[7,2,1,""],get_mesh:[7,2,1,""],onesattr:[7,2,1,""],plot:[7,2,1,""],plot_attr:[7,2,1,""],plot_net:[7,2,1,""],plot_netattr:[7,2,1,""]},"mmdps.vis.bnv.MatProc":{proc:[7,2,1,""]},"mmdps.vis.bnv.ScaleProc":{proc:[7,2,1,""]},"mmdps.vis.bnv.ThresholdProc":{proc:[7,2,1,""]},"mmdps.vis.heatmap":{HeatmapPlot:[7,1,1,""]},"mmdps.vis.heatmap.HeatmapPlot":{get_cmap:[7,2,1,""],plot:[7,2,1,""]},"mmdps.vis.line":{LinePlot:[7,1,1,""]},"mmdps.vis.line.LinePlot":{plot:[7,2,1,""]},"mmdps.vis.matprocs":{absolute:[7,3,1,""],negativeonly:[7,3,1,""],noproc:[7,3,1,""],positiveonly:[7,3,1,""]},"mmdps.vis.netprocs":{get_valuerange:[7,3,1,""]},"mmdps.vis.report":{PlotAttr:[7,1,1,""],PlotNet:[7,1,1,""]},"mmdps.vis.report.PlotAttr":{run:[7,2,1,""],run_plot_bnv:[7,2,1,""],run_plot_line:[7,2,1,""]},"mmdps.vis.report.PlotNet":{run:[7,2,1,""],run_plot_heatmap:[7,2,1,""]},mmdps:{common:[2,0,0,"-"],dms:[3,0,0,"-"],gui:[4,0,0,"-"],proc:[5,0,0,"-"],rootconfig:[1,0,0,"-"],util:[6,0,0,"-"],vis:[7,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"],"4":["py","attribute","Python attribute"],"5":["py","classmethod","Python class method"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function","4":"py:attribute","5":"py:classmethod"},terms:{"boolean":4,"case":[4,5],"class":[1,3,4,5,6,7],"default":[4,5,6,7],"export":[0,1,5],"float":4,"function":[4,5],"import":[0,1,5,6],"int":4,"new":[3,4,5,7],"return":[3,4,5,6,7],"static":[1,3],"true":[3,4,5,6],"var":4,For:[5,6,7],One:[4,5],Such:3,The:[1,3,4,5,6,7],There:5,Use:[3,4,5,6],Useful:[5,6],aal:5,abs:7,absolut:[5,7],absthresholdproc:7,access:[3,5],accord:5,act:6,action:4,actor:6,actual:[4,5],add:[1,3,4,5,7],add_act:4,add_row:3,add_volum:5,added:5,adding:4,addpath:5,address:1,addtick:5,adjust:5,adjust_mat:5,adjust_mat_col:5,adjust_mat_row:5,adjust_tick:5,adjust_vec:5,affin:6,after:[5,7],alchemi:3,all:[3,4,5,6,7],allfunc:5,alreadi:4,also:[4,5],ani:5,anytre:4,api:[1,3],apicor:[0,1],app:[1,3],append:5,arg:[4,5],argv:[5,6],argvec:5,around:1,arrai:[5,6],ask:4,askdirectori:4,askopenfilenam:4,asksaveasfilenam:4,associ:4,atla:[0,1,6],atlas:5,atlasfold:5,atlasnam:5,atlasname_default:5,atlasobj:5,attr:[5,7],attribut:[5,7],attrload:5,attrnam:[5,7],attrproc:[0,1],auth:3,avoid:[5,6],back:5,background:5,bar:3,base:[1,3,4,5,6,7],basemodel:3,basic:4,bat:6,batch:[3,5],batchget:[0,1],batchjob:5,becaus:4,befor:[5,6],begin:3,better:3,bin:1,birth:3,block:3,bnv:[0,1],bnv_cfg:7,bnv_mesh:7,bnvdata:1,bnvedg:7,bnvnode:7,bnvplot:7,bold:3,bool:4,boolfield:[4,5],both:[3,5],brain:5,brainnet:7,brainnetview:7,brodmann_lr:5,bsecond:5,build:[3,4,5,6],build_cmdlist:5,build_fullcmd:5,build_fullconfig:5,build_intern:5,build_matlab_logfil:5,build_matlab_wd:5,build_rootcmd:5,build_uri:3,build_widget:[4,6],built:6,builtinpathlist:6,button:[4,6],bval:[3,6],bvec:[3,6],calcul:[5,6],call:[3,4,5,6],call_in_wd:5,call_log:5,call_logged2:5,call_pi:6,callback:4,callfunc:5,callrun:5,can:[1,3,4,5,6],cannot:6,canon:6,caselist:5,caus:4,cb_button_edit:4,cb_button_select:4,cb_var_chang:4,cfgname:7,chang:[3,4,5,7],change_column:7,change_label:7,change_modular:7,change_valu:7,chdir:5,chdirto:5,check:[3,4,5,7],checkbutton:4,checkmod:3,child:4,children:[4,5],chunk_siz:3,circluar:6,clash:5,classmethod:[4,5],click:4,clinic:5,clock:[0,1],closest:6,cls_niftigett:3,cmap:7,cmd:[1,5,6],cmdlist:[5,6],code:1,col:7,column:[5,6,7],colvalu:7,combobox:4,comboboxfield:[4,5],command:[4,5,6],command_popup:4,command_select:4,common:[0,1,6],compos:4,composit:4,compositefield:[4,5],comput:5,config:[1,4,5,6,7],config_to_field:[4,5],configfield:[0,1,5],configfieldconnector:[4,5],configfil:5,configjob:5,configpara:5,configsfold:5,configur:[1,3,4,5,6],connect:3,connectfieldvar:4,connector:[4,5],consid:7,consol:5,construct:[3,4,5],constructor:5,consum:[3,5],contain:[4,5],content:0,context:5,convers:3,convert:[0,1,4,5],convert_dicom_to_nifti:3,coolwarm:7,copi:[3,5,7],copy_nifti:3,copy_nifti_on:3,copy_nifti_one_mod:3,copy_sub:7,correspond:[4,5,7],could:3,count:5,creat:[3,4,5,7],create_by_fil:5,create_by_fold:5,create_engin:3,create_scrolledmain:4,create_sub:5,create_toolbar:4,create_unscrolledmain:4,csv:[3,5,6],csvdict:5,csvfilenam:5,csvwriter:3,curatla:6,curatlasnam:6,curpar:6,current:[5,6,7],cwd:6,data:[1,3,4,5,6,7],data_dicom:1,data_rawnii:1,databas:[3,5],databasegener:3,dataconfig:5,dataconfigfil:5,dataexport:[0,1],dataop:[0,1],date:[3,6],dbfile:3,dbgen:[0,1],dcm2nii:1,dcm2niix:1,deal:5,declar:3,dedic:6,default_config:[4,5],defaultpathlist:6,defaultsimpleconnector:[4,5],defin:[3,5,6],desc:5,descdict:5,descript:[3,5],detail:7,dicom:3,dict:[3,4,5,6],differ:5,dimens:[5,6],dimension:5,dipi:6,dir:[5,6],directli:4,directori:[4,5,6],dirnam:6,dms:[0,1],don:[4,6],done:5,download:3,dump:[4,5],dwi:[0,1,3],dwifil:3,each:[5,6],eas:[3,4],edg:7,edgefil:7,edgepath:7,edit:[1,4,6],edit_json:6,edit_text:6,editor:6,element:4,empti:4,enter:5,entri:4,env:6,environ:[5,6],error:3,event:4,everi:[3,5],everyth:5,exactli:3,exampl:5,except:5,exe:[1,6],execut:[5,6],executablejob:5,exist:[1,3],exist_ok:6,exit:5,ext:[3,4,6],extract:6,f_attrproc:7,f_netproc:7,fail:5,fals:[5,6],fanci:3,fbval:6,fbvec:6,fdwi:6,featur:[3,5],feature_full_url:3,feature_get:3,featureconfig:5,featuredata:3,featuredataaccessor:3,featurenam:5,featureroot:3,featurestorag:1,field:[0,1,5],field_to_config:[4,5],file:[1,3,4,5,6,7],fileeditfield:[4,5],filefield:[4,5],filejobconfigfield:4,filenam:[4,5,6],fileobj:6,fileop:[0,1,4],filepath:[3,6],finalfold:5,find:[4,6],find_by_nam:4,findfil:6,finish:5,first:6,firstonli:5,firstpart:6,flatten:5,flip:6,floatfield:4,fmt:6,fnmatch_al:3,fnmatch_on:3,folder:[1,3,4,5,6],folder_dicom:1,folder_mridata:1,folder_rawnii:1,folder_work:1,folderfield:[4,5],folderlist:5,foldernam:5,foreachbas:5,foreachmriscan:5,foreachperson:5,form:[3,5],format:6,four:5,frame:4,framework:5,from:[3,4,5],from_dict:[4,5],full:[3,5,6,7],full_url:3,fullfil:[5,6],fullfile_bnvdata:7,fullinfold:5,fulloutfold:5,fullpath:[5,7],fusion:[0,1],fwrap:5,gen_csv:3,gen_edg:7,gen_matlab:7,gen_nod:7,gender:3,gener:[3,5,6,7],genlogfilenam:5,gensub:5,get:[3,5,6,7],get_bold:3,get_cfg:7,get_cmap:7,get_default_manag:6,get_dwi:3,get_dwi_file_path:6,get_dwi_img_gtab:6,get_fil:3,get_file_iter_r:3,get_file_progress:3,get_fold:3,get_fvtk_streamlines_actor:6,get_iter_r:3,get_iter_r_mriscan:3,get_mesh:7,get_mriscan_by_named:3,get_mriscan_data_iter_r:3,get_namedate_by_mriscanid:3,get_person_by_nam:3,get_process:5,get_t1:3,get_t2:3,get_valuerang:7,get_volum:5,getbyenv:5,getbywd:5,getdict:3,getfilepath:6,getfirstpart:6,getfunc:3,getobjdict:3,gettabledict:3,glob:3,gradient:6,grei:7,group:[3,5],groupconfigdict:5,groupfil:5,groupload:5,groupsconfig:5,grouptabl:3,gui:[0,1,3,5,6],guifram:[0,1],gz_unzip:6,gz_zip:6,gzfile:6,handl:5,hasbold:3,hasdwi:3,hast1:3,hast2:3,have:[5,7],heatmap:[0,1],heatmapplot:7,how:5,http:[1,3],httpstorag:3,human:4,idx:7,imag:[6,7],img:6,implement:[4,6],import_changgung:1,includ:5,index:[0,5,6,7],indexes_to_tick:5,indic:3,infil:6,info:5,infold:3,inform:3,inherit:3,init:[4,5,7],init_al:5,init_group:5,init_netattr:5,init_scor:5,initdict:4,inmainfold:3,input:[4,5,7],insert:3,insert_groupt:3,insert_motionscorerow:3,insert_motionscoret:3,insert_mrirow:3,insert_mrit:3,insert_strokescorerow:3,insert_strokescoret:3,integ:4,interchang:4,interfac:3,intern:5,interpret:5,intfield:4,iso:6,iso_to_simpl:6,iso_to_tim:6,isofmt:6,isostr:6,item:4,iter:[3,5],itself:[4,5],jfile:[5,6],job:[0,1,4],jobconfig:5,jobconfigfield:[0,1],jobconfigfieldconnector:5,joblist:5,jobobj:5,join:6,json:[3,5,6],just:[5,7],kwarg:[3,4,5],label:[4,7],labeled_widget:4,labelfram:4,labeltext:4,launch:4,leav:4,len:5,like:[5,6],limit:3,line:[0,1,5,6],lineplot:7,linux:1,list:[3,4,5,6,7],listbox:4,load:[4,5,6],load_csvmat:6,load_json:6,load_json_nonrais:5,load_json_ord:6,load_mriscanstxt:5,load_nii:6,load_scorecsvfil:5,load_streamlines_from_trk:6,load_trkfil:6,load_txt:6,loaddata:5,loader:[0,1],loadfilepath:5,loadsav:[0,1],loadvstack:5,localpath:3,log:5,lot:5,mai:5,main:[1,3,4],mainconffil:5,mainconfig:5,mainconfigfil:5,mainfold:5,mainfram:4,mainli:3,mainwindow:4,make:[5,6],makedir:6,makedirs_fil:6,manag:[3,5,6],mani:[4,5],manipul:7,manual:[1,7],map:3,master:[4,6],mat:[5,6,7],match:3,matfil:6,matlab:[5,6,7],matlab_path_to_add:5,matlabjob:5,matlabpath:5,matproc:[0,1],matrix:[5,6,7],mattool:[0,1],merg:5,merge_dict:5,mesh:7,meshnam:7,method:4,microsoft:1,mmdpdatabas:1,mmdpdb:3,mmdps_builtinpath:6,mmdps_cur_atla:5,mmdpsoftwar:1,mmdpsvarsal:6,modal:[3,5],modal_to_fil:3,model:3,modifi:1,modul:0,modular:7,more:[3,4],mostli:6,motion:3,motionscor:3,motionscoredict:3,motionscoretablecsv:3,move:1,mricrogl:1,mricron:1,mridata:[0,1],mridataaccessor:3,mriscan:[3,5,6],mriscan_id:3,mriscanfold:3,mriscanimport:3,mriscanprocexport:5,mriscanprocmriscanatlasexport:5,mriscansfold:3,mriscanstxt:3,mriscantableexport:3,mritabl:3,mritablecsv:3,msg:3,much:3,multipl:[3,6],multipli:5,must:4,name:[3,4,5,6,7],name_d:[3,6],named:3,need:[4,5],neg:7,negativeonli:7,net:[5,7],netattr:[0,1],netattrconfig:5,netattrfil:5,netattrnam:5,netload:5,netnam:7,netproc:[0,1],network:[5,7],new_zoom:6,newnam:3,newvalu:4,nib:6,nifti:[3,6],niftifold:3,niftigett:3,nii:[3,5,6],niifil:6,niinam:6,niiview:1,node:[4,7],nodefil:7,nodepath:7,non:3,none:[3,4,5,6,7],noproc:7,normal:5,note:6,now:[3,6],object:[1,3,4,5,6,7],objid:3,on_frame_configur:4,one:[3,5,6,7],onejobconnector:5,ones:7,onesattr:7,onli:[3,4,5,7],open:[4,6],open_nii:6,opentool:6,oper:6,order:[5,6],ordereddict:5,origin:7,orm:3,other:[3,5,6],otherwis:[5,6],out:5,outcsvnam:3,outedgefil:7,outfil:[5,6,7],outfilepath:[3,7],outfold:3,outmainfold:3,outnodefil:7,outpath:7,output:5,overrid:[4,5,7],own:[4,6,7],p00:5,p01:5,pack:4,packag:0,page:0,para:[0,1],parabas:[0,1,7],paraconfigfield:[0,1],paraconfigfieldconnector:5,parallel:[5,7],paramet:5,parent:[1,4,5,6],part:6,pass:4,pat:3,path:[0,1,3,5,7],path_tolist:6,path_tovar:6,pathlist:6,pathvar:6,pattern:3,pearsonr:6,peopl:[3,5],person:[3,5],person_id:3,person_to_mriscan:5,platform:1,plot:7,plot_attr:7,plot_bnv:5,plot_circo:5,plot_heatmap:5,plot_lin:5,plot_net:7,plot_netattr:7,plotattr:7,plotindex:5,plotnet:7,plottyp:7,popen:6,popen_pi:6,posit:7,positiveonli:7,possibl:[4,5,6],primit:4,proc:[0,1,7],proc_mriscan:3,proce:7,process:[5,6],program:[1,3,4,6],progress:[3,5],progressbar_length:3,project:[5,6],projectpathlist:6,proper:[3,4,5,6,7],properli:3,provid:[4,5,7],put:5,pyex:6,pyroot:1,pyshellex:6,python35:1,python:[1,3,5,6],pythonjob:5,pythonpath:1,pythonw:1,pyui:6,raw:[3,5],reachabl:6,readabl:4,receiv:3,record:3,regardless:5,region:5,regions_to_index:5,relat:6,reload:7,remov:6,renam:3,replac:4,report:[0,1,3,5],repres:[4,6,7],request:3,requir:1,reset:7,resid:5,resiz:4,reslic:6,reslice_img:6,rest:3,result:[3,6],ret:3,right:4,rmdb:3,rmtree:6,root:[1,4,5],rootcmd:5,rootconfig:0,row:[3,5],run1:5,run:[0,1,3,5,7],run_callfunc:5,run_callrun:5,run_configfil:5,run_featur:5,run_in_background:5,run_joblist:5,run_mriscan_atla:5,run_para:5,run_plot_bnv:7,run_plot_heatmap:7,run_plot_lin:7,run_seq:5,run_simpl:5,runjob:5,runmod:5,same:5,save:[4,5,6],save_csvmat:6,save_json:6,save_json_ord:6,save_streamlines_to_trk:6,save_txt:6,scale:7,scaleproc:7,scan:3,scarat:3,scfma:3,scma:3,scmotor:3,score:[3,5],scoreconfigdict:5,scorefil:5,scoreload:5,scoresconfig:5,script:[5,6],scroll:4,scscim:3,scsensori:3,sctsi:3,scva:3,scwisci2:3,scwolf:3,search:[0,5,6],searchpathlist:[5,6],second:5,secondlist:5,select:[3,4],self:5,send:3,sequenti:5,serial:[4,5],serv:[3,4],server:[1,3],set:[4,6],set_mainwidget:4,setbynam:4,sever:[5,6],shell:5,shelljob:5,should:[3,4,5,6],similar:[5,7],simpl:[3,4,5,6],simple_to_tim:6,simplefmt:6,simplestr:6,slow:7,softwar:[1,6],someth:6,sourc:[1,3,4,5,6,7],specif:3,specifi:[3,5,6],specifii:1,split:6,splitext:6,sqaur:5,sql:3,sqlalchemi:3,sqlite:3,sqmat:5,squar:7,storag:[0,1],store:4,str:4,streamlin:6,string:[4,5,6,7],stringfield:[4,5],stroke:3,strokescor:3,strokescoredict:3,strokescoretablecsv:3,structur:4,sub:[5,6,7],sub_list:[6,7],sub_mat:6,sub_vec:6,subatlasnam:5,subindex:[5,7],submodul:0,subpackag:[0,3],success:3,summari:3,suppli:5,sure:[4,5],system:3,tabl:[1,6],tablenam:3,task:5,test:[3,5],text:[4,6],texteditor:1,thejob:5,them:5,thepara:5,thi:[1,4,5,6,7],thing:5,thre:7,threshold:7,thresholdproc:7,tick:5,ticks_to_index:5,ticks_to_region:5,time:[3,5,6],time_to_iso:6,titl:7,tkinter:4,tktool:[0,1],tkvar:4,to_config:4,to_dict:[4,5],todo:[3,5,7],tool:[1,4,5,6],toolbar:4,toolman:[0,1],toolmanag:6,toolnam:6,tools_config:6,trackvi:6,tractographi:6,tree:[4,5,6],trk:6,tupl:3,two:5,txt:[5,6],txtfile:6,type:[5,7],typenam:5,typic:[3,5],ui_configjob:4,unit:5,unscrol:4,updat:[3,7],update_db:3,uri:3,url:3,urlbas:3,urlpath:3,use:[3,4,5,6,7],used:[3,4,5,6,7],usepyshel:6,user:3,using:[5,6],util:[0,1],valid:3,valu:[3,4,5,6,7],valuerang:7,variabl:[5,6],variou:4,vartyp:4,vec:[5,6],vector:[5,6],viewer:[6,7],vis:[0,1],visul:7,volum:[5,6],volumenam:5,vstack:5,vtk:6,wai:5,want:[4,5],webapp:3,what:[3,5],whateven:5,when:[1,3,4,5],whenev:[5,6],wheneven:[4,6],where:5,which:[3,5,6],whole:[3,4],widget:4,widgetclass:4,win32:1,window:4,without:5,work:[5,6],would:3,wrap:5,wrapper:4,write:[5,7],x86:1,xmat:6,xvec:6,you:[4,5,6],your:[4,6,7],yvec:6,zip:6},titles:["Welcome to MMDPS\u2019s documentation!","mmdps package","mmdps.common package","mmdps.dms package","mmdps.gui package","mmdps.proc package","mmdps.util package","mmdps.vis package"],titleterms:{"export":3,"import":3,apicor:3,atla:5,attrproc:7,batchget:3,bnv:7,clock:6,common:2,configfield:4,content:[1,2,3,4,5,6,7],convert:3,dataexport:5,dataop:6,dbgen:3,dms:3,document:0,dwi:6,field:4,fileop:6,fusion:5,gui:4,guifram:4,heatmap:7,indic:0,job:5,jobconfigfield:5,line:7,loader:5,loadsav:6,matproc:7,mattool:6,mmdp:[0,1,2,3,4,5,6,7],modul:[1,2,3,4,5,6,7],mridata:3,netattr:5,netproc:7,packag:[1,2,3,4,5,6,7],para:5,parabas:5,paraconfigfield:5,path:6,proc:5,report:7,rootconfig:1,run:6,storag:3,submodul:[1,3,4,5,6,7],subpackag:1,tabl:[0,3],tktool:4,toolman:6,util:6,vis:7,welcom:0}})