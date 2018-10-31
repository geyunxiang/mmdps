from mmdps.dms import dbgen


if __name__ == '__main__':
    dg = dbgen.DatabaseGenerator('rawtable/ChanggengMRITable.csv',
        'mmdpdb.db',
        'rawtable/scipatient_motionscores.csv',
        'rawtable/jixieshou_BCI+Jixieshou_scores.csv',
        [('normal', 'Healthy normal people.', 'rawtable/normal_peopleorder.txt'),
         ('scipatient', 'SCI patients.', 'rawtable/patient_peopleorder.txt'),
         ('strokepatient', 'Stroke patients.', 'rawtable/jixieshou.txt')]
        )
    dg.run()
    
