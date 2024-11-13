from tkinter import *
import ttk

root = Tk()



tree = ttk.Treeview(root)

tree["columns"]=("one","two")
tree.heading("one", text="coulmn A")
tree.heading("two", text="column B")

tree.insert("", 3, "dir3", text="Dir 3",values=("3A"," 3B"))
tree.insert("dir3", 3, 'subdir3', text="sub dir 3", values=("3A"," 3B"))

tree.bind("<Double-1>",)


tree.pack()
root.mainloop()