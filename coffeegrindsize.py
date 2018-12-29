from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
import time
import pdb
stop = pdb.set_trace

#Default Parameters
def_threshold = 58.8

class coffeegrindsize_GUI:
	def __init__(self,root):
		
		root.image_id = None
		root.scale = 1.0
		
		root.title("Coffee Particle Size Distribution by Jonathan Gagne")
		
		#Create a toolbar
		toolbar = Frame(root, bg="gray90")
		
		toolbar.pack(side=TOP, fill=X)
		
		frame_options = Frame(root)#, width=1200, height=1250
		frame_options.pack()
		
		#Create a status bar
		self.status_var = StringVar()
		self.status_var.set("Idle...")
		status = Label(root, textvariable=self.status_var, anchor=W, bg="grey")#, relief=SUNKEN
		status.pack(side=BOTTOM, fill=X)
		
		#Adjustable keyword options
		options_row = 1
		width_entries = 6
		title_padx = 12
		
		sep1 = Label(frame_options, text="")
		sep1.grid(row=options_row)
		
		options_row += 1
		
		sep1 = Label(frame_options, text="Threshold Step:", font='Helvetica 18 bold')
		sep1.grid(row=options_row, sticky=W, padx=title_padx)

		options_row += 1

		self.threshold_var = StringVar()
		self.threshold_var.set(str(def_threshold))
		threshold_label = Label(frame_options, text="Threshold:")
		threshold_entry = Entry(frame_options, textvariable=self.threshold_var, width=width_entries)
		threshold_label_units = Label(frame_options, text="%")
		threshold_label.grid(row=options_row,sticky=E)
		threshold_entry.grid(row=options_row,column=1)
		threshold_label_units.grid(row=options_row,column=2,sticky=W)

		options_row += 1

		sep1 = Label(frame_options, text="")
		sep1.grid(row=options_row)

		options_row += 1

		sep1 = Label(frame_options, text="Particle Recognition Step:", font='Helvetica 18 bold')
		sep1.grid(row=options_row, sticky=W, padx=title_padx)

		options_row += 1

		pixel_scale_var = StringVar()
		pixel_scale_var.set("0.177")
		pixel_scale_label = Label(frame_options, text="Pixel Scale:")
		pixel_scale_entry = Entry(frame_options, textvariable=pixel_scale_var, width=width_entries)
		pixel_scale_label_units = Label(frame_options, text="mm/pix")
		pixel_scale_label.grid(row=options_row,sticky=E)
		pixel_scale_entry.grid(row=options_row,column=1)
		pixel_scale_label_units.grid(row=options_row,column=2,sticky=W)

		options_row += 1

		max_cluster_axis_var = StringVar()
		max_cluster_axis_var.set("500")
		max_cluster_axis_label = Label(frame_options, text="Maximum Cluster Diameter:")
		max_cluster_axis_entry = Entry(frame_options, textvariable=max_cluster_axis_var, width=width_entries)
		max_cluster_axis_label_units = Label(frame_options, text="pix")
		max_cluster_axis_label.grid(row=options_row,sticky=E)
		max_cluster_axis_entry.grid(row=options_row,column=1)
		max_cluster_axis_label_units.grid(row=options_row,column=2,sticky=W)

		options_row += 1

		min_surface_var = StringVar()
		min_surface_var.set("2")
		min_surface_label = Label(frame_options, text="Minimum Cluster Surface:")
		min_surface_entry = Entry(frame_options, textvariable=min_surface_var, width=width_entries)
		min_surface_label_units = Label(frame_options, text="pix^2")
		min_surface_label.grid(row=options_row,sticky=E)
		min_surface_entry.grid(row=options_row,column=1)
		min_surface_label_units.grid(row=options_row,column=2,sticky=W)

		options_row += 1

		min_roundness_var = StringVar()
		min_roundness_var.set("0")
		min_roundness_label = Label(frame_options, text="Minimum Roundness:")
		min_roundness_entry = Entry(frame_options, textvariable=min_roundness_var, width=width_entries)
		min_roundness_label.grid(row=options_row,sticky=E)
		min_roundness_entry.grid(row=options_row,column=1)

		options_row += 1

		sep1 = Label(frame_options, text="")
		sep1.grid(row=options_row)

		options_row += 1

		sep1 = Label(frame_options, text="Histogram Options:", font='Helvetica 18 bold')
		sep1.grid(row=options_row,sticky=W, padx=title_padx)

		options_row += 1

		# Create a Tkinter variable
		self.histogram_type = StringVar(root)
		 
		# Dictionary with options
		#default_choice = 'Number Fraction vs Particle Diameter'
		#choices = { 'Number Fraction vs Particle Diameter','Extracted Fraction vs Particle Surface','Surface Fraction vs Particle Surface'}
		default_choice = 'NumDiam'
		choices = { 'NumDiam', 'NumSurf'}
		self.histogram_type.set(default_choice) # set the default option
		 
		histogram_type_label = Label(frame_options, text="Histogram Type:")
		histogram_type_menu = OptionMenu(frame_options, self.histogram_type, *choices)
		histogram_type_label.grid(row=options_row,sticky=E)
		histogram_type_menu.grid(row=options_row,column=1,columnspan=2,sticky=W)
		
		# link function to change dropdown
		self.histogram_type.trace('w', self.change_dropdown_histogram_type)

		options_row += 1

		xmin_var = StringVar()
		xmin_var.set("0")
		xmin_label = Label(frame_options, text="Minimum X Axis:")
		xmin_entry = Entry(frame_options, textvariable=xmin_var, width=width_entries)
		xmin_label.grid(row=options_row,sticky=E)
		xmin_entry.grid(row=options_row,column=1)

		options_row += 1

		xmax_var = StringVar()
		xmax_var.set("1000")
		xmax_label = Label(frame_options, text="Maximum X Axis:")
		xmax_entry = Entry(frame_options, textvariable=xmax_var, width=width_entries)
		xmax_label.grid(row=options_row,sticky=E)
		xmax_entry.grid(row=options_row,column=1)

		options_row += 1

		xlog_var = IntVar()
		xlog_var.set(1)
		checkbox1 = Checkbutton(frame_options, text="Logarithmic X axis",variable=xlog_var)
		checkbox1.grid(row=options_row,columnspan=2,sticky=E)

		options_row += 1

		sep1 = Label(frame_options, text="")
		sep1.grid(row=options_row)

		options_row += 1

		sep1 = Label(frame_options, text="Output Options:", font='Helvetica 18 bold')
		sep1.grid(row=options_row,sticky=W, padx=title_padx)

		options_row += 1

		session_name_var = StringVar()
		session_name_var.set("JG_PSD")
		session_name_label = Label(frame_options, text="Base of File Names:")
		session_name_entry = Entry(frame_options, textvariable=session_name_var, width=width_entries*3)
		session_name_label.grid(row=options_row,sticky=E)
		session_name_entry.grid(row=options_row,column=1,columnspan=2,sticky=W)

		options_row += 1

		for i in range(12):
			sep1 = Label(frame_options, text="")
			sep1.grid(row=options_row)
			options_row += 1

		button1 = Button(frame_options, text="Reset to Default Parameters", command=lambda : self.reset_status(root))

		button1.grid(row=options_row,column=2,sticky=E)

		options_row += 1

		reset_zoom_button = Button(frame_options, text="Reset Zoom Parameters", command=lambda : self.reset_zoom(root))
		reset_zoom_button.grid(row=options_row,column=2,sticky=E)

		#Canvas for image
		self.canvas_width = 1000
		self.canvas_height = 800
		image_canvas_bg = "gray40"
		self.image_canvas = Canvas(frame_options, width=self.canvas_width, height=self.canvas_height, bg=image_canvas_bg)
		self.image_canvas.grid(row=0,column=3,rowspan=145)

		#Prevent the image canvas to shrink when labels are placed in it
		self.image_canvas.pack_propagate(0)

		root.noimage_label = Label(self.image_canvas, text="No Image Loaded", anchor=CENTER, bg=image_canvas_bg, font='Helvetica 18 bold', width=self.canvas_width, height=self.canvas_height)
		root.noimage_label.pack(side=LEFT)

		toolbar_padx = 8
		toolbar_pady = 15
		open_image_button = Button(toolbar, text="Open Image...", command=lambda : self.open_image(root))
		open_image_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		threshold_image_button = Button(toolbar, text="Threshold Image...", command=lambda : self.threshold_image(root))
		threshold_image_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		psd_button = Button(toolbar, text="Launch Particle Recognition...", command=lambda : self.launch_psd(root))
		psd_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		histogram_button = Button(toolbar, text="Create Histogram Figure...", command=lambda : self.create_histogram(root))
		histogram_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		save_button = Button(toolbar, text="Save Data...", command=lambda : self.launch_psd(root))
		save_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		#Create a menu bar
		menu = Menu(root)
		root.config(menu=menu)

		#Create a FILE submenu
		subMenu = Menu(menu)
		menu.add_cascade(label="File", menu=subMenu)
		subMenu.add_command(label="Open Image...", command=lambda : self.open_image(root))
		subMenu.add_separator()
		subMenu.add_command(label="Python Debugger...", command=lambda : self.pdb_call(root))
		subMenu.add_separator()
		subMenu.add_command(label="Quit", command=quit)

		#Create zoom options
		self.image_canvas.bind('<Motion>', self.motion)

		self.image_canvas.bind("<ButtonPress-1>", self.move_start)
		self.image_canvas.bind("<B1-Motion>", self.move_move)
		#linux scroll
		self.image_canvas.bind_all("i", self.zoomerP)
		self.image_canvas.bind_all("o", self.zoomerM)
	
	# On change dropdown value
	def change_dropdown_histogram_type(self, *args):
		print(self.histogram_type.get())
	
	def label_entry(self, default_var, text, units_text):
	
		data_var = StringVar()
		data_var.set(default_var)
		data_label = Label(self.frame_options, text=text)
		data_entry = Entry(self.frame_options, textvariable=data_var, width=self.width_entries)
		data_label_units = Label(self.frame_options, text=units_text)
		data_label.grid(row=self.options_row,sticky=E)
		data_entry.grid(row=self.options_row,column=1)
		data_label_units.grid(row=self.options_row,column=2,sticky=W)
		
		self.options_row += 1
	
	#Redraw image
	def redraw(self, master, x=0, y=0):
	        
	        if master.image_id:
	            self.image_canvas.delete(master.image_id)
	        iw, ih = master.img.size
	        size = int(iw * master.scale), int(ih * master.scale)
	        master.image_obj = ImageTk.PhotoImage(master.img.resize(size))
	        master.image_id = self.image_canvas.create_image(x, y, image=master.image_obj)
	        
	#Move image
	def move_start(self, event):
		self.image_canvas.scan_mark(event.x, event.y)
		
	def move_move(self, event):
		self.image_canvas.scan_dragto(event.x, event.y, gain=1)

	def motion(self, event):
	    root.mouse_x, root.mouse_y = event.x, event.y

	#linux zoom
	def zoomerP(self, event):
		
		#Get current coordinates of image
		image_x, image_y = self.image_canvas.coords(root.image_id)
		
		#Include effect of drag
		image_x -= self.image_canvas.canvasx(0)
		image_y -= self.image_canvas.canvasy(0)
		
		#Get original image size
		orig_nx, orig_ny = root.img.size
		
		#Determine cursor position on original image coordinates (x,y -> alpha, beta)
		mouse_alpha = orig_nx/2 + (root.mouse_x-image_x)/root.scale
		mouse_beta = orig_ny/2 + (root.mouse_y-image_y)/root.scale
		
		#Change the scale of image
		root.scale *= 2
		
		#Determine pixel position for the center of the new zoomed image
		new_image_x = root.mouse_x - (mouse_alpha - orig_nx/2)*root.scale
		new_image_y = root.mouse_y - (mouse_beta - orig_ny/2)*root.scale
		
		#Include effect of drag
		new_image_x += self.image_canvas.canvasx(0)
		new_image_y += self.image_canvas.canvasy(0)
		
		#Redraw image at the desired position
		self.redraw(root, x=new_image_x, y=new_image_y)
		
	def zoomerM(self, event):
		
		#Get current coordinates of image
		image_x, image_y = self.image_canvas.coords(root.image_id)
		
		#Include effect of drag
		image_x -= self.image_canvas.canvasx(0)
		image_y -= self.image_canvas.canvasy(0)
		
		#Get original image size
		orig_nx, orig_ny = root.img.size
		
		#Determine cursor position on original image coordinates (x,y -> alpha, beta)
		mouse_alpha = orig_nx/2 + (root.mouse_x-image_x)/root.scale
		mouse_beta = orig_ny/2 + (root.mouse_y-image_y)/root.scale
		
		#Change the scale of image
		root.scale *= 0.5
		
		#Determine pixel position for the center of the new zoomed image
		new_image_x = root.mouse_x - (mouse_alpha - orig_nx/2)*root.scale
		new_image_y = root.mouse_y - (mouse_beta - orig_ny/2)*root.scale
		
		#Include effect of drag
		new_image_x += self.image_canvas.canvasx(0)
		new_image_y += self.image_canvas.canvasy(0)
		
		#Redraw image at the desired position
		self.redraw(root, x=new_image_x, y=new_image_y)

	def pdb_call(self, master):
		pdb.set_trace()

	def reset_zoom(self, master):
		self.status_var.set("Zoom Parameters Reset to Defaults...")
		master.scale = master.original_scale
		
		#Reset the effect of dragging
		self.image_canvas.xview_moveto(0)
		self.image_canvas.yview_moveto(0)
		
		self.redraw(master, x=self.canvas_width/2, y=self.canvas_height/2)
		master.update()

	def reset_status(self, master):
		self.status_var.set("Parameters Reset to Defaults...")
		self.threshold_var.set(str(def_threshold))
		master.update()
		
	def open_image(self, master):
		
		#Update root to avoid problems with file dialog
		master.update()
		image_filename = "/Users/gagne/Documents/IDL/IDL_resources/Kinu3.4_1_sub_detection_final.png"
		
		#Do not delete
		#image_filename = filedialog.askopenfilename(initialdir="/",title="Select a PNG image",filetypes=(("png files","*.png"),("all files","*.*")))
		
		if image_filename != "":
			
			master.img = Image.open(image_filename)
			
			#Resize image to canvas size
			width_factor = self.canvas_width/master.img.size[0]
			height_factor = self.canvas_height/master.img.size[1]
			scale_factor = min(width_factor,height_factor)
			nx = round(scale_factor*master.img.size[0])
			ny = round(scale_factor*master.img.size[1])
				
			# #Resize the image
			master.image_obj = ImageTk.PhotoImage(master.img)
			
			master.noimage_label.pack_forget()
			
			master.scale = scale_factor
			master.original_scale = scale_factor
			
			#Set a scanning anchor for drawing of image
			master.scanning_anchor_x = 0
			master.scanning_anchor_y = 0
			
			self.redraw(master, x=self.canvas_width/2+3, y=self.canvas_height/2+3)
			
			self.status_var.set("Image opened: "+image_filename)
			master.update()
		
	def threshold_image(self, master):
		print("Not coded yet")
		for i in range(12):
			time.sleep(1)
			self.status_var.set("Iteration #"+str(i))
			master.update()
			
	def launch_psd(self, master):
		print("Not coded yet")
		
	def create_histogram(self, master):
		print("Not coded yet")
		
	def save_data(self, master):
		print("Not coded yet")
		
	def quit(self, master):
		print("Not coded yet")
		pdb.set_trace()

#Main loop and call to the GUI
root = Tk()
coffeegrindsize_GUI(root)
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass