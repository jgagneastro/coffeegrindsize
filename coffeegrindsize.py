from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
import time
import pdb
stop = pdb.set_trace

#Default Parameters
def_threshold = 58.8
def_pixel_scale = 0.177
def_max_cluster_axis = 500
def_min_surface = 2
def_min_roundness = 0
def_min_x_axis = 0
def_max_x_axis = 1000
def_session_name = "JG_PSD"

class coffeegrindsize_GUI:
	def __init__(self,root):
		
		self.image_id = None
		self.scale = 1.0
		self.master = root
		
		self.master.title("Coffee Particle Size Distribution by Jonathan Gagne")
		
		#Create a toolbar
		toolbar_bg = "gray90"
		toolbar = Frame(self.master, bg=toolbar_bg)
		
		toolbar.pack(side=TOP, fill=X)
		
		self.frame_options = Frame(root)#, width=1200, height=1250
		self.frame_options.pack()
		
		#Create a status bar
		self.status_var = StringVar()
		self.status_var.set("Idle...")
		status = Label(self.master, textvariable=self.status_var, anchor=W, bg="grey", relief=SUNKEN)
		status.pack(side=BOTTOM, fill=X)
		
		#Adjustable keyword options
		self.options_row = 1
		self.width_entries = 6
		self.title_padx = 12
		
		sep1 = Label(self.frame_options, text="")
		sep1.grid(row=self.options_row)
		
		self.options_row += 1
		
		sep1 = Label(self.frame_options, text="Threshold Step:", font='Helvetica 18 bold')
		sep1.grid(row=self.options_row, sticky=W, padx=self.title_padx)

		self.options_row += 1
		
		#Options menu
		
		self.threshold_var = self.label_entry(def_threshold, "Threshold:", "%")
		
		self.label_separator()
		
		self.label_title("Particle Recognition Step:")
		
		self.pixel_scale_var = self.label_entry(def_pixel_scale, "Pixel Scale:", "mm/pix")
		
		self.max_cluster_axis_var = self.label_entry(def_max_cluster_axis, "Maximum Cluster Diameter:", "pix")
		
		self.min_surface_var = self.label_entry(def_min_surface, "Minimum Cluster Surface:", "pix^2")
		
		self.min_roundness_var = self.label_entry(def_min_roundness, "Minimum Roundness:", "")

		self.label_separator()
		
		self.label_title("Histogram Options:")
		
		self.histogram_type = StringVar(self.master)
		
		#default_choice = 'Number Fraction vs Particle Diameter'
		#choices = { 'Number Fraction vs Particle Diameter','Extracted Fraction vs Particle Surface','Surface Fraction vs Particle Surface'}
		default_choice = 'NumDiam'
		choices = { 'NumDiam', 'NumSurf'}
		self.histogram_type.set(default_choice) # set the default option
		 
		histogram_type_label = Label(self.frame_options, text="Histogram Type:")
		histogram_type_menu = OptionMenu(self.frame_options, self.histogram_type, *choices)
		histogram_type_label.grid(row=self.options_row,sticky=E)
		histogram_type_menu.grid(row=self.options_row,column=1,columnspan=2,sticky=W)
		
		# link function to change dropdown
		self.histogram_type.trace('w', self.change_dropdown_histogram_type)

		self.options_row += 1
		
		self.xmin_var = self.label_entry(def_min_x_axis, "Minimum X Axis:", "")
		
		self.xmax_var = self.label_entry(def_max_x_axis, "Maximum X Axis:", "")
		
		xlog_var = IntVar()
		xlog_var.set(1)
		checkbox1 = Checkbutton(self.frame_options, text="Logarithmic X axis",variable=xlog_var)
		checkbox1.grid(row=self.options_row,columnspan=2,sticky=E)

		self.options_row += 1
		
		self.label_separator()
		
		self.label_title("Output Options:")
		
		self.session_name_var = self.label_entry(def_session_name, "Base of File Names:", "", columnspan=2, width=self.width_entries*3)
		
		for i in range(12):
			self.label_separator()

		reset_params_button = Button(self.frame_options, text="Reset to Default Parameters", command=self.reset_status)
		reset_params_button.grid(row=self.options_row,column=0)
		self.options_row += 1

		reset_zoom_button = Button(self.frame_options, text="Reset Zoom Parameters", command=self.reset_zoom)
		reset_zoom_button.grid(row=self.options_row,column=0)

		#Canvas for image
		self.canvas_width = 1000
		self.canvas_height = 800
		image_canvas_bg = "gray40"
		self.image_canvas = Canvas(self.frame_options, width=self.canvas_width, height=self.canvas_height, bg=image_canvas_bg)
		self.image_canvas.grid(row=0,column=3,rowspan=145)

		#Prevent the image canvas to shrink when labels are placed in it
		self.image_canvas.pack_propagate(0)

		self.noimage_label = Label(self.image_canvas, text="No Image Loaded", anchor=CENTER, bg=image_canvas_bg, font='Helvetica 18 bold', width=self.canvas_width, height=self.canvas_height)
		self.noimage_label.pack(side=LEFT)

		toolbar_padx = 6
		toolbar_pady = 6
		open_image_button = Button(toolbar, text="Open Image...", command=self.open_image,highlightbackground=toolbar_bg)
		open_image_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		threshold_image_button = Button(toolbar, text="Threshold Image...", command=lambda : self.threshold_image(root),highlightbackground=toolbar_bg)
		threshold_image_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		psd_button = Button(toolbar, text="Launch Particle Recognition...", command=lambda : self.launch_psd(root),highlightbackground=toolbar_bg)
		psd_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		histogram_button = Button(toolbar, text="Create Histogram Figure...", command=lambda : self.create_histogram(root),highlightbackground=toolbar_bg)
		histogram_button.pack(side=LEFT, padx=toolbar_padx, pady=toolbar_pady)

		save_button = Button(toolbar, text="Save Data...", command=lambda : self.launch_psd(root),highlightbackground=toolbar_bg)
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
	
	def label_entry(self, default_var, text, units_text, columnspan=None, width=None):
		
		if width is None:
			width = self.width_entries
		
		data_var = StringVar()
		data_var.set(str(default_var))
		data_label = Label(self.frame_options, text=text)
		data_entry = Entry(self.frame_options, textvariable=data_var, width=width)
		data_label_units = Label(self.frame_options, text=units_text)
		data_label.grid(row=self.options_row,sticky=E)
		data_entry.grid(row=self.options_row,column=1,columnspan=columnspan)
		data_label_units.grid(row=self.options_row,column=2,sticky=W)
		
		self.options_row += 1
		
		return data_var
	
	def label_title(self, text):
		title_label = Label(self.frame_options, text=text, font='Helvetica 18 bold')
		title_label.grid(row=self.options_row, sticky=W, padx=self.title_padx)
		self.options_row += 1
	
	def label_separator(self):
		separator_label = Label(self.frame_options, text="")
		separator_label.grid(row=self.options_row)
		self.options_row += 1
	
	#Redraw image
	def redraw(self, x=0, y=0):
	        
	        if self.image_id:
	            self.image_canvas.delete(self.image_id)
	        iw, ih = self.img.size
	        size = int(iw * self.scale), int(ih * self.scale)
	        self.image_obj = ImageTk.PhotoImage(self.img.resize(size))
	        self.image_id = self.image_canvas.create_image(x, y, image=self.image_obj)
	        
	#Move image
	def move_start(self, event):
		self.image_canvas.scan_mark(event.x, event.y)
		
	def move_move(self, event):
		self.image_canvas.scan_dragto(event.x, event.y, gain=1)

	def motion(self, event):
	    self.mouse_x, self.mouse_y = event.x, event.y

	#linux zoom
	def zoomerP(self, event):
		
		#Get current coordinates of image
		image_x, image_y = self.image_canvas.coords(self.image_id)
		
		#Include effect of drag
		image_x -= self.image_canvas.canvasx(0)
		image_y -= self.image_canvas.canvasy(0)
		
		#Get original image size
		orig_nx, orig_ny = self.img.size
		
		#Determine cursor position on original image coordinates (x,y -> alpha, beta)
		mouse_alpha = orig_nx/2 + (self.mouse_x-image_x)/self.scale
		mouse_beta = orig_ny/2 + (self.mouse_y-image_y)/self.scale
		
		#Change the scale of image
		self.scale *= 2
		
		#Determine pixel position for the center of the new zoomed image
		new_image_x = self.mouse_x - (mouse_alpha - orig_nx/2)*self.scale
		new_image_y = self.mouse_y - (mouse_beta - orig_ny/2)*self.scale
		
		#Include effect of drag
		new_image_x += self.image_canvas.canvasx(0)
		new_image_y += self.image_canvas.canvasy(0)
		
		#Redraw image at the desired position
		self.redraw(x=new_image_x, y=new_image_y)
		
	def zoomerM(self, event):
		
		#Get current coordinates of image
		image_x, image_y = self.image_canvas.coords(self.image_id)
		
		#Include effect of drag
		image_x -= self.image_canvas.canvasx(0)
		image_y -= self.image_canvas.canvasy(0)
		
		#Get original image size
		orig_nx, orig_ny = self.img.size
		
		#Determine cursor position on original image coordinates (x,y -> alpha, beta)
		mouse_alpha = orig_nx/2 + (self.mouse_x-image_x)/self.scale
		mouse_beta = orig_ny/2 + (self.mouse_y-image_y)/self.scale
		
		#Change the scale of image
		self.scale *= 0.5
		
		#Determine pixel position for the center of the new zoomed image
		new_image_x = self.mouse_x - (mouse_alpha - orig_nx/2)*self.scale
		new_image_y = self.mouse_y - (mouse_beta - orig_ny/2)*self.scale
		
		#Include effect of drag
		new_image_x += self.image_canvas.canvasx(0)
		new_image_y += self.image_canvas.canvasy(0)
		
		#Redraw image at the desired position
		self.redraw(x=new_image_x, y=new_image_y)

	def pdb_call(self):
		pdb.set_trace()

	def reset_zoom(self):
		self.status_var.set("Zoom Parameters Reset to Defaults...")
		self.scale = self.original_scale
		
		#Reset the effect of dragging
		self.image_canvas.xview_moveto(0)
		self.image_canvas.yview_moveto(0)
		
		self.redraw(x=self.canvas_width/2, y=self.canvas_height/2)
		self.master.update()

	def reset_status(self):
		self.status_var.set("Parameters Reset to Defaults...")
		self.threshold_var.set(str(def_threshold))
		self.pixel_scale_var.set(str(def_pixel_scale))
		self.max_cluster_axis_var.set(str(def_max_cluster_axis))
		self.min_surface_var.set(str(def_min_surface))
		self.min_roundness_var.set(str(def_min_roundness))
		self.xmin_var.set(str(def_min_x_axis))
		self.xmax_var.set(str(def_max_x_axis))
		self.session_name_var.set(str(def_session_name))
		self.master.update()
		
	def open_image(self):
		
		#Update root to avoid problems with file dialog
		self.master.update()
		image_filename = "/Users/gagne/Documents/IDL/IDL_resources/Kinu3.4_1_sub_detection_final.png"
		
		#Do not delete
		#image_filename = filedialog.askopenfilename(initialdir="/",title="Select a PNG image",filetypes=(("png files","*.png"),("all files","*.*")))
		
		if image_filename != "":
			
			self.img = Image.open(image_filename)
			
			#Resize image to canvas size
			width_factor = self.canvas_width/self.img.size[0]
			height_factor = self.canvas_height/self.img.size[1]
			scale_factor = min(width_factor,height_factor)
			nx = round(scale_factor*self.img.size[0])
			ny = round(scale_factor*self.img.size[1])
				
			# #Resize the image
			self.image_obj = ImageTk.PhotoImage(self.img)
			
			self.noimage_label.pack_forget()
			
			self.scale = scale_factor
			self.original_scale = scale_factor
			
			self.redraw(x=self.canvas_width/2+3, y=self.canvas_height/2+3)
			
			self.status_var.set("Image opened: "+image_filename)
			self.master.update()
		
	def threshold_image(self):
		print("Not coded yet")
		for i in range(12):
			time.sleep(1)
			self.status_var.set("Iteration #"+str(i))
			self.master.update()
			
	def launch_psd(self):
		print("Not coded yet")
		
	def create_histogram(self):
		print("Not coded yet")
		
	def save_data(self):
		print("Not coded yet")
		
	def quit(self):
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