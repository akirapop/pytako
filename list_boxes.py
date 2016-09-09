import tkinter as tk


class ScrolledListbox(tk.Frame):

     def __init__(self, entries=None, master=None):
         tk.Frame.__init__(self, master)
         self.pack(side=tk.LEFT)

         self.list_box=self._make_listbox(entries) 
         self.list_box.pack(side=tk.LEFT)

     def configure(self, **kwds):
         self.list_box.configure(kwds)

     def get_all(self):
         return "\n".join(self.list_box.get(0,tk.END))

     def get_index_and_selection(self):
         selection=self.list_box.curselection()
         value = self.list_box.get(selection[0])

         return selection[0], value

     def get_selection(self):
         selection=self.list_box.curselection()
         value = self.list_box.get(selection[0])

         return value

     def add_item(self, item):
         self.list_box.insert(tk.END, item)
 
     def _make_listbox(self, entries=None):

         vs= tk.Scrollbar(self, orient=tk.VERTICAL)
         hs= tk.Scrollbar(self, orient=tk.HORIZONTAL)

         lbox=tk.Listbox(self, xscrollcommand=hs.set, yscrollcommand=vs.set)
         vs.config(command=lbox.yview)
         hs.config(command=lbox.xview)

         vs.pack(side=tk.RIGHT, fill=tk.Y)
         hs.pack(side=tk.BOTTOM, fill=tk.X)

         if entries is not None:
             for e in entries:
                 lbox.insert(tk.END, e) 
         return lbox

     def make_binding(self, bindcmd):
         self.list_box.bind("<Double-Button-1>", bindcmd)

