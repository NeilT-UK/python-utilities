""" class to use as a general purpose GUI input widget
and a few convenience functions for validating data inputs
"""

"""
Copyright (c) <2014>, <Neil Thomas>, <NeilT-UK>, <dc_fm@hotmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the FreeBSD Project.
"""

# works with Python 3.4
# should work with Python 2.7

try:
    # Python 3 spelling
    import tkinter as tki
    import tkinter.messagebox as tkm
    import tkinter.filedialog as tkf
except ImportError:
    # Python 2 spelling
    import Tkinter as tki
    import tkMessageBox as tkm
    import tkFileDialog as tkf
import json

class EntryLine(tki.Frame):
    """ a combination of label, entry and help button, for validated gui entry of data"""
    def __init__(self, parent, text='no label', data='', conv=None, update=None, width=15, default=None):
        """ text    optional    used to label the entry
        
            data    optional    used to initialise the Entry box
                                uses empty string if none supplied
        
            conv    optional    conversion function, which also validates the entry
                                note that int, float and str can be used
                                return string unchanged (str) if omitted or None
                                conv must return object if entry is valid
                                its __doc__ string is available as help
                                if the docstring starts with [x], x is put on the help button
                                (TODO have to work on tooltips sometime!)
                                raise ValueError if the entry is invalid (int, float and str do this)
                                The err from ValueError is saved for the help button
                                so more info can be given about failure to validate

            update  optional    the name of the function to call when entries are updated
                                needed for the execute when all valid functionality

            width   optional    defaults to 15, maybe should make this adaptive sometime

            default optional    defaults to None
                                returns if the text string produces an invalid result
                                allows .get() to be called asynchronously, and return valid
                                results to the calling program

        """
        tki.Frame.__init__(self, master=parent) # tki refuses to work with super!
        self.update = update
        self.conv = conv
        self.text = text
        self.default = default
        
        # init the properties
        self.err = ''
        self.value = None
        self.valid = False
        
        # do the label
        self.label = tki.Label(self, text=text, width=width)
        self.label.grid(row=0, column=0)

        # do the conversion function
        cdoc = conv.__doc__  # easier to type
        if conv:
            # we have a conversion function specified
            # is it one of the builtins?
            if conv == int:
                help_face = 'i'
                self.conv_help = 'builtin int() function'
            elif conv == float:
                help_face = 'f'
                self.conv_help = 'builtin float() function'
            elif conv == str:
                help_face = 'str'
                self.conv_help = 'builtin str() function'
            else:
                # none of those, so does it have a docstring?
                if cdoc:
                    # yes, does it start with a help_face?
                    face_end = cdoc.find(']')
                    if (cdoc[0] == '[') and (face_end != -1) and (face_end < 6):
                        help_face = cdoc[1:face_end]
                    else:
                        help_face = '?'
                    # is the help prompt truncated in the docstring?
                    if '[end_help]' in cdoc:
                        self.conv_help = cdoc[:cdoc.find('[end_help]')]
                    else:
                        self.conv_help = cdoc
                    # this could be done by knowing .find() returns -1 if not found
                    # and slicing [;find()] regardless
                    # but that's bordering on the tricky, this is clearer
                else:
                    self.conv_help = 'no documentation\navailable for\nthis conversion'
                    help_face = '?'
        else:
            self.conv = str
            help_face = 'str'
            self.conv_help = 'returned as string'

        # do the entry
        self.var = tki.StringVar()
        self.entry = tki.Entry(self, textvariable=self.var, width=width)
        self.entry.grid(row=0, column=1)
        self.var.trace('w', self._changed)
        self.entry.bind('<Return>', self._returned)

        # do the help button
        self.help_but = tki.Button(self,
                                   text=help_face,
                                   command=self._show_help,
                                   width=5,
                                   takefocus=0) # don't take part in tab-focus
                                                # took a while to figure this out
        self.help_but.grid(row=0, column=2)

        # initialise it, which triggers the trace, _changed and validation
        self.var.set(str(data))

    def _returned(self, *args):
        self.update(enter=True)

    def _show_help(self):
        tkm.showinfo('conversion information', '{}\n{}'.format(self.conv_help, self.err))

    def _changed(self, *args):
        ent_val = self.var.get()
        self.val_string = ent_val
        try:
            self.value = self.conv(ent_val)
            self.entry.config(bg='white')
            self.err = ''
            self.valid = True
        except ValueError as err:
            try:
                self.value = self.conv(self.default)   # we convert the default value
            except (TypeError, ValueError):
                self.value = self.default   # which if it can't be converted (None) is returned intact
            self.entry.config(bg='orange')
            self.err = err
            self.valid = False
        self.update()

    def put(self, value):
        """ allows the client to change the displayed value"""
        self.var.set(value)

class GUI_inputs(tki.LabelFrame):
    """ A GUI data input convenience class, with tab-able fields and verified data"""
    def __init__(self, parent, text="Neil's Input Widget", execute=None,
                                                           exec_label='execute',
                                                           loadsave=None,
                                                           **kwargs):
        """ initialise with text for the LabelFrame

            set execute to the name of a function to be called on execute
            execute button greyed out until all entries are valid
            
            set loadsave=True to put up load/save buttons
        """
        tki.LabelFrame.__init__(self, master=parent, text=text)
        self.kwargs = kwargs        

        # we have a dict of entries
        self.entries = {}    # the data entry widgets
        self.row = 0
       
        # if there's a execute supplied, put up a button for it, on the last row
        self.execute_func = execute
        self.exec_label = exec_label
        if execute:
            # an execute button
            self.execute_but = tki.Button(self, text=self.exec_label,
                                           command=self.execute_func,
                                           state=tki.DISABLED)
            self.execute_but.grid(row=99, column=1) #MAXROWS anyone?
            # a tick box for the enter binding
            self.exec_ent_var = tki.IntVar()
            self.exec_check = tki.Checkbutton(self, text='exec on enter', variable=self.exec_ent_var)
            self.exec_check.grid(row=99, column=0)

        # if we want load/save functionality, True for current path
        if loadsave:
            self.load_but = tki.Button(self, text='load', command=self._load_func)
            self.load_but.grid(row=100, column=0)
            self.save_but = tki.Button(self, text='save', command=self._save_func)
            self.save_but.grid(row=100, column=1)
            

    def add(self, key, disp_name='', data='', conv=None, default=None):
        """ add a new data entry line to the input widget

        key         required    key for the entry, must be unique on this widget
                                the returned dict uses this as the key
                                use a string, but other objects do work as well
                                
        disp_name   optional    labels the data entry, uses the key if omitted

        data        optional    initial string data for the entry box

        conv        optional    A function, that takes a string, returns an object
                                or raises ValueError if it can't understand the string
                                int and float do this

        default     optional    When GUI_inputs is the client, execute is always greyed
                                if there are any invalid entries. However as a server,
                                .get() might be called when entries are invalid. Default
                                provides a default response for invalid entries, to avoid
                                the calling program having to try: all return values                                    
        """

        if key in self.entries:
            raise ValueError('duplicate key name >>>{}<<<'.format(key))

        if not disp_name:
            disp_name = str(key)

        mle = EntryLine(self, disp_name, data, conv, self.update, default=default, **self.kwargs)
        mle.grid(row=self.row, column=0, columnspan=2)
        self.row += 1
        self.entries[key] = mle
        

    def _load_func(self):
        """ read a json encoded list of tuples
        update the GUI with the entries
        warn if there are too many or too few
        If a tuple contains only two data, assume to be key and value"""

        load_name = tkf.askopenfilename(filetypes = [('JSON files', '.json'), ('all files', '.*')])
        if load_name:
            with open(load_name, 'rt') as load_file:
                updates = json.load(load_file)

            # make a dict with what to update, and what to update it with
            # maybe there should be more error checking here
            # but printing out what gets used and not, into a gui, gives you a chance
            try:
                src_keys = [x[0] for x in updates]
                data = [x[-1] for x in updates]
            except IndexError:
                print("can't understand the load data file, are all fields present?")
                return
            src_dict = dict(zip(src_keys, data))
            
            dst_keys = self.entries.keys()
            
            # using sets to do this is a bit more elegant and explicit than
            # looping and testing over both sets of keys
            can_update = set(src_keys) & set(dst_keys)
            not_updated = set(dst_keys).difference(src_keys)
            not_used = set(src_keys).difference(dst_keys)

            for key in can_update:
                self.set_data(key, src_dict[key])
                print('"{}" was updated to "{}"'.format(key, src_dict[key]))
            for key in not_updated:
                print('Warning - "{}" found on GUI but not in load file, not updated'.format(key))
            for key in not_used:
                print('Warning - "{}" found in load file but not on GUI, not used'.format(key))

    def _save_func(self):
        """ put a list of (key, display_name, value_string) tuples
        into a json encoded file, or into the shell window if no file is specified

        'key' is effectively the variable name used in the code
        'display_name' is for documentation on save, ignored on load
        'value_string' is whatever is present, whether valid or not"""

        # retrieve and format the data
        keys = self.entries.keys()
        names = [x.text for x in self.entries.values()]
        data = [x.val_string for x in self.entries.values()]
        save_stuff = list(zip(keys, names, data)) # zip returns an iterator in python3!

        save_name = tkf.asksaveasfilename(filetypes = [('JSON files', '.json'), ('all files', '.*')])
        if save_name:         
            if not ('.' in save_name):
                save_name += '.json'
            with open(save_name, 'wt') as save_file:
                json.dump(save_stuff, save_file)
        else:
            print(save_stuff)
        


    def update(self, enter=False):
        """ called when something has changed, or enter has been hit
        this is a clumsy interface, not sure its well thought out
        in fact it confused me when I returned to the code
        but now I think I know what's going on"""
        # only need to worry about this when there's a execute button to handle
        if self.execute_func:
            # get the valid properties of each entry
            valids = [x.valid for x in self.entries.values()]
            if all(valids):
                self.execute_but.config(state=tki.NORMAL)
                if enter and (self.exec_ent_var.get() == 1):
                    self.execute_func()
            else:
                self.execute_but.config(state=tki.DISABLED)            

    def get(self):
        """ return a dict of the converted results"""
        output = dict(zip(self.entries.keys(), [x.value for x in self.entries.values()]))
        return output
    
    def set_data(self, key, data):
        """ set the entry field of 'key' to data"""
        self.entries[key].put(data)

# conversion functions, for example, and to be used by the application      

def float_pair(x):
    """[f,f] Two floats seperated by a comma
    [end_help]

    example non-trivial conversion function
    not all of docstring intended to be displayed as help
    throw ValueError from two locations, one from split, one from float
    return a list of the values
    """
    fields = x.split(',')
    if len(fields) != 2:
        raise ValueError('need two fields seperated by one comma')
    output = []
    for field in fields:        # float() will ValueError if it's wrong 
        output.append(float(field))
    return output

def list_of_floats(x):
    """[lof] list of floats
    One float, or several floats separated by commas"""

    # try to eliminate the simplest problem
    if ',' in x:
        if x.rstrip()[-1] == ',':
            raise ValueError('no final value')

    out = []
    fields = x.split(',')          # this will always work without error
    for field in fields:
        out.append(float(field))   # and float() will ValueError if it 
    return out                     # doesn't understand the string                    







if __name__ == '__main__':

    def execute_func():
        # get data in converted form from the widgets
        print('executing with')
        print( full.get(), basic.get())
        # show updating data on the forms
        try:
            execute_func.count += 1
        except Exception:
            execute_func.count = 0
        basic.set_data('key 1', '{}'.format(execute_func.count))

    # define additional conversion functions in the calling application

    def int16(x):
        """[16] a base16 (hexadecimal) integer"""
        return int(x, base=16)

    def cryptic_conv(x):
        # there happens to be no docstring for this conversion function
        return int(x)
   
    root = tki.Tk()
    
    basic = GUI_inputs(root)
    basic.pack()
    basic.add('key 1')
    basic.add('key 2')
   
    full = GUI_inputs(root, 'full fat', execute=execute_func, loadsave=True, width=20)
    full.pack()
    full.add('examp 1')
    full.add('we1', conv=str, data=3)
    full.add('an int', conv=int, default=7)
    full.add('we2', 'disp4we2', data=999)
    full.add('pair', 'f_pair', '3,4', float_pair, default='7,8' )
    full.add('adr', 'hex address', '0xC0DE', int16)
    full.add('float_list', 'float list', '3, 4, 5', list_of_floats, )
    full.add('cryp', 'no doc string', 6, cryptic_conv)

    get_but = tki.Button(root, text='force get', command=execute_func)
    get_but.pack()

    root.mainloop()
        
        
