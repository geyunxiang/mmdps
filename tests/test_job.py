from mmdps.proc import job
from mmdps.util.loadsave import load_json_ordered, save_json_ordered

def run_jobconf(d):
    j = job.load(d)
    j.run()
    return j

def test_load_save(jobfile):
    jconf = load_json_ordered(jobfile)
    print(jconf)
    j = run_jobconf(jconf)
    
    outd = job.dump(j)
    print(outd)
    run_jobconf(outd)
    save_json_ordered('saved_' + jobfile, outd)

if __name__ == '__main__':
    test_load_save('config_alljob.json')
    test_load_save('saved_config_alljob.json')
    
