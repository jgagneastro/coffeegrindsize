from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
import time
import pdb
stop = pdb.set_trace

#Default Parameters
def_threshold = 58.8


root = Tk()

root.image_id = None
root.scale = 1.0

root.title("Coffee Particle Size Distribution by Jonathan Gagne")

# class psdButton:
	
# 	def __init__(self, master):
# 		frame = Frame(master)
# 		frame.pack()
		
# 		self.printButton = Button(frame, text="Message", command=self.printMessage)
# 		self.printButton.pack(side=LEFT)

#Redraw image
def redraw(master, x=0, y=0):
        if master.image_id:
            image_canvas.delete(master.image_id)
        iw, ih = master.img.size
        size = int(iw * master.scale), int(ih * master.scale)
        master.image_obj = ImageTk.PhotoImage(master.img.resize(size))
        master.image_id = image_canvas.create_image(x, y, image=master.image_obj)

        # tell the canvas to scale up/down the vector objects as well
        image_canvas.scale(ALL, x, y, master.scale, master.scale)

#move
def move_start(event):
	image_canvas.scan_mark(event.x, event.y)
def move_move(event):
	image_canvas.scan_dragto(event.x, event.y, gain=1)

#windows zoom
#def zoomer(event):
#	if (event.delta > 0):
#		image_canvas.scale("all", event.x, event.y, 1.1, 1.1)
#	elif (event.delta < 0):
#		image_canvas.scale("all", event.x, event.y, 0.9, 0.9)
#	image_canvas.configure(scrollregion = image_canvas.bbox("all"))

#linux zoom
def zoomerP(event):
	root.scale *= 2
	redraw(root, x=event.x, y=event.y)
	#photo = photo.zoom(x=scale, y=scale)
	#image_canvas.resize("all", event.x, event.y, 1.1, 1.1)
	#image_canvas.configure(scrollregion = image_canvas.bbox("all"))
def zoomerM(event):
	root.scale *= 0.5
	redraw(root, x=event.x, y=event.y)
	#print("BLABLA2")
	#image_canvas.scale("all", event.x, event.y, 0.9, 0.9)
	#image_canvas.configure(scrollregion = image_canvas.bbox("all"))

def pdb_call(master):
	pdb.set_trace()

def reset_zoom(master):
	status_var.set("Zoom Parameters Reset to Defaults...")
	master.scale = 1
	redraw(master, x=0, y=0)
	master.image_id = image_canvas.create_image(3, 3, anchor=NW, image=master.image_obj)
	#image_canvas.scan_dragto(0, 0, gain=1)
	master.update()

def reset_status(master, status_var):
	status_var.set("Parameters Reset to Defaults...")
	threshold_var.set(str(def_threshold))
	master.update()
	
def open_image(master,image_canvas):
	#Update root to avoid problems with file dialog
	master.update()
	image_filename = filedialog.askopenfilename(initialdir="/",title="Select a PNG image",filetypes=(("png files","*.png"),("all files","*.*")))
	if image_filename != "":
		
		master.img = Image.open(image_filename)
		
		#Resize image to canvas size
		width_factor = canvas_width/master.img.size[0]
		height_factor = canvas_height/master.img.size[1]
		scale_factor = min(width_factor,height_factor)
		nx = round(scale_factor*master.img.size[0])
		ny = round(scale_factor*master.img.size[1])
		
		master.img = master.img.resize((nx,ny), Image.ANTIALIAS)
		master.image_obj = ImageTk.PhotoImage(master.img)
		
		master.image_id = image_canvas.create_image(3, 3, anchor=NW, image=master.image_obj)
		status_var.set("Image opened: "+image_filename)
		master.update()
	
def threshold_image(master):
	#Update root to avoid problems with file dialog
	print("Not coded yet")
	for i in range(12):
		time.sleep(1)
		status_var.set("Iteration #"+str(i))
		master.update()
		

def launch_psd(master):
	#Update root to avoid problems with file dialog
	print("Not coded yet")
	
def create_histogram(master):
	#Update root to avoid problems with file dialog
	print("Not coded yet")
	
def save_data(master):
	#Update root to avoid problems with file dialog
	print("Not coded yet")
	
def quit():
	print("Not coded yet")
	pdb.set_trace()

# label1 = Label(root,text="Bla")
# label1.pack()

# frame_up = Frame(root)
# frame_up.pack()
# frame_down = Frame(root)
# frame_down.pack(side=BOTTOM)

# button1 = Button(frame_up, text="Button 1", fg="red")
# button2 = Button(frame_up, text="Button 2", fg="blue")

# button1.pack(side=LEFT)
# button2.pack()

#Create a toolbar

toolbar = Frame(root, bg="gray90")

#open_image_button = Button(toolbar, text="Open Image...", command=lambda : open_image(root))
#open_image_button.pack(side=LEFT, padx=0, pady=0)

toolbar.pack(side=TOP, fill=X)

frame_up = Frame(root)#, width=1200, height=1250
frame_up.pack()

#Create a status bar

status_var = StringVar()
status_var.set("Idle...")
status = Label(root, textvariable=status_var, anchor=W, bg="grey")#, relief=SUNKEN
status.pack(side=BOTTOM, fill=X)

#Adjustable keyword options
options_row = 1
width_entries = 6
title_padx = 12

sep1 = Label(frame_up, text="")
sep1.grid(row=options_row)

options_row += 1

sep1 = Label(frame_up, text="Threshold Step:", font='Helvetica 18 bold')
sep1.grid(row=options_row, sticky=W, padx=title_padx)

options_row += 1

threshold_var = StringVar()
threshold_var.set(str(def_threshold))
threshold_label = Label(frame_up, text="Threshold:")
threshold_entry = Entry(frame_up, textvariable=threshold_var, width=width_entries)
threshold_label_units = Label(frame_up, text="%")
threshold_label.grid(row=options_row,sticky=E)
threshold_entry.grid(row=options_row,column=1)
threshold_label_units.grid(row=options_row,column=2,sticky=W)

options_row += 1

sep1 = Label(frame_up, text="")
sep1.grid(row=options_row)

options_row += 1

sep1 = Label(frame_up, text="Particle Recognition Step:", font='Helvetica 18 bold')
sep1.grid(row=options_row, sticky=W, padx=title_padx)

options_row += 1

pixel_scale_var = StringVar()
pixel_scale_var.set("0.177")
pixel_scale_label = Label(frame_up, text="Pixel Scale:")
pixel_scale_entry = Entry(frame_up, textvariable=pixel_scale_var, width=width_entries)
pixel_scale_label_units = Label(frame_up, text="mm/pix")
pixel_scale_label.grid(row=options_row,sticky=E)
pixel_scale_entry.grid(row=options_row,column=1)
pixel_scale_label_units.grid(row=options_row,column=2,sticky=W)

options_row += 1

max_cluster_axis_var = StringVar()
max_cluster_axis_var.set("500")
max_cluster_axis_label = Label(frame_up, text="Maximum Cluster Diameter:")
max_cluster_axis_entry = Entry(frame_up, textvariable=max_cluster_axis_var, width=width_entries)
max_cluster_axis_label_units = Label(frame_up, text="pix")
max_cluster_axis_label.grid(row=options_row,sticky=E)
max_cluster_axis_entry.grid(row=options_row,column=1)
max_cluster_axis_label_units.grid(row=options_row,column=2,sticky=W)

options_row += 1

min_surface_var = StringVar()
min_surface_var.set("2")
min_surface_label = Label(frame_up, text="Minimum Cluster Surface:")
min_surface_entry = Entry(frame_up, textvariable=min_surface_var, width=width_entries)
min_surface_label_units = Label(frame_up, text="pix^2")
min_surface_label.grid(row=options_row,sticky=E)
min_surface_entry.grid(row=options_row,column=1)
min_surface_label_units.grid(row=options_row,column=2,sticky=W)

options_row += 1

min_roundness_var = StringVar()
min_roundness_var.set("0")
min_roundness_label = Label(frame_up, text="Minimum Roundness:")
min_roundness_entry = Entry(frame_up, textvariable=min_roundness_var, width=width_entries)
min_roundness_label.grid(row=options_row,sticky=E)
min_roundness_entry.grid(row=options_row,column=1)


options_row += 1

sep1 = Label(frame_up, text="")
sep1.grid(row=options_row)

options_row += 1

sep1 = Label(frame_up, text="Histogram Options:", font='Helvetica 18 bold')
sep1.grid(row=options_row,sticky=W, padx=title_padx)

options_row += 1

# Create a Tkinter variable
histogram_type = StringVar(root)
 
# Dictionary with options
#default_choice = 'Number Fraction vs Particle Diameter'
#choices = { 'Number Fraction vs Particle Diameter','Extracted Fraction vs Particle Surface','Surface Fraction vs Particle Surface'}
default_choice = 'NumDiam'
choices = { 'NumDiam', 'NumSurf'}
histogram_type.set(default_choice) # set the default option
 
histogram_type_label = Label(frame_up, text="Histogram Type:")
histogram_type_menu = OptionMenu(frame_up, histogram_type, *choices)
histogram_type_label.grid(row=options_row,sticky=E)
histogram_type_menu.grid(row=options_row,column=1,columnspan=2,sticky=W)
 
# On change dropdown value
def change_dropdown_histogram_type(*args):
    print(histogram_type.get())
 
# link function to change dropdown
histogram_type.trace('w', change_dropdown_histogram_type)

options_row += 1

xmin_var = StringVar()
xmin_var.set("0")
xmin_label = Label(frame_up, text="Minimum X Axis:")
xmin_entry = Entry(frame_up, textvariable=xmin_var, width=width_entries)
xmin_label.grid(row=options_row,sticky=E)
xmin_entry.grid(row=options_row,column=1)

options_row += 1

xmax_var = StringVar()
xmax_var.set("1000")
xmax_label = Label(frame_up, text="Maximum X Axis:")
xmax_entry = Entry(frame_up, textvariable=xmax_var, width=width_entries)
xmax_label.grid(row=options_row,sticky=E)
xmax_entry.grid(row=options_row,column=1)

options_row += 1

xlog_var = IntVar()
xlog_var.set(1)
checkbox1 = Checkbutton(frame_up, text="Logarithmic X axis",variable=xlog_var)
checkbox1.grid(row=options_row,columnspan=2,sticky=E)

options_row += 1

sep1 = Label(frame_up, text="")
sep1.grid(row=options_row)

options_row += 1

sep1 = Label(frame_up, text="Output Options:", font='Helvetica 18 bold')
sep1.grid(row=options_row,sticky=W, padx=title_padx)

options_row += 1

session_name_var = StringVar()
session_name_var.set("JG_PSD")
session_name_label = Label(frame_up, text="Base of File Names:")
session_name_entry = Entry(frame_up, textvariable=session_name_var, width=width_entries*3)
session_name_label.grid(row=options_row,sticky=E)
session_name_entry.grid(row=options_row,column=1,columnspan=2,sticky=W)

options_row += 1


for i in range(12):
	sep1 = Label(frame_up, text="")
	sep1.grid(row=options_row)
	options_row += 1

button1 = Button(frame_up, text="Reset to Default Parameters", command=lambda : reset_status(root, status_var))
#button1.bind("<Button-1>",print_name)
button1.grid(row=options_row,column=0)

options_row += 1

reset_zoom_button = Button(frame_up, text="Reset Zoom Parameters", command=lambda : reset_zoom(root))
reset_zoom_button.grid(row=options_row,column=0)

#reset_zoom

#Canvas for image
canvas_width = 1000
canvas_height = 800
#xpad = 10
#ypad = 10
image_canvas_bg = "gray40"
image_canvas = Canvas(frame_up, width=canvas_width, height=canvas_height, bg=image_canvas_bg)
image_canvas.grid(row=0,column=3,rowspan=145)

#Prevent the image canvas to shrink when labels are placed in it
image_canvas.pack_propagate(0)
#blackline = canvas.create_line(xpad,ypad,canvas_width,ypad)

if hasattr(root, "image_obj"):
	image_canvas.create_image(0, 0, anchor=NW, image=root.image_obj)
else:
	no_image_label = Label(image_canvas, text="No Image Loaded", anchor=CENTER, bg=image_canvas_bg, font='Helvetica 18 bold', width=canvas_width, height=canvas_height)
	no_image_label.pack(side=LEFT)

toolbar_padx = 8
toolbar_pady = 15
open_image_button = Button(toolbar, text="Open Image...", command=lambda : open_image(root, image_canvas))
open_image_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

threshold_image_button = Button(toolbar, text="Threshold Image...", command=lambda : threshold_image(root))
threshold_image_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

psd_button = Button(toolbar, text="Launch Particle Recognition...", command=lambda : launch_psd(root))
psd_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

histogram_button = Button(toolbar, text="Create Histogram Figure...", command=lambda : create_histogram(root))
histogram_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

save_button = Button(toolbar, text="Save Data...", command=lambda : launch_psd(root))
save_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

#if hasattr(root, "image_obj"):
#	image_canvas.create_image(0, 0, anchor=NW, image=master.image_obj)

#Create a menu bar
menu = Menu(root)
root.config(menu=menu)

#Create a FILE submenu
subMenu = Menu(menu)
menu.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open Image...", command=lambda : open_image(root,image_canvas))
subMenu.add_separator()
subMenu.add_command(label="Python Debugger...", command=lambda : pdb_call(root))
subMenu.add_separator()
subMenu.add_command(label="Quit", command=quit)

#Create zoom options
image_canvas.bind("<ButtonPress-1>", move_start)
image_canvas.bind("<B1-Motion>", move_move)
#linux scroll
image_canvas.bind_all("i", zoomerP)
image_canvas.bind_all("o", zoomerM)
#windows scroll
#image_canvas.bind("<MouseWheel>",zoomer)

while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass

#root.mainloop()

#root.update()
#root.filename = filedialog.askopenfilename(initialdir="/",title="Select a PNG image",filetypes=(("png files","*.png"),("all files","*.*")))

#image_file = root.filename#"/Users/gagne/Documents/Postdoc/Coffee_Stuff/Grind_Size/Kinu_Victor/Kinu3.4_1_sub.png"
#image_obj = ImageTk.PhotoImage(Image.open(image_file))

#canvas.create_image(0, 0, anchor=NW, image=image_obj)

#photo = PhotoImage(file="/Users/gagne/Documents/Postdoc/Coffee_Stuff/Grind_Size/Kinu_Victor/Kinu3.4_1_sub.png")
#photo_label = Label(canvas, image=photo)
#photo_label.pack()

#root.mainloop()