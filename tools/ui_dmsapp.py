import os
import functools
import tkinter as tk
import tkinter.simpledialog
from mmdps.gui import guiframe, tktools, field
from mmdps.dms import apicore
from mmdps.util.loadsave import load_json
from mmdps import rootconfig
from mmdps.proc import parabase
from mmdps.util import fileop


ThisDir = os.path.abspath(os.path.dirname(__file__))
ConfDir = os.path.join(ThisDir, 'ui_dmsapp_conf')

def loadconf(confname):
    return load_json(os.path.join(ConfDir, confname+'.json'))

class PersonFrame(guiframe.MainWindow):
    conf_personbasic = loadconf('personbasic')
    conf_mriscan = loadconf('mriscan')
    conf_motionscore = loadconf('motionscore')
    conf_strokescore = loadconf('strokescore')
    conf_group = loadconf('group')

    def __init__(self, master=None, **kw):
        guiframe.MainWindow.__init__(self, master, **kw)

    def setup(self, infoapi, personid):
        self._api = infoapi
        self._personid = personid
        self.build_widgets()
        
    def build_actions(self):
        pass

    def mriscan_open(self, mriscan_id, modal):
        def helper():
            if modal[-7:] != '.nii.gz':
                outfilename = modal + '.nii.gz'
            else:
                outfilename = modal
            localpath = os.path.join('temp_get', str(mriscan_id), outfilename)
            b = self._api.download('/mriscans/{}/get/{}'.format(mriscan_id, modal), localpath)
            if b:
                fileop.open_nii(localpath)
        parabase.run_in_background(helper)

    def mriscan_save(self, mriscan_id, modal):
        localpath = tktools.asksaveasfilename()
        def helper():
            b = self._api.download('/mriscans/{}/get/{}'.format(mriscan_id, modal), localpath)
            if b:
                print('Saved', localpath)
        parabase.run_in_background(helper)

    def build_mriscan_add_open_save(self, mriscan_id, wmodals):
        for modal, wmodal in wmodals:
            curf_open = functools.partial(self.mriscan_open, mriscan_id, modal)
            btn = tktools.button(wmodal, 'Open', curf_open)
            btn.pack(side='right')
            curf_save = functools.partial(self.mriscan_save, mriscan_id, modal)
            btn = tktools.button(wmodal, 'Save', curf_save)
            btn.pack(side='right')
            
    def build_mriscan(self, master, mriscan_id):
        mriscandict = self._api.getobjdict('mriscans', mriscan_id)
        curfield = field.load(self.conf_mriscan)
        children = curfield.children
        field.setbyname(children, 'id', mriscandict['id'])
        field.setbyname(children, 'date', mriscandict['date'])
        field.setbyname(children, 'T1', mriscandict['hasT1'])
        field.setbyname(children, 'T2', mriscandict['hasT2'])
        field.setbyname(children, 'BOLD', mriscandict['hasBOLD'])
        field.setbyname(children, 'DWI', mriscandict['hasDWI'])
        curw = curfield.build_widget(master)
        wchildren = curw.winfo_children()
        wT1 = wchildren[2]
        wT2 = wchildren[3]
        wBOLD = wchildren[4]
        wDWI = wchildren[5]
        wmodals = [('T1', wT1), ('T2', wT2), ('BOLD', wBOLD), ('DWI', wDWI)]
        self.build_mriscan_add_open_save(mriscan_id, wmodals)
        return curw
        
    def build_motionscore(self, master, motionscore_id):
        motionscoredict = self._api.getobjdict('motionscores', motionscore_id)
        curfield = field.load(self.conf_motionscore)
        scorenames = ['date', 'scTSI', 'scVAS', 'scSensory', 'scWISCI2', 'scSCIM', 'scMotor', 'scMAS']
        children = curfield.children
        for child, scorename in zip(children, scorenames):
            child.value = motionscoredict[scorename]
        curw = curfield.build_widget(master)
        return curw
    
    def build_strokescore(self, master, strokescore_id):
        strokescoredict = self._api.getobjdict('strokescores', strokescore_id)
        curfield = field.load(self.conf_strokescore)
        scorenames = ['date', 'scFMA', 'scARAT', 'scWOLF']
        children = curfield.children
        for child, scorename in zip(children, scorenames):
            child.value = strokescoredict[scorename]
        curw = curfield.build_widget(master)
        return curw

    def build_group(self, master, group_id):
        groupdict = self._api.getobjdict('groups', group_id)
        curfield = field.load(self.conf_group)
        scorenames = ['name', 'description']
        children = curfield.children
        for child, scorename in zip(children, scorenames):
            child.value = groupdict[scorename]
        curw = curfield.build_widget(master)
        return curw
        
    def build_multiple(self, master, name, buildfunc, ids):
        print('multiple', name)
        curframe = tktools.labelframe(master, name)
        for curid in ids:
            curw = buildfunc(curframe, curid)
            curw.pack(fill='x', expand=True)
        curframe.pack(fill='x', expand=True)
    
    def build_personbasic(self, master, persondict):
        curfield = field.load(self.conf_personbasic)
        curfield.children[0].value = persondict['id']
        curfield.children[1].value = persondict['name']
        curw = curfield.build_widget(master)
        curw.pack(fill='x', expand=True)
    
    def build_widgets(self):
        masterw = self.mainframe
        persondict = self._api.getobjdict('people', self._personid)
        self.build_personbasic(masterw, persondict)
        mriscan_ids = persondict.get('mriscans', [])
        self.build_multiple(masterw, 'MRIScans', self.build_mriscan, mriscan_ids)
        motionscore_ids = persondict.get('motionscores', [])
        self.build_multiple(masterw, 'MotionScores', self.build_motionscore, motionscore_ids)
        strokescore_ids = persondict.get('strokescores', [])
        self.build_multiple(masterw, 'StrokeScores', self.build_strokescore, strokescore_ids)
        group_ids = persondict.get('groups', [])
        self.build_multiple(masterw, 'Groups', self.build_group, group_ids)
        
        
class UserPassDialog(tk.simpledialog.Dialog):
    def body(self, master):
        wu, tkvar, frame = tktools.labeled_widget(master, 'Username', tktools.entry)
        self._tkvar_username = tkvar
        frame.pack()
        wp, tkvar, frame = tktools.labeled_widget(master, 'Password', tktools.entry, show='*')
        self._tkvar_password = tkvar
        frame.pack()
        return wu

    def validate(self):
        self.result = None
        u = self._tkvar_username.get()
        p = self._tkvar_password.get()
        self._auth = (u, p)
        self._api = apicore.ApiCore(rootconfig.server.api, self._auth)
        if self._api.valid():
            return 1
        else:
            return 0


    def apply(self):
        self.result = (self._api, self._auth)
    
class Application(guiframe.MainWindow):
    def __init__(self, master=None, **kw):
        guiframe.MainWindow.__init__(self, master, False, **kw)
        self.build_actions()
        self.build_widgets()
        self._justlogin = False
        
    def setup(self, infoapi):
        self._api = infoapi
        self._justlogin = True
        
    def build_actions(self):
        self.add_action('Login', self.cb_Login)
        #self.add_action('Test', self.cb_Test)
        
    def build_widgets(self):
        w, tkvar, frame = tktools.labeled_widget(self.mainframe, 'Filter:', tktools.entry)
        tkvar.trace('w', self.cb_filter_changed)
        self._tkvar_filter = tkvar
        frame.pack(fill='x')
        w, _, frame = tktools.listbox(self.mainframe, self.cb_list_select, self.cb_list_popup)
        self._listbox = w
        frame.pack(fill='both', expand=True)

    def refresh_list(self):
        self._listbox.delete(0, tk.END)
        for person in self._people:
            self._listbox.insert(tk.END, '{} ({})'.format(person['name'], person['id']))

    def show_person(self, personid):
        top = tk.Toplevel(self)
        personframe = PersonFrame(top)
        personframe.setup(self._api, personid)
        personframe.pack(fill='both', expand=True)
        
    def cb_list_select(self, event):
        selectedidx = self.get_selected()
        if selectedidx >= 0:
            person = self._people[selectedidx]
            self.show_person(person['id'])

    def get_all_people(self):
        if self._justlogin:
            self._people_all_cache = self._api.getdict('/people?projection={"name":1}')['_items']
            self._justlogin = False
        return self._people_all_cache
    
    def get_people_startswith(self, s):
        return self._api.getdict('/people?where={{"name":"startswith(\\"{}\\")"}}&projection={{"name":1}}'.format(s))['_items']

    def get_selected(self):
        selectedidxes = self._listbox.curselection()
        if len(selectedidxes) == 1:
            selectedidx = selectedidxes[0]
        else:
            selectedidx = -1
        return selectedidx
    
    def cb_filter_changed(self, *args):
        filterstr = self._tkvar_filter.get().strip()
        if filterstr == '':
            self._people = self.get_all_people()
        else:
            self._people = self.get_people_startswith(filterstr)
            print(self._people)
        self.refresh_list()
        
    def cb_list_popup(self, event):
        pass
    
    def cb_Login(self):
        d = UserPassDialog(self)
        if d.result is not None:
            self._api, self._auth = d.result
            self._justlogin = True
            self._people = self.get_all_people()
            self.refresh_list()
        
    def cb_Test(self):
        print('Test')
        
if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    urlbase = 'http://127.0.0.1:5000/'
    auth = ('mmdpdata', '123')
    infoapi = apicore.ApiCore(urlbase, auth)
    app.setup(infoapi)
    app.pack(fill='both', expand=True)
    root.title('MMDPS DMS App')
    root.mainloop()
    
