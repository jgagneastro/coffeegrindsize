#Import the required packages
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
import time
import numpy as np
import webbrowser
import pandas as pd
import os

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.ticker as mticker
from matplotlib import path

#Set thick axes
from matplotlib import rc
rc("axes", linewidth=2)
#from pylab import gca

#Set latex fonts
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
#rc('text', usetex=True)

#Temporary for debugging purposes
import pdb
stop = pdb.set_trace

# === Default Parameters for analysis and plotting ===

#Default value for image thresholding (%)
def_threshold = 58.8

#Default value for the pixel scale (pixels/millimeters)
def_pixel_scale = None

#Default value for the maximum diameter of a single cluster (pixels)
#Smaller values will speed up the code slightly
def_max_cluster_axis = 100

#Default value for the minimum surface of a cluster (pixels squared)
def_min_surface = 5

#Default value for the minimum roundness of a cluster (no units)
#Roundness is defined as the ratio of cluster to all pixels in the smallest circle that encompasses all pixels of a cluster
def_min_roundness = 0

#Default X axis range for the histogram (variable units)
def_min_x_axis = 0.01
def_max_x_axis = 10

#Default name for the session (used for output filenames)
def_session_name = "PSD_"+time.strftime("%Y%m%d_%Hh%Mm%Ss")

original_image_display_name = "Original"
threshold_image_display_name = "Thresholded"
outlines_image_display_name = "Cluster Outlines"
histogram_image_display_name = "Histograms"

#Default sizes for histogram bins
default_log_binsize = 0.05
default_binsize = 0.1

#List of reference objects with their diameters in millimeters
reference_objects_dict = {"Custom":None, "Canadian Quarter":23.81, "Canadian Dollar":26.5, "Canadian Dime":18.03, "US Quarter":24.26, "US Dollar":26.92, "US Dime":17.91}

#Default output directory
def_output_dir = os.path.expanduser("~")

#Python class for comparison data
class Comparison:
	def __init__(self, **kwds):
		
		#This variable will add some required dictionary values
		self.__dict__.update(kwds)

#Python class for the user interface window
class coffeegrindsize_GUI:
	
	#Actions to be taken on initialization of user interface window
	def __init__(self, root):
		
		# === Set some object variables that will not be garbage collected ===
		
		#This variable contains the output directory
		self.output_dir = def_output_dir
		
		#This variable will contain the object of the image currently displayed
		self.image_id = None
		
		#This variable will keep track of the number of detected clusters
		self.nclusters = None
		self.comparison = Comparison(nclusters=None)
		
		#Keep track of the mouse click mode
		self.mouse_click_mode = None
		
		#These variables will contain various PIL images
		self.img = None
		self.img_source = None
		self.img_threshold = None
		self.img_clusters = None
		self.img_histogram = None
		
		#These variables contain the starting point of line for drawing
		self.linex_start = None
		self.liney_start = None
		self.line_obj = None
		
		#These variables contain the polygon for analysis region
		self.polygon_alpha = None
		self.polygon_beta = None
		self.selreg_current_line = None
		
		#These variables will contain thresholding information
		self.mask_threshold = None
		
		#These variables will contain cluster information
		self.cluster_data = None
		
		#This is the display scale for zooming in/out
		self.scale = 1.0
		
		#This variable controls the zoom directionality (+1 in/-1 out)
		self.zoom_dir = 0
		
		#Remember the root object for the full user interface so that the methods of coffeegrindsize_GUI can refer to it
		self.master = root
		
		#The first row where options or buttons will be displayed
		self.options_row = 1
		
		#The width of text entries for adjustable options
		self.width_entries = 6
		
		#Horizontal spaces around the option labels
		self.title_padx = 12
		
		#Horizontal and vertical spaces around the toolbar buttons
		self.toolbar_padx = 6
		self.toolbar_pady = 6
		
		#Size in pixels of the canvas where the pictures and figures will be displayed
		self.canvas_width = 1000
		self.canvas_height = 780
		
		#Set the last image position memory to its default center
		self.last_image_x = self.canvas_width/2
		self.last_image_y = self.canvas_height/2
		
		#Set the window title
		self.master.title("Coffee Particle Size Distribution by Jonathan Gagne")
		
		#Create a toolbar with buttons to launch various steps of analysis
		toolbar_bg = "gray90"
		toolbar = Frame(self.master, bg=toolbar_bg)
		toolbar.pack(side=TOP, fill=X)
		
		#Create a second toolbar
		toolbar2 = Frame(self.master, bg=toolbar_bg)
		toolbar2.pack(side=TOP, fill=X)
		
		#Create a status bar at the bottom of the window
		self.status_var = StringVar()
		self.status_var.set("Idle...")
		status = Label(self.master, textvariable=self.status_var, anchor=W, bg="grey", relief=SUNKEN)
		status.pack(side=BOTTOM, fill=X)
		
		# === Initialize the main frame that will contain option buttons and settings and the image ===
		self.frame_options = Frame(root)
		self.frame_options.pack()
		
		# === Build the adjustable keyword options ===
		
		#This adds a vertical spacing in the options frame
		self.label_separator()
		
		#All options related to image scale
		self.label_title("Physical Scale of the Image:")
		
		if def_pixel_scale is None:
			def_pix_len = None
		else:
			def_pix_len = def_pixel_scale*float(reference_objects_dict["Custom"])
		
		#Length of the reference object
		self.pixel_length_var, self.pixel_length_id = self.label_entry(def_pix_len, "Reference Pixel Length:", "pix", entry_id=True)
		self.physical_length_var, self.physical_length_id = self.label_entry(reference_objects_dict["Custom"], "Reference Physical Size:", "mm", entry_id=True, event_on_entry="update_pixel_scale")
		self.pixel_length_id.config(state=DISABLED)
		
		#Angle of selection
		self.physical_angle_var, self.physical_angle_id = self.label_entry("None", "Angle of Reference Line:", "deg", entry_id=True)
		self.physical_angle_id.config(state=DISABLED)
		
		#Provide a menu of reference objects
		self.reference_object = self.dropdown_entry("Reference Object:", list(reference_objects_dict.keys()), self.change_reference_object)
		
		#Physical size of one pixel in the coffee grounds picture
		#For now this needs to be input manually
		self.pixel_scale_var = self.label_entry(def_pixel_scale, "Pixel Scale:", "pix/mm")
		
		self.label_separator()
		
		#All options related to image thresholding
		self.label_title("Threshold Step:")
		
		#Value of fractional threshold in units of flux in the blue channel of the image
		self.threshold_var = self.label_entry(def_threshold, "Threshold:", "%")
		
		self.label_separator()
		
		#All options related to particle detection
		self.label_title("Particle Detection Step:")
		
		#Maximum cluster diameter that should be considered a valid coffee particle
		self.max_cluster_axis_var = self.label_entry(def_max_cluster_axis, "Maximum Cluster Diameter:", "pix")
		
		#Minumum cluster surface that should be considered a valid coffee particle
		self.min_surface_var = self.label_entry(def_min_surface, "Minimum Cluster Surface:", "pix²")
		
		#Minimum cluster roundness that should be considered a valid coffee particle
		#Roundess is defined between 0 and 1 where 1 is a perfect circle. It represents the fraction of thresholded pixels inside the smallest circle that encompasses the farthest thresholded pixels in one cluster
		self.min_roundness_var = self.label_entry(def_min_roundness, "Minimum Roundness:", "")
		
		#Whether the Particle Detection step should be quick and approximate
		self.quick_var = IntVar()
		self.quick_var.set(0)
		quick_checkbox = Checkbutton(self.frame_options, text="Quick & Approximate", variable=self.quick_var)
		quick_checkbox.grid(row=self.options_row, columnspan=2, sticky=E)
		
		self.options_row += 1
		
		self.label_separator()
		
		#All options related to particle detection
		self.label_title("Create Histogram Step:")
		
		self.hist_choices = ["Number vs Diameter", "Number vs Surface", "Mass vs Diameter", "Mass vs Surface", "Extract vs Diameter", "Extract vs Surface", "Surface vs Diameter", "Surface vs Surface", "Extraction Yield Distribution"]
		self.hist_codes = ["num_diam", "num_surf", "mass_diam", "mass_surf", "bev_diam", "bev_surf", "surf_diam", "surf_surf", "ey"]
		self.histogram_type = self.dropdown_entry("Histogram Options:", self.hist_choices, self.change_histogram_type)
		
		#Label for the data
		self.data_label_var, self.data_label_id = self.label_entry("Current Data", "Data Label:", "", entry_id=True, columnspan=2, width=self.width_entries*3, event_on_enter="create_histogram")
		
		#Label for the comparison data
		self.comparison_data_label_var, self.comparison_data_label_id = self.label_entry("Comparison Data", "Comparison Label:", "", entry_id=True, columnspan=2, width=self.width_entries*3, event_on_enter="create_histogram")
		
		#Deactivate by default
		self.comparison_data_label_id.config(state=DISABLED)
		
		#Whether the X axis of the histogram should be set manually
		#This is a checkbox
		self.xaxis_auto_var = IntVar()
		self.xaxis_auto_var.set(1)
		xaxis_auto_checkbox = Checkbutton(self.frame_options, text="Automated X axis | ", variable=self.xaxis_auto_var, command=self.xaxis_auto_event)
		xaxis_auto_checkbox.grid(row=self.options_row, columnspan=1, sticky=E, column=0)
		
		#X axis range for the histogram figure
		self.xmin_var, self.xmin_var_id = self.label_entry(def_min_x_axis, "Min. X Axis:", "", entry_id=True, addcol=1, event_on_enter="create_histogram")
		
		#Whether the X axis of the histogram should be in logarithm format
		#This is a checkbox
		self.xlog_var = IntVar()
		self.xlog_var.set(1)
		xlog_checkbox = Checkbutton(self.frame_options, text="Log X axis | ", variable=self.xlog_var, command=self.xlog_event)
		xlog_checkbox.grid(row=self.options_row, columnspan=1, sticky=E, column=0)
		
		self.xmax_var, self.xmax_var_id = self.label_entry(def_max_x_axis, "Max. X Axis:", "", entry_id=True, addcol=1, event_on_enter="create_histogram")
		
		#By default these options are disabled
		self.xmin_var_id.config(state=DISABLED)
		self.xmax_var_id.config(state=DISABLED)
		
		self.options_row += 1
		
		#Whether the number of bins should be automated
		#This is a checkbox
		self.nbins_auto_var = IntVar()
		self.nbins_auto_var.set(1)
		nbins_auto_checkbox = Checkbutton(self.frame_options, text="Automated bins | ", variable=self.nbins_auto_var, command=self.nbins_auto_event)
		nbins_auto_checkbox.grid(row=self.options_row, columnspan=1, column=0, sticky=E)
		
		#self.options_row += 1
		
		#X axis range for the histogram figure
		self.nbins_var, self.nbins_var_id = self.label_entry(10, "Num. bins:", "", entry_id=True, addcol=1, event_on_enter="create_histogram")
		
		#By default this option is disabled
		self.nbins_var_id.config(state=DISABLED)
		
		self.label_separator()
		
		#All options related to saving output data
		self.label_title("Output Options:")
		
		#Button to select an output directory
		output_dir_button = Button(self.frame_options, text="Select Output Directory:", command=self.select_output_dir)
		output_dir_button.grid(row=self.options_row, sticky=E)
		
		#Display current output dir
		self.output_dir_var, self.output_dir_label_id = self.label_entry(self.output_dir, "", "", entry_id=True, columnspan=2, width=self.width_entries*3)
		self.output_dir_label_id.config(state=DISABLED)
		
		self.options_row += 1
		
		#The base of the output file names
		self.session_name_var = self.label_entry(def_session_name, "Base of File Names:", "", columnspan=2, width=self.width_entries*3)
		
		self.label_separator()
		
		#All options related to image display
		self.label_title("Display Options:")
		
		#Select the display type
		choices = [original_image_display_name, threshold_image_display_name, outlines_image_display_name, histogram_image_display_name]
		self.display_type = self.dropdown_entry("Display Type:", choices, self.change_display_type)
		
		#Remember the previous display type in case of error
		self.previous_display_type = choices[0]
		
		#Button to zoom in
		self.zoom_in_button = Button(self.frame_options, text="Zoom In", command=self.zoom_in_button)
		self.zoom_in_button.grid(row=self.options_row, column=0, columnspan=1, sticky=E)
		
		self.zoom_out_button = Button(self.frame_options, text="Zoom Out", command=self.zoom_out_button)
		self.zoom_out_button.grid(row=self.options_row, column=1, columnspan=1, sticky=W)
		
		#Button for resetting zoom in the displayed image
		self.reset_zoom_button = Button(self.frame_options, text="Reset Zoom", command=self.reset_zoom)
		self.reset_zoom_button.grid(row=self.options_row, column=2, columnspan=1, sticky=W)
		self.options_row += 1
		
		#Add a few horizontal spaces
		#for i in range(4):
		self.label_separator()
		
		#Button for resetting all options to default
		reset_params_button = Button(self.frame_options, text="Reset All Parameters", command=self.reset_status)
		reset_params_button.grid(row=self.options_row, column=1, columnspan=2, sticky=E)
		
		# === Create a canvas to display images and figures ===
		
		#Initialize the image canvas
		image_canvas_bg = "gray40"
		self.image_canvas = Canvas(self.frame_options, width=self.canvas_width, height=self.canvas_height, bg=image_canvas_bg)
		self.image_canvas.grid(row=0, column=3, rowspan=145, sticky=N)
		
		#Prevent the image canvas to shrink when labels are placed in it
		self.image_canvas.pack_propagate(0)
		
		#Display a label when no image was loaded
		self.noimage_label = Label(self.image_canvas, text="No Image Loaded", anchor=CENTER, bg=image_canvas_bg, font='Helvetica 18 bold', width=self.canvas_width, height=self.canvas_height)
		self.noimage_label.pack(side=LEFT)
		
		frame_stats_bg = "gray60"
		self.frame_stats = Frame(self.frame_options, bg=frame_stats_bg, padx=2, pady=10)
		self.frame_stats.grid(row=33, column=3, sticky=NW, rowspan=10)
		
		title_label = Label(self.frame_stats, text="Properties of the Particle Distribution:", font='Helvetica 18 bold', bg=frame_stats_bg)
		title_label.grid(row=0, sticky=W, padx=self.title_padx, columnspan=12)
		
		stats_colsep_width = 3
		stats_row = 1
		stats_column = 0
		
		stats_entry_width = 5
		self.diam_average_var = StringVar()
		self.diam_average_var.set("None")
		diam_average_label = Label(self.frame_stats, text="Average Diameter:", bg=frame_stats_bg, font='Helvetica 14 bold')
		diam_average_label.grid(row=stats_row, sticky=E, column=stats_column)
		diam_average_entry = Label(self.frame_stats, textvariable=self.diam_average_var, width=stats_entry_width, bg=frame_stats_bg)
		diam_average_entry.grid(row=stats_row, column=stats_column+1)
		unit_label = Label(self.frame_stats, text="(mm)", bg=frame_stats_bg)
		unit_label.grid(row=stats_row, column=stats_column+2, sticky=W)
		
		stats_row += 1
		
		self.diam_stddev_var = StringVar()
		self.diam_stddev_var.set("None")
		diam_stddev_label = Label(self.frame_stats, text="Scatter in Diameter:", bg=frame_stats_bg, font='Helvetica 14 bold')
		diam_stddev_label.grid(row=stats_row, sticky=E, column=stats_column)
		diam_stddev_entry = Label(self.frame_stats, textvariable=self.diam_stddev_var, width=stats_entry_width, bg=frame_stats_bg)
		diam_stddev_entry.grid(row=stats_row, column=stats_column+1)
		unit_label = Label(self.frame_stats, text="(mm)", bg=frame_stats_bg)
		unit_label.grid(row=stats_row, column=stats_column+2, sticky=W)
		
		stats_column += 3
		stats_row =1
		
		separator_label = Label(self.frame_stats, text="", width=stats_colsep_width, bg=frame_stats_bg)
		separator_label.grid(row=stats_row, column=stats_column)
		
		stats_column += 1
		
		self.surf_average_var = StringVar()
		self.surf_average_var.set("None")
		surf_average_label = Label(self.frame_stats, text="Average Surface:", bg=frame_stats_bg, font='Helvetica 14 bold')
		surf_average_label.grid(row=stats_row, sticky=E, column=stats_column)
		surf_average_entry = Label(self.frame_stats, textvariable=self.surf_average_var, width=stats_entry_width, bg=frame_stats_bg)
		surf_average_entry.grid(row=stats_row, column=stats_column+1)
		unit_label = Label(self.frame_stats, text="(mm²)", bg=frame_stats_bg)
		unit_label.grid(row=stats_row, column=stats_column+2, sticky=W)
		
		stats_row += 1
		
		self.surf_stddev_var = StringVar()
		self.surf_stddev_var.set("None")
		surf_stddev_label = Label(self.frame_stats, text="Scatter in Surface:", bg=frame_stats_bg, font='Helvetica 14 bold')
		surf_stddev_label.grid(row=stats_row, sticky=E, column=stats_column)
		surf_stddev_entry = Label(self.frame_stats, textvariable=self.surf_stddev_var, width=stats_entry_width, bg=frame_stats_bg)
		surf_stddev_entry.grid(row=stats_row, column=stats_column+1)
		unit_label = Label(self.frame_stats, text="(mm²)", bg=frame_stats_bg)
		unit_label.grid(row=stats_row, column=stats_column+2, sticky=W)
		
		stats_column += 3
		stats_row =1
		
		separator_label = Label(self.frame_stats, text="", width=stats_colsep_width, bg=frame_stats_bg)
		separator_label.grid(row=stats_row, column=stats_column)
		
		stats_column += 1
		
		self.ey_average_var = StringVar()
		self.ey_average_var.set("None")
		ey_average_label = Label(self.frame_stats, text="Average EY:", bg=frame_stats_bg, font='Helvetica 14 bold')
		ey_average_label.grid(row=stats_row, sticky=E, column=stats_column)
		ey_average_entry = Label(self.frame_stats, textvariable=self.ey_average_var, width=stats_entry_width, bg=frame_stats_bg)
		ey_average_entry.grid(row=stats_row, column=stats_column+1)
		unit_label = Label(self.frame_stats, text="(%)", bg=frame_stats_bg)
		unit_label.grid(row=stats_row, column=stats_column+2, sticky=W)
		
		stats_row += 1
		
		self.ey_stddev_var = StringVar()
		self.ey_stddev_var.set("None")
		ey_stddev_label = Label(self.frame_stats, text="Scatter in EY:", bg=frame_stats_bg, font='Helvetica 14 bold')
		ey_stddev_label.grid(row=stats_row, sticky=E, column=stats_column)
		ey_stddev_entry = Label(self.frame_stats, textvariable=self.ey_stddev_var, width=stats_entry_width, bg=frame_stats_bg)
		ey_stddev_entry.grid(row=stats_row, column=stats_column+1)
		unit_label = Label(self.frame_stats, text="(%)", bg=frame_stats_bg)
		unit_label.grid(row=stats_row, column=stats_column+2, sticky=W)
		
		# === Populate the toolbar with buttons for analysis ===
		
		#Button to open an image of the coffee grounds picture
		open_image_button = Button(toolbar, text="Open Image", command=self.open_image, highlightbackground=toolbar_bg)
		open_image_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to select a reference object
		ref_obj_button = Button(toolbar, text="Select Reference Object", command=self.select_reference_object_mouse, highlightbackground=toolbar_bg)
		ref_obj_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to select region containing the coffee grounds
		region_button = Button(toolbar, text="Select Analysis Region", command=self.select_region, highlightbackground=toolbar_bg)
		region_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to apply image threshold
		threshold_image_button = Button(toolbar, text="Threshold Image", command=self.threshold_image, highlightbackground=toolbar_bg)
		threshold_image_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to launch the particle detection analysis
		psd_button = Button(toolbar, text="Launch Particle Detection", command=self.launch_psd,highlightbackground=toolbar_bg)
		psd_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to display histogram figures
		histogram_button = Button(toolbar, text="Create Histogram", command=lambda: self.create_histogram(None), highlightbackground=toolbar_bg)
		histogram_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Read Blog Button
		#Button to open blog
		blog_button = Button(toolbar, text="Read Coffee Ad Astra Blog", command=self.blog_goto, highlightbackground=toolbar_bg)
		blog_button.pack(side=RIGHT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Downsample button
		downsample_button = Button(toolbar2, text="Reduce Image Quality", command=self.downsample_image, highlightbackground=toolbar_bg)
		downsample_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to load data from disk
		load_data_button = Button(toolbar2, text="Load Data", command=self.load_data, highlightbackground=toolbar_bg)
		load_data_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to load comparison data from disk
		load_comparison_data_button = Button(toolbar2, text="Load Comparison Data", command=self.load_comparison_data, highlightbackground=toolbar_bg)
		load_comparison_data_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to flush comparison data
		flush_comparison_data_button = Button(toolbar2, text="Flush Comparison Data", command=self.flush_comparison_data, highlightbackground=toolbar_bg)
		flush_comparison_data_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to output data to the disk
		save_button = Button(toolbar2, text="Save Data", command=self.save_data, highlightbackground=toolbar_bg)
		save_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to save histogram to disk
		savehist_button = Button(toolbar2, text="Save View", command=self.save_histogram, highlightbackground=toolbar_bg)
		savehist_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Quit button
		quit_button = Button(toolbar2, text="Quit", command=self.quit_gui, highlightbackground=toolbar_bg)
		quit_button.pack(side=RIGHT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Help button
		help_button = Button(toolbar2, text="Help", command=self.launch_help, highlightbackground=toolbar_bg)
		help_button.pack(side=RIGHT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		# === Create a menu bar (File, Edit...) ===
		menu = Menu(root)
		root.config(menu=menu)

		#Create a FILE submenu
		subMenu = Menu(menu)
		menu.add_cascade(label="File", menu=subMenu)
		
		#Add an option to open images from disk
		subMenu.add_command(label="Open Image...", command=self.open_image)
		subMenu.add_separator()
		
		#Add an option to downsample images
		subMenu.add_command(label="Reduce Image Quality...", command=self.downsample_image)
		subMenu.add_separator()
		
		#Add an option for debugging
		subMenu.add_command(label="Python Debugger...", command=self.pdb_call)
		subMenu.add_separator()
		
		#Add an option to quit
		subMenu.add_command(label="Quit", command=self.quit_gui)
		
		# === Create drag and zoom options for the image canvas ===
		
		#Always keep track of the mouse position (this is used for zooming toward the cursor)
		self.image_canvas.bind('<Motion>', self.motion)
		
		#Set up key bindings for dragging the image
		self.image_canvas.bind("<ButtonPress-1>", self.move_start)
		self.image_canvas.bind("<B1-Motion>", self.move_move)
		
		#Set up key bindings for drawing a line
		self.image_canvas.bind("<ButtonPress-2>", self.line_start)
		self.image_canvas.bind("<B2-Motion>", self.line_move)
		
		#Set up key bindings for zooming in and out with the i/o keys
		self.image_canvas.bind_all("i", self.zoom_in)
		self.image_canvas.bind_all("o", self.zoom_out)
		
		#Set up key binding for data analysis selection quit
		self.image_canvas.bind_all("q", self.quit_region_select)
	
	#Method to refresh histograms when xlog is toggled
	def xlog_event(self):
		
		#If there is already a histogram in play, refresh it
		if self.img_histogram is not None:
			self.create_histogram(None)
	
	#Method to refresh histograms when automated bins are changed
	def nbins_auto_event(self):
		
		#If not automated then enable the option
		if self.nbins_auto_var.get() == 0:
			self.nbins_var_id.config(state=NORMAL)
		
		#If automated then disable the option
		if self.nbins_auto_var.get() == 1:
			self.nbins_var_id.config(state=DISABLED)
		
		#If there is already a histogram in play, refresh it
		if self.img_histogram is not None:
			self.create_histogram(None)
	
	#Method to set the X axis options to automated
	def xaxis_auto_event(self):
		
		#If there is already a histogram in play, refresh it
		if self.img_histogram is not None:
			self.create_histogram(None)
		
		#If not automated then enable the parameters
		if self.xaxis_auto_var.get() == 0:
			self.xmin_var_id.config(state=NORMAL)
			self.xmax_var_id.config(state=NORMAL)
		
		#If automated then disable the parameters
		if self.xaxis_auto_var.get() == 1:
			self.xmin_var_id.config(state=DISABLED)
			self.xmax_var_id.config(state=DISABLED)
	
	#Method to select the reference object in the image with the mouse
	def select_reference_object_mouse(self):
		
		#Verify that an image is loaded
		if self.img_source is None:
				
				#Update the user interface status
				self.status_var.set("Original Image not Loaded Yet... Use Open Image Button...")
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Change the mouse click mode
		self.mouse_click_mode = "SELECT_REFERENCE_OBJECT_READY"
		
		#Update the user interface status
		self.status_var.set("Use your mouse to click on one side of the reference object... You will then need to click again to set up a measuring line...")
		
		#Update the user interface
		self.master.update()
	
	#Method to select analysis region
	def select_region(self):
		
		#Do nothing if already in select region mode
		if self.mouse_click_mode == "SELECT_REGION":
			return
		
		#Verify that an image is loaded
		if self.img_source is None:
				
				#Update the user interface status
				self.status_var.set("Original Image not Loaded Yet... Use Open Image Button...")
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Delete all currently drawn lines
		self.image_canvas.delete(self.image_canvas.find_withtag("line"))
		
		#Reset the region if it exists
		self.polygon_alpha = None
		self.polygon_beta = None
		
		#Redraw the selected image
		self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#Update the user interface status
		self.status_var.set("Click on the image to draw a polygon enclosing the coffee grounds, then press q...")
		
		#Update the user interface
		self.master.update()
		
		#Change mouse click mode
		self.mouse_click_mode = "SELECT_REGION"
	
	#Method to finish analysis region selection
	def quit_region_select(self, event):
		
		#Only active if image canvas has focus
		if self.master.focus_get() != self.image_canvas:
			return
		
		#Only active in SELECT_REGION mode
		if self.mouse_click_mode == "SELECT_REGION":
			
			#Destroy current mobile line if it exists
			if self.selreg_current_line is not None:
				self.image_canvas.delete(self.selreg_current_line)
				self.selreg_current_line = None
			
			#If there are too few polygon corners just quit
			if self.polygon_alpha.size < 3:
				
				#Delete all currently drawn lines
				self.image_canvas.delete(self.image_canvas.find_withtag("line"))
				
				#Reset the polygon region
				self.polygon_alpha = None
				self.polygon_beta = None
				
				#Update the user interface status
				self.status_var.set("Analysis Region Did Not Have Enough Corners (at least 3 are needed)...")
				
			else:
				
				#Add last polygon corner
				self.polygon_alpha = np.append(self.polygon_alpha, self.polygon_alpha[0])
				self.polygon_beta = np.append(self.polygon_beta, self.polygon_beta[0])
				
				#Update the user interface status
				self.status_var.set("Analysis Region Was Set...")
			
			#Redraw image
			self.redraw(x=self.last_image_x, y=self.last_image_y)
			
			#Update the user interface
			self.master.update()
			
			#Change mouse click mode
			self.mouse_click_mode = None
	
	#Method to open blog web page
	def blog_goto(self, *args):
		webbrowser.open("https://coffeeadastra.com")
	
	#Method to change the reference object on the image
	def change_reference_object(self, *args):
		
		#Set the physical size of the reference object
		self.physical_length_var.set(reference_objects_dict[self.reference_object.get()])
		
		#Enable or disable the manual data entry depending on dictionary value
		if self.reference_object.get() == "Custom":
			self.physical_length_id.config(state=NORMAL)
		else:
			self.physical_length_id.config(state=DISABLED)
		
		#Update the resulting pixel scale
		self.update_pixel_scale()
		
		#Update the GUI status
		self.status_var.set("Reference Object set to "+self.reference_object.get()+"...")
		
		#Update the user interface
		self.master.update()
	
	#Method to update the pixel scale
	def update_pixel_scale(self):
		
		#Calculate pixel scale. If an error arises then something was not a number
		try:
			pixel_scale = float(self.pixel_length_var.get())/float(self.physical_length_var.get())
			#Make it a string
			pixel_scale_str = "{0:.{1}f}".format(pixel_scale, 3)
		except:
			pixel_scale = None
			pixel_scale_str = "None"
		
		#Update the object value and display
		self.pixel_scale_var.set(pixel_scale_str)
	
	#Method to register changes in the histogram type option
	def change_histogram_type(self, *args):
		
		#If there is already a histogram in play, refresh it
		if self.img_histogram is not None:
			self.create_histogram(None)
	
	def change_display_type(self, *args):
		
		#Verify that original image is loaded
		if self.display_type.get() == original_image_display_name:
			if self.img_source is None:
				
				#Update the user interface status
				self.status_var.set("Original Image not Loaded Yet... Use Open Image Button...")
				
				#Reset to previous display type
				self.display_type.set(self.previous_display_type)
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Verify that thresholded image is loaded
		if self.display_type.get() == threshold_image_display_name:
			if self.img_threshold is None:
				
				#Update the user interface status
				self.status_var.set("Thresholded Image not Available Yet... Use Threshold Image Button...")
				
				#Reset to previous display type
				self.display_type.set(self.previous_display_type)
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Verify that cluster outlines image is loaded
		if self.display_type.get() == outlines_image_display_name:
			if self.img_clusters is None:
				
				#Update the user interface status
				self.status_var.set("Cluster Outlines Image not Available Yet... Use Launch Particle Detection Button...")
				
				#Reset to previous display type
				self.display_type.set(self.previous_display_type)
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Verify that cluster outlines image is loaded
		if self.display_type.get() == histogram_image_display_name:
			if self.img_histogram is None:
				
				#Update the user interface status
				self.status_var.set("Histogram Figure not Available Yet... Use Create Histogram Figure Button...")
				
				#Reset to previous display type
				self.display_type.set(self.previous_display_type)
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Reset zoom options etc if moving in to histogram style
		if self.display_type.get() == histogram_image_display_name:
			
			#Delete all polygons
			self.image_canvas.delete(self.image_canvas.find_withtag("line"))
			self.polygon_alpha = None
			self.polygon_beta = None
			
			#Reset the effect of dragging
			self.image_canvas.xview_moveto(0)
			self.image_canvas.yview_moveto(0)
			
			#Remember this new position
			self.last_image_x = self.canvas_width/2
			self.last_image_y = self.canvas_height/2
			
			#Set scale to unity
			self.scale = 1
			
			#Deactivate zoom buttons
			self.zoom_in_button.config(state=DISABLED)
			self.zoom_out_button.config(state=DISABLED)
			self.reset_zoom_button.config(state=DISABLED)
			
		#If we are moving out from histogram display
		else:
			if self.previous_display_type == histogram_image_display_name:
				#Set scale to original scale
				self.scale = self.original_scale
				
				#Reactivate zoom buttons
				self.zoom_in_button.config(state=NORMAL)
				self.zoom_out_button.config(state=NORMAL)
				self.reset_zoom_button.config(state=NORMAL)
		
		#Redraw the selected image
		self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#Update the user interface status
		self.status_var.set("Changed Display to "+self.display_type.get()+"...")
		
		#Remember the previous display image in case of future error
		self.previous_display_type = self.display_type.get()
		
		#Update the user interface
		self.master.update()
		
	def dropdown_entry(self, label, choices, method, default_choice_index=0):
		
		#Create a variable that will be bound to the dropdown menu
		data_var = StringVar()
		
		#First option is the initial choice by default
		data_var.set(choices[default_choice_index])
		
		#Create a label for the dropdown menu
		dropdown_label = Label(self.frame_options, text=label)
		dropdown_label.grid(row=self.options_row, sticky=E)
		
		#Create the dropdown menu itself
		dropdown_menu = OptionMenu(self.frame_options, data_var, *choices)
		dropdown_menu.grid(row=self.options_row, column=1, columnspan=2, sticky=EW)
		
		#Link the tropdown menu to a method
		data_var.trace('w', method)
		
		#Update the display row
		self.options_row += 1
		
		#Return internal variable to caller
		return data_var
	
	def test(self):
		print("!")
	
	#Method to display a label in the options frame
	def label_entry(self, default_var, text, units_text, columnspan=None, width=None, entry_id=False, event_on_entry=None, addcol=0, event_on_enter=None):
		
		#Default width is located in the internal class variables
		if width is None:
			width = self.width_entries
		
		#Introduce a variable to be linked with the entry dialogs
		data_var = StringVar()
		
		#Set variable to default value
		data_var.set(str(default_var))
		
		#Display the label for the name of the option
		if text != "":
			data_label = Label(self.frame_options, text=text)
			data_label.grid(row=self.options_row, sticky=E, column=addcol)
		
		#Link data entry to an event if this is required
		if event_on_entry is not None:
			#Determine the function to be triggered
			function_trigger = getattr(self, event_on_entry)
			data_var.trace("w", lambda name, index, mode, data_var=data_var: function_trigger())
		
		#Display the data entry box
		data_entry = Entry(self.frame_options, textvariable=data_var, width=width)
		data_entry.grid(row=self.options_row, column=1+addcol, columnspan=columnspan)
		
		#Bind the return key with a method
		if event_on_enter is not None:
			function_trigger = getattr(self, event_on_enter)
			data_entry.bind('<Return>', function_trigger)
		
		#Display the physical units of this option
		if units_text != "":
			data_label_units = Label(self.frame_options, text=units_text)
			data_label_units.grid(row=self.options_row, column=2+addcol, sticky=W)
		
		#Update the row where next labels and entries will be displayed
		self.options_row += 1
		
		#Return data entry ID to caller if required
		if entry_id is True:
			return data_var, data_entry
		else:
			#Otherwise return just value of the bound variable to the caller
			return data_var
	
	#Method to display a title for option groups
	def label_title(self, text):
		title_label = Label(self.frame_options, text=text, font='Helvetica 18 bold')
		title_label.grid(row=self.options_row, sticky=W, padx=self.title_padx, columnspan=2)
		self.options_row += 1
	
	#Method to display a vertical blank separator in the options frame
	def label_separator(self):
		separator_label = Label(self.frame_options, text="")
		separator_label.grid(row=self.options_row)
		self.options_row += 1
	
	#Method to redraw the image after a zoom
	def redraw(self, x=0, y=0):
			
			#Delete all currently drawn lines
			self.image_canvas.delete(self.image_canvas.find_withtag("line"))
			
			#Delete currently drawn image if there is one
			if self.image_id:
				self.image_canvas.delete(self.image_id)
			
			#Select the appropriate image to be displayed
			if self.display_type.get() == original_image_display_name:
				self.img = self.img_source
			if self.display_type.get() == threshold_image_display_name:
				self.img = self.img_threshold
			if self.display_type.get() == outlines_image_display_name:
				self.img = self.img_clusters
			
			#The case of a histogram is a bit special
			if self.display_type.get() == histogram_image_display_name:
				
				#Place histogram in image buffer
				self.img = self.img_histogram
				
				#Delete all currently drawn lines
				
				#Reset the region if it exists
				self.polygon_alpha = None
				self.polygon_beta = None
			
			#Determine the size of the image to be drawn and scale it appropriately
			iw, ih = self.img.size
			size = int(iw*self.scale), int(ih*self.scale)

			#Load and display the updated image
			self.image_obj = ImageTk.PhotoImage(self.img.resize(size))
			self.image_id = self.image_canvas.create_image(x, y, image=self.image_obj)
			
			#Draw data analysis lines if they are defined
			if self.polygon_alpha is not None:
				
				#There must be at least two points to draw the lines
				npoly = self.polygon_alpha.size
				if npoly > 1:
					
					#Get current coordinates of image
					image_x, image_y = self.image_canvas.coords(self.image_id)
					
					#Include effect of drag
					image_x -= self.image_canvas.canvasx(0)
					image_y -= self.image_canvas.canvasy(0)
					
					#Get original image size
					orig_nx, orig_ny = self.img.size
					
					#Now draw the lines
					for i in range(npoly-1):
						
						#Determine current X, Y positions of lines
						line_x_start = (self.polygon_alpha[i] - orig_nx/2)*self.scale + image_x
						line_y_start = (self.polygon_beta[i] - orig_ny/2)*self.scale + image_y
						line_x_end = (self.polygon_alpha[i+1] - orig_nx/2)*self.scale + image_x
						line_y_end = (self.polygon_beta[i+1] - orig_ny/2)*self.scale + image_y
						
						#Include effect of drag
						line_x_start += self.image_canvas.canvasx(0)
						line_y_start += self.image_canvas.canvasy(0)
						line_x_end += self.image_canvas.canvasx(0)
						line_y_end += self.image_canvas.canvasy(0)
						
						#Redraw line
						line_obj = self.image_canvas.create_line(line_x_start, line_y_start, line_x_end, line_y_end, fill="green")
						
						#I will need to figure out how to delete those when they go outside of the image frame
	
	#Method to set the starting point of a drag
	def move_start(self, event):
		
		#Set focus on image canvas to avoid writing in Entries
		self.image_canvas.focus_set()
		
		#In histogram mode, do nothing
		if self.display_type.get() == histogram_image_display_name:
			return
		
		#In normal mode, set start of motion
		if self.mouse_click_mode is None:
			self.image_canvas.scan_mark(event.x, event.y)
		
		#If this is the second click in Select Reference Object mode, end it
		if self.mouse_click_mode == "SELECT_REFERENCE_OBJECT":
			
			#Tell the motion method that we are now in line drawing mode
			self.mouse_click_mode = None
			
			#Refresh the user interface status
			self.status_var.set("The length of the the reference object was set to "+self.pixel_length_var.get()+" pixels... Now select its physical size with the library in the Reference Object dropdown menu, or with a custom Reference Physical Size...")
			
			#Refresh the state of the user interface window
			self.master.update()
		
		#In Select Reference Object mode, set start of line
		if self.mouse_click_mode == "SELECT_REFERENCE_OBJECT_READY":
			
			#In histogram mode, do nothing
			if self.display_type.get() == histogram_image_display_name:
				return
			
			#Set the starting point for the red line
			self.line_start(event)
			
			#Tell the motion method that we are now in line drawing mode
			self.mouse_click_mode = "SELECT_REFERENCE_OBJECT"
			
			#Refresh the user interface status
			self.status_var.set("Drag the red line across the reference object then click again... Be careful to exclude shadows, and make sure that the Angle of Reference Line entry is satisfactory to you...")
			
			#Refresh the state of the user interface window
			self.master.update()
			
			#Redraw image (TMP is this needed !!)
			#self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#In select Region mode, add corners to polygon
		if self.mouse_click_mode == "SELECT_REGION":
			
			# === Determine mouse position in original pixel units ===
			#Get current coordinates of image
			image_x, image_y = self.image_canvas.coords(self.image_id)
			
			#Include effect of drag
			image_x -= self.image_canvas.canvasx(0)
			image_y -= self.image_canvas.canvasy(0)
		
			#Get original image size
			orig_nx, orig_ny = self.img.size
		
			#Determine cursor position on original image coordinates (x,y -> alpha, beta)
			mouse_alpha = orig_nx/2 + (self.mouse_x - image_x)/self.scale
			mouse_beta = orig_ny/2 + (self.mouse_y - image_y)/self.scale
			
			if self.polygon_alpha is None:
				self.polygon_alpha = np.array([mouse_alpha])
				self.polygon_beta = np.array([mouse_beta])
			else:
				self.polygon_alpha = np.append(self.polygon_alpha, mouse_alpha)
				self.polygon_beta = np.append(self.polygon_beta, mouse_beta)
			
			#Redraw image
			self.redraw(x=self.last_image_x, y=self.last_image_y)
	
	#Method to execute the move of a drag
	def move_move(self, event):
		
		#In histogram mode, do nothing
		if self.display_type.get() == histogram_image_display_name:
			return
		
		#Otherwise, drag image
		if self.mouse_click_mode is None:
			self.image_canvas.scan_dragto(event.x, event.y, gain=1)
	
	#Method to set the starting point of a line
	def line_start(self, event):
		
		#In histogram mode, do nothing
		if self.display_type.get() == histogram_image_display_name:
			return
		
		#Otherwise, remember start position for line
		self.linex_start = event.x + self.image_canvas.canvasx(0)
		self.liney_start = event.y + self.image_canvas.canvasy(0)
		
	#Method to draw the line
	def line_move(self, event):
		
		#In histogram mode, do nothing
		if self.display_type.get() == histogram_image_display_name:
			return
		
		#Destroy any existing line
		if self.line_obj is not None:
			self.image_canvas.delete(self.line_obj)
		
		#Calculate current x and y positions
		cur_x = event.x + self.image_canvas.canvasx(0)
		cur_y = event.y + self.image_canvas.canvasy(0)
		
		#Redraw line
		self.line_obj = self.image_canvas.create_line(self.linex_start, self.liney_start, cur_x, cur_y, fill="red")
		
		#Update length of line in pixels
		line_length = np.sqrt((cur_x - self.linex_start)**2 + (cur_y - self.liney_start)**2)/self.scale
		line_length_str = "{0:.{1}f}".format(line_length, 1)
		self.pixel_length_var.set(line_length_str)
		
		#Update angle of line in degrees
		line_angle = 180.0/np.pi*np.arctan2( (cur_y - self.liney_start), (cur_x - self.linex_start) )
		line_angle_str = "{0:.{1}f}".format(line_angle, 1)
		self.physical_angle_var.set(line_angle_str)
		
		#Update pixel scale
		self.update_pixel_scale()
	
	#Method to track the mouse position
	def motion(self, event):
		
		#In histogram mode, do nothing
		if self.display_type.get() == histogram_image_display_name:
			return
		
		#Update the current mouse position
		self.mouse_x, self.mouse_y = event.x, event.y
		
		#In Select Reference Object mode, set start of line
		if self.mouse_click_mode == "SELECT_REFERENCE_OBJECT":
			
			#Set the current point for the red line
			self.line_move(event)
			
			#Redraw image (TMP is this needed !!)
			#self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#In analysis selection region mode, show the next line
		if self.mouse_click_mode == "SELECT_REGION":
			
			#Draw data analysis lines if they are defined
			if self.polygon_alpha is not None:
				
				#Get current coordinates of image
				image_x, image_y = self.image_canvas.coords(self.image_id)
				
				#Include effect of drag
				image_x -= self.image_canvas.canvasx(0)
				image_y -= self.image_canvas.canvasy(0)
				
				#Get original image size
				orig_nx, orig_ny = self.img.size
				
				# === Now draw the line ===
				#Determine current X, Y positions of the line
				line_x_start = (self.polygon_alpha[-1] - orig_nx/2)*self.scale + image_x
				line_y_start = (self.polygon_beta[-1] - orig_ny/2)*self.scale + image_y
				line_x_end = self.mouse_x
				line_y_end = self.mouse_y
				
				#Include effect of drag
				line_x_start += self.image_canvas.canvasx(0)
				line_y_start += self.image_canvas.canvasy(0)
				line_x_end += self.image_canvas.canvasx(0)
				line_y_end += self.image_canvas.canvasy(0)
				
				#Destroy line if it exists
				if self.selreg_current_line is not None:
					self.image_canvas.delete(self.selreg_current_line)
				
				#Redraw line
				self.selreg_current_line = self.image_canvas.create_line(line_x_start, line_y_start, line_x_end, line_y_end, fill="green")

	
	#Method to apply a zoom in with the button
	def zoom_in_button(self):
		
		#Artificially set the mouse position at the image center
		self.mouse_x, self.mouse_y = self.last_image_x, self.last_image_x
		
		#Apply zoom in the positive direction
		self.zoom(None, 1)
	
	#Method to apply a zoom out with the button
	def zoom_out_button(self):
		
		#Artificially set the mouse position at the image center
		self.mouse_x, self.mouse_y = self.last_image_x, self.last_image_x
		
		#Apply zoom in the positive direction
		self.zoom(None, -1)
	
	#Method to apply a zoom in
	def zoom_in(self, event):
		
		#Check if the image canvas has focus
		if self.master.focus_get() != self.image_canvas:
			return
		
		#In histogram mode, do nothing
		if self.display_type.get() == histogram_image_display_name:
			return
		
		#Apply zoom in the positive direction
		self.zoom(event, 1)
		
	#Method to apply a zoom in
	def zoom_out(self, event):
		
		#In histogram mode, do nothing
		if self.display_type.get() == histogram_image_display_name:
			return
		
		#Apply zoom in the positive direction
		self.zoom(event, -1)
	
	#Method to apply a zoom in any direction
	def zoom(self, event, directionality):
		
		#Get current coordinates of image
		image_x, image_y = self.image_canvas.coords(self.image_id)
		
		#Include effect of drag
		image_x -= self.image_canvas.canvasx(0)
		image_y -= self.image_canvas.canvasy(0)
		
		#Get original image size
		orig_nx, orig_ny = self.img.size
		
		#Determine cursor position on original image coordinates (x,y -> alpha, beta)
		mouse_alpha = orig_nx/2 + (self.mouse_x - image_x)/self.scale
		mouse_beta = orig_ny/2 + (self.mouse_y - image_y)/self.scale
		
		#Change the scale of image according to directionality
		if directionality > 0:
			self.scale *= 2
		if directionality < 0:
			self.scale /= 2
		
		#Determine pixel position for the center of the new zoomed image
		new_image_x = self.mouse_x - (mouse_alpha - orig_nx/2)*self.scale
		new_image_y = self.mouse_y - (mouse_beta - orig_ny/2)*self.scale
		
		#Include effect of drag
		new_image_x += self.image_canvas.canvasx(0)
		new_image_y += self.image_canvas.canvasy(0)
		
		#Remember the last image position
		self.last_image_x = new_image_x
		self.last_image_y = new_image_y
		
		#Redraw image at the desired position
		self.redraw(x=new_image_x, y=new_image_y)
	
	#Method to trigger the Python debugger
	def pdb_call(self):
		pdb.set_trace()
	
	#Method to reset zoom
	def reset_zoom(self):
		
		#Update the user interface status
		self.status_var.set("Zoom Parameters Reset to Defaults...")
		
		#Set back the scale to its original value when the image was loaded
		self.scale = self.original_scale
		
		#Reset the effect of dragging
		self.image_canvas.xview_moveto(0)
		self.image_canvas.yview_moveto(0)
		
		#Redraw the image
		self.redraw(x=self.canvas_width/2, y=self.canvas_height/2)
		
		#Remember this new position
		self.last_image_x = self.canvas_width/2
		self.last_image_y = self.canvas_height/2
		
		#Update the user interface
		self.master.update()
	
	#Method to reset status
	def reset_status(self):
		
		#Reset all options to their default values
		self.threshold_var.set(str(def_threshold))
		self.max_cluster_axis_var.set(str(def_max_cluster_axis))
		self.min_surface_var.set(str(def_min_surface))
		self.min_roundness_var.set(str(def_min_roundness))
		self.quick_var.set(0)
		self.histogram_type.set(self.hist_choices[0])
		self.xmin_var.set(str(def_min_x_axis))
		self.xmax_var.set(str(def_max_x_axis))
		self.xlog_var.set(1)
		self.output_dir = def_output_dir
		self.output_dir_var.set(self.output_dir)
		self.session_name_var.set(str(def_session_name))
		self.display_type.set(original_image_display_name)
		
		#Reset zoom to center the image properly
		self.reset_zoom()
		
		#Update the user interface status
		self.status_var.set("Parameters Reset to Defaults...")
		
		#Update the user interface
		self.master.update()
	
	#Method to select the output directory
	def select_output_dir(self):
		
		#Update root to avoid problems with file dialog
		self.master.update()
		
		#Invoke a file dialog to select output directory
		self.output_dir = filedialog.askdirectory(initialdir=self.output_dir,title="Select an output directory")
		
		#Update the label entry
		self.output_dir_var.set(self.output_dir)
		
		#Update root to avoid problems with file dialog
		self.master.update()
	
	#Method to downsample an image
	def downsample_image(self):
		
		#Verify that an image was loaded
		if self.img_source is None:
				
				#Update the user interface status
				self.status_var.set("Original Image not Loaded Yet... Use Open Image Button...")
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Zoom in
		self.scale *= 2
		self.original_scale *= 2
		
		#Resize image
		self.img_source = self.img_source.resize((int(float(self.img.size[0])/2),int(float(self.img.size[1])/2)), Image.ANTIALIAS)
		self.img = self.img_source
		
		#Redraw the image
		self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#Update the user interface status
		self.status_var.set("The Image was Downsampled by a Factor two... Current Size is ("+str(self.img.size[0])+", "+str(self.img.size[1])+")")
		
		#Update the user interface
		self.master.update()
		
	#Method to open an image from the disk
	def open_image(self):
		
		#Delete all currently drawn lines
		self.image_canvas.delete(self.image_canvas.find_withtag("line"))
		
		#Reset the region if it exists
		self.polygon_alpha = None
		self.polygon_beta = None
		
		#Update root to avoid problems with file dialog
		self.master.update()
		
		#Do not delete
		#Invoke a file dialog to select image
		#image_filename = "/Users/gagne/Documents/Postdoc/Coffee_Stuff/Grind_Size/Forte_half_seasoned/forte_3y_mid.png"
		image_filename = filedialog.askopenfilename(initialdir=self.output_dir,title="Select a PNG image",filetypes=(("png files","*.png"),("all files","*.*")))
		
		# === Display image if filename is set ===
		# Hitting cancel in the filedialog will therefore skip the following steps
		if image_filename != "":
			
			#Open image and remember it as the source image
			self.img_source = Image.open(image_filename)
			
			#Set it to the current plotting object
			self.display_type.set(original_image_display_name)
			self.img = self.img_source
			
			#Determine smallest zoom such that the full image fits in the canvas
			width_factor = self.canvas_width/self.img.size[0]
			height_factor = self.canvas_height/self.img.size[1]
			scale_factor = min(width_factor, height_factor)
			nx = round(scale_factor*self.img.size[0])
			ny = round(scale_factor*self.img.size[1])
				
			#Interpret the image with tkinter
			self.image_obj = ImageTk.PhotoImage(self.img)
			
			#Set the resulting scale in an internal variable
			self.scale = scale_factor
			self.original_scale = scale_factor
			
			#Delete any object that was currently displayed
			self.noimage_label.pack_forget()
			
			#Refresh the image
			self.redraw(x=self.canvas_width/2, y=self.canvas_height/2)
			
			#Reset zoom to center the image properly
			self.reset_zoom()
			
			#Refresh the user interface status
			self.status_var.set("Image opened: "+image_filename)
			
			#Refresh the state of the user interface window
			self.master.update()
	
	#Method to apply image threshold
	def threshold_image(self):
		
		#Verify that an image was loaded
		if self.img_source is None:
				
				#Update the user interface status
				self.status_var.set("Original Image not Loaded Yet... Use Open Image Button...")
				
				#Update the user interface
				self.master.update()
				
				#Return to caller
				return
		
		#Interpret the image into a matrix of numbers
		imdata_3d = np.array(self.img_source)
		
		#Only look at the blue channel of the image
		self.imdata = imdata_3d[:, :, 2]
		
		#Determine a value for the white background from the median
		self.background_median = np.median(self.imdata)
		
		#Create a mask for thresholded pixels
		self.mask_threshold = np.where(self.imdata < self.background_median*np.float(self.threshold_var.get())/100)
		
		#If an analysis polygon is set, select only pixels inside the polygon
		if self.polygon_alpha is not None:
			
			#Build a polygon from the data stored as internal variables
			coord_list = [(self.polygon_alpha[0], self.polygon_beta[0])]
			npoly = self.polygon_alpha.size
			for i in range(npoly-1):
				coord_list.append((self.polygon_alpha[i+1], self.polygon_beta[i+1]))
			#poly = geometry.Polygon(coord_list)
			poly = path.Path(coord_list)
			
			pts = np.vstack((self.mask_threshold[1], self.mask_threshold[0])).T
			contained = poly.contains_points(pts)
			
			#If no points are in the polygon then break with an error
			if np.max(contained) is False:
				
				#Refresh the user interface status
				self.status_var.set("No Thresholded Pixels were Located Inside of the Analysis Region")
				
				#Refresh the state of the user interface window
				self.master.update()
				
				#Return to caller	
				return
			
			#Only keep points inside the polygon
			self.mask_threshold = (self.mask_threshold[0][np.where(contained)[0]], self.mask_threshold[1][np.where(contained)[0]])
		
		#Create a thresholded image for display
		threshold_im_display = np.copy(imdata_3d)
		
		#Make the thresholded pixels red
		threshold_im_display[:, :, 0][self.mask_threshold] = 255
		threshold_im_display[:, :, 1][self.mask_threshold] = 0
		threshold_im_display[:, :, 2][self.mask_threshold] = 0
		
		#Transform the display array into a PIL image
		self.img_threshold = Image.fromarray(threshold_im_display)
		
		#Set the thresholded image as the currently plotted object
		self.display_type.set(threshold_image_display_name)
		self.img = self.img_threshold
		
		#Refresh the image that is displayed
		self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#Determine fraction of thresholded pixels
		thresholded_fraction = self.mask_threshold[0].size/self.imdata.size*100
		thresholded_fraction_str = "{0:.{1}f}".format(thresholded_fraction, 1)
		
		#Refresh the user interface status
		self.status_var.set("Image thresholded: "+thresholded_fraction_str+"% of all pixels were thresholded")
		
		#Refresh the state of the user interface window
		self.master.update()
	
	#Method to launch particle detection analysis
	def launch_psd(self):
		
		#Verify that an image was thresholded
		if self.mask_threshold is None:
			
			#Update the user interface status
			self.status_var.set("Image not Thresholded Yet... Use Threshold Image Button...")
			
			#Update the user interface
			self.master.update()
			
			#Return to caller
			return
		
		#Options not accessible in the GUI
		reference_threshold = 0.1
		nsmooth = 3
		maxcost = 0.35
		
		#Read options from internal variables
		max_cluster_axis = float(self.max_cluster_axis_var.get())
		min_surface_var = float(self.min_surface_var.get())
		min_roundness_var = float(self.min_roundness_var.get())
		
		#Sort the thresholded pixel indices by increasing brightness in the blue channel
		sort_indices = np.argsort(self.imdata[self.mask_threshold])
		self.mask_threshold = (self.mask_threshold[0][sort_indices], self.mask_threshold[1][sort_indices])
		
		#Create an image of the X and Y positions
		#Not needed
		#imx = np.tile(np.arange(self.imdata.shape[1]),(self.imdata.shape[0],1))
		#imy = np.tile(np.arange(self.imdata.shape[0]),(self.imdata.shape[1],1)).transpose()
		
		#Catalog image brightness
		imdata_mask = self.imdata[self.mask_threshold]
		
		#Create an empty list of clusters
		self.cluster_data = []
		
		#Start the creation of clusters
		counted = np.zeros(self.mask_threshold[0].size, dtype=bool)
		for i in range(self.mask_threshold[0].size):
			
			#Update status only on some steps
			if i%10 == 0:
				frac_counted = np.sum(counted)/self.mask_threshold[0].size*100
				frac_counted = np.minimum(frac_counted,99.9)
				frac_counted_str = "{0:.{1}f}".format(frac_counted, 1)
				self.status_var.set("Iteration #"+str(i)+"; Fraction of thresholded pixels that were analyzed: "+frac_counted_str+" %")
				self.master.update()
			
			#Select all thresholded pixels that were not yet included in a cluster
			#(we call those "open" pixels)
			iopen = np.where(counted == False)[0]
			
			#Break the loop if all pixels were counted
			if iopen.size == 0:
				break
			
			#Select the first thresholded pixel that was not yet included in a cluster
			icurrent = iopen[0]
			
			#Calculate distances between current pixel and all other open pixels
			dopen2 = (self.mask_threshold[0][icurrent] - self.mask_threshold[0][iopen])**2 + (self.mask_threshold[1][icurrent] - self.mask_threshold[1][iopen])**2
			
			#Select those within a reasonable distance only
			iwithinmax = np.where(dopen2 <= max_cluster_axis**2)
			
			#Skip this pixel if no other pixels are close enough
			if iwithinmax[0].size == 0:
				
				#Mark current pixel as counted
				counted[icurrent] = True
				
				#Skip this loop element
				continue
			
			#Do a quick clustering around the current pixel
			ipreclust = iopen[iwithinmax]
			qc_indices = self.quick_cluster(self.mask_threshold[0][ipreclust], self.mask_threshold[1][ipreclust], self.mask_threshold[0][icurrent], self.mask_threshold[1][icurrent])
			iclust = ipreclust[qc_indices]
			
			#Skip cluster if surface is too small
			if iclust.size < min_surface_var:
				
				#Mark current pixel as counted
				counted[icurrent] = True
				
				#Skip this loop element
				continue
			
			#Create a map of the blue channel flux
			imdata_mask_cluster = imdata_mask[iclust]
			
			#Unless the quick option is selected, now do a rejection of pixels based on the image values in the blue channel. The goal of this step is to break clumps of coffee grounds
			if self.quick_var.get() == 1:
				
				#The full cluster is adopted
				iclust_filtered = np.arange(iclust.size)
				
				#Some variables that will be needed as outputs
				maxcost_along_path = np.full(iclust.size, np.nan)
				cost = np.full(iclust.size, np.nan)
				
			else:
				
				#Order the cluster pixels w-r-t their distance from the current starting pixel
				dcurrent2 = (self.mask_threshold[0][iclust] - self.mask_threshold[0][icurrent])**2 + (self.mask_threshold[1][iclust] - self.mask_threshold[1][icurrent])**2
				iclust = iclust[np.argsort(dcurrent2)]
				
				#Identify the current pixel in this cluster
				icurrent_in_clust = np.where(iclust == icurrent)
				
				#Check that the current pixel was found only once
				if icurrent_in_clust[0].size != 1:
					raise ValueError("The starting pixel was not found in a cluster. This should never happen !")
				
				#Create a cost function along the positions of this cluster for pixel rejection
				cost = ( imdata_mask_cluster - imdata_mask[icurrent] )**2/self.background_median**2
				
				#Cost cannot be negative
				cost = np.maximum(cost, 0)
				
				#Loop on the cluster and check if the cost along the path to the starting pixel is exceeded
				iclust_filtered = np.copy(icurrent_in_clust[0])#== glist
				maxcost_along_path = np.full(iclust.size, np.nan)
				for ci in range(iclust.size):
					
					#Skip current pixel if it is the starting point
					if iclust[ci] == icurrent:
						continue
					
					#Make a list of all current pixels that are almost as dark as the reference pixel
					idark_in_list = np.where( imdata_mask_cluster[iclust_filtered] <= ( ( self.background_median - imdata_mask[icurrent] )*reference_threshold + imdata_mask[icurrent] ) )
					idark = iclust[iclust_filtered[idark_in_list[0]]]
					
					#There should be at least one dark pixel
					if idark.size == 0:
						raise ValueError("There should be at least one dark pixel in the cluster, this should never happen !")
					
					#Pick the nearest reference dark pixel
					if idark.size > 1:
						dist2 = ( self.mask_threshold[0][idark] - self.mask_threshold[0][iclust[ci]] )**2 + ( self.mask_threshold[1][idark] - self.mask_threshold[1][iclust[ci]] )**2
						idark = idark[np.argmin(dist2)]
					
					#If the current pixel was picked as a reference dark pixel then it is automatically accepted
					if iclust[ci] == idark:
						
						maxcost_along_path[ci] = 0.
						
					else:
						
						#Calculate distance between all points and a line that passes through pixel i and the reference dark pixel.
						x1 = self.mask_threshold[0][iclust[ci]]
						y1 = self.mask_threshold[1][iclust[ci]]
						x2 = self.mask_threshold[0][idark]
						y2 = self.mask_threshold[1][idark]
						x0 = self.mask_threshold[0][iclust]
						y0 = self.mask_threshold[1][iclust]
						
						ddline = np.abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1) / np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
						dd1 = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
						dd2 = np.sqrt((x2 - x0)**2 + (y2 - y0)**2)
						dd12 = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
						
						#Select all pixels within the path of the line
						ipath = np.where((ddline <= np.sqrt(2)) & (dd1 <= dd12) & (dd2 <= dd12))
						
						#Deduce distance projected on the line
						ddonline = np.sqrt(dd2[ipath[0]]**2 - ddline[ipath[0]]**2)
						
						#Sort by distance along the line
						ipath = ipath[0][np.argsort(ddonline)]
						
						#Interpolate cost along this path
						cost_path = cost[ipath]
						
						#Boxcar-sum the cost along the path
						if nsmooth > cost_path.size:
							cost_path_sm = self.smooth(cost_path, nsmooth)*nsmooth
						else:
							cost_path_sm = np.full(cost_path.size, np.sum(cost_path))
						
						#Find the maximum cost along the path
						maxcost_along_path[ci] = np.max(cost_path_sm)
					
					#If the cost does not go above the threshold then adopt this pixel
					if maxcost_along_path[ci] < maxcost:
						iclust_filtered = np.append(iclust_filtered, ci)
			
			#Mark the current pixels as counted
			counted[iclust] = True
			
			#Count the surface of this cluster
			surface = iclust_filtered.size
			
			#Skip cluster if surface is too small
			if surface < min_surface_var:
				continue
			
			#Create a list of positions and flux for this cluster
			xlist = self.mask_threshold[0][iclust[iclust_filtered]]
			ylist = self.mask_threshold[1][iclust[iclust_filtered]]
			zlist = imdata_mask_cluster[iclust_filtered]
			
			#Compute an approximate average centroid
			xmean = np.mean(xlist)
			ymean = np.mean(ylist)
			
			#Compute an approximate semi-major axis
			dlist = np.sqrt( ( xlist - xmean )**2 + ( ylist - ymean )**2 )
			dlist = np.maximum(dlist, 1e-4)
			axis = np.max(dlist)
			
			#Skip cluster if axis is too large
			if axis > max_cluster_axis:
				continue
			
			#Determine roundness from the ratio of thresholded pixels in the circle to the ratio of total pixels
			if surface == 1:
				roundness = 1
			else:
				roundness = float(surface) / ( np.pi*float(axis)**2 )
			
			#Skip cluster if roundness is too small
			if roundness < min_roundness_var:
				continue
			
			#Calculate shortest axis of the particle
			short_axis = surface/(np.pi*axis)
			
			#Suppose that the hidden axis is equal to the short axis and calculate volume
			#Here we also approximate the coffee particle as an ellipsoid
			volume = np.pi*short_axis**2*axis
			
			#Create a structure with the cluster information
			clusteri_data = {"CLUSTER_ID":i, "SURFACE":surface, "XLIST":xlist, "YLIST":ylist, "LONG_AXIS":axis, "ROUNDNESS":roundness, "VOLUME":volume, "SHORT_AXIS":short_axis, "XMEAN":xmean, "YMEAN":ymean, "XSTART":self.mask_threshold[0][icurrent], "YSTART":self.mask_threshold[1][icurrent], "ZLIST":zlist, "ICLUST_FILTERED":iclust[iclust_filtered], "ICLUST":iclust, "MAXCOST_ALONG_PATH":maxcost_along_path, "COST":cost}
			
			#Append cluser data with this dictionary
			self.cluster_data.append(clusteri_data)
		
		#Read useful cluster data
		self.nclusters = len(self.cluster_data)
		self.clusters_surface = np.full(self.nclusters, np.nan)
		self.clusters_long_axis = np.full(self.nclusters, np.nan)
		self.clusters_roundness = np.full(self.nclusters, np.nan)
		self.clusters_short_axis = np.full(self.nclusters, np.nan)
		self.clusters_volume = np.full(self.nclusters, np.nan)
		for i in range(self.nclusters):
			self.clusters_surface[i] = self.cluster_data[i]["SURFACE"]
			self.clusters_long_axis[i] = self.cluster_data[i]["LONG_AXIS"]
			self.clusters_roundness[i] = self.cluster_data[i]["ROUNDNESS"]
			self.clusters_short_axis[i] = self.cluster_data[i]["SHORT_AXIS"]
			self.clusters_volume[i] = self.cluster_data[i]["VOLUME"]
		
		#Set the status to completed
		self.status_var.set("Particle Detection Analysis Done ! Creating Cluster Map Image...")
		self.master.update()
		
		#Interpret the source image into a matrix of numbers
		imdata_3d = np.array(self.img_source)
		
		#Create a cluster image for display
		cluster_map_display = np.copy(imdata_3d)
		
		#Loop on clusters to display outlines
		for i in range(self.nclusters):
			
			#Read some cluster data
			xlist = self.cluster_data[i]["XLIST"]
			ylist = self.cluster_data[i]["YLIST"]
			surface = self.cluster_data[i]["SURFACE"]
			
			#Loop on cluster pixels
			for l in range(surface):
				
				#Count neighbors
				ineigh = np.where((np.abs(xlist - xlist[l]) <= 1) & (np.abs(ylist - ylist[l]) <= 1))
				
				#Skip if the pixel is surrounded
				if ineigh[0].size == 9:
					continue
				
				#Mark edge pixel in red
				cluster_map_display[xlist[l], ylist[l], 0] = 255
				cluster_map_display[xlist[l], ylist[l], 1] = 0
				cluster_map_display[xlist[l], ylist[l], 2] = 0
			
			#Mark cluster center in blue
			xmean = int(round(self.cluster_data[i]["XMEAN"]))
			ymean = int(round(self.cluster_data[i]["YMEAN"]))
			cluster_map_display[xmean, ymean, 0] = 40
			cluster_map_display[xmean, ymean, 1] = 40
			cluster_map_display[xmean, ymean, 2] = 255
		
		#Transform the display array into a PIL image
		self.img_clusters = Image.fromarray(cluster_map_display)
		
		#Set the cluster map image as the currently plotted object
		self.display_type.set(outlines_image_display_name)
		self.img = self.img_clusters
		
		#Refresh the image that is displayed
		self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#Refresh the user interface status
		self.status_var.set("Particle Detection Analysis Done ! Cluster Map Image is Now Displayed...")
		
		#Refresh the state of the user interface window
		self.master.update()
	
	#Method for a smoothing by moving average
	def smooth(self, x, window_size):
		window = np.ones(int(window_size))/float(window_size)
		return np.convolve(x, window, "same")
	
	#Method for quick clustering of pixels near a coffee particle
	def quick_cluster(self, xlist, ylist, xstart, ystart):
		#self.mask_threshold[0][ipreclust], self.mask_threshold[1][ipreclust], self.mask_threshold[0][icurrent], self.mask_threshold[1][icurrent]
		
		#The first pixels to be checked will be those around the starting point
		xcheck = np.array([xstart])
		ycheck = np.array([ystart])
		
		#Create copies of xlist and ylist that will decay
		#Those are the lists of pixels that still need to be considered
		xlist_decay = np.copy(xlist)
		ylist_decay = np.copy(ylist)
		ilist_decay = np.arange(xlist.size)
		
		#Remove the starting pixel from the decaying lists
		istart = np.where((xlist_decay == xstart) & (ylist_decay == ystart))
		if istart[0].size != 0:
			xlist_decay = np.delete(xlist_decay, istart[0])
			ylist_decay = np.delete(ylist_decay, istart[0])
			ilist_decay = np.delete(ilist_decay, istart[0])
		
		#Initialize a vector of output indices
		iout = istart[0]
		
		#Start a loop on all pixels that need to be checked
		for i in range(xlist.size):
			
			#Select all neighbor pixels
			isel = np.where( ( np.abs(xlist_decay - xcheck[0]) + np.abs(ylist_decay - ycheck[0]) ) <= 1.001)
			
			#If no neighbor pixels are found, mark the current pixel as checked and move on
			if isel[0].size == 0:
				
				#If this was the only pixel that currently needed to be checked break the loop
				if xcheck.size == 1:
					break
				
				#Remove current pixel from the list to be checked
				xcheck = np.delete(xcheck, 0)
				ycheck = np.delete(ycheck, 0)
				
				#Skip this element of the loop
				continue
			
			#If some neighbor pixels are found add then to the output list
			iout = np.append(iout, ilist_decay[isel[0]])
			
			#Also add them to the list of pixels to be checked next
			xcheck = np.append(xcheck, xlist_decay[isel[0]])
			ycheck = np.append(ycheck, ylist_decay[isel[0]])
			
			#Remove the pixel that was just checked
			xcheck = np.delete(xcheck, 0)
			ycheck = np.delete(ycheck, 0)
			
			#If the decaying lists are empty stop the whole process
			if isel[0].size == xlist_decay.size:
				break
			
			#Remove the newly selected pixels from the decaying lists
			xlist_decay = np.delete(xlist_decay, isel[0])
			ylist_decay = np.delete(ylist_decay, isel[0])
			ilist_decay = np.delete(ilist_decay, isel[0])
			
		#Return the final list of indices to the caller
		return iout
	
	def psd_hist_from_data(self, source, hist_color=[147, 36, 30], hist_label=None, bins_input=None, histtype="bar"):
		
		#Read pixel scale from internal variables
		pixel_scale = float(source.pixel_scale_var.get())
		
		#Initiate empty data
		data = None
		self.xlabel = None
		
		#Default label
		if hist_label is None:
			hist_label = self.data_label_var.get()
		
		# === Define X axis as required ===
		
		#If X data is diameter
		if "vs Diameter" in self.histogram_type.get():
			data = 2*np.sqrt(source.clusters_long_axis*source.clusters_short_axis)/pixel_scale
			self.xlabel = "Particle Diameter (mm)"
		
		#If X data is surface
		if "vs Surface" in self.histogram_type.get():
			data = source.clusters_surface/pixel_scale**2
			self.xlabel = "Particle Surface (mm$^2$)"
		
		#If X data is volume
		if "vs Volume" in self.histogram_type.get():
			data = source.clusters_volume/pixel_scale**3
			self.xlabel = "Particle Volume (mm$^3$)"
		
		if "Extraction Yield Distribution" in self.histogram_type.get():
			#Not coded yet
			#Create a subroutine that computes the extraction Yield
			self.xlabel = "Extraction Yield (%)"
			
			#Refresh the user interface status
			self.status_var.set("This option has not been coded yet...")
			
			#Refresh the state of the user interface window
			self.master.update()
			
			return
		
		#If data is still empty then the selection was not recognized
		if data is None:
			raise ValueError("The histogram option "+self.histogram_type.get()+" was not recognized properly")
		
		#Initiate empty data
		data_weights = None
		density = False
		self.ylabel = None
		
		#If Y data is the number of particles
		if "Number vs" in self.histogram_type.get():
			data_weights = np.full(source.nclusters, 1)
			density = False
			self.ylabel = "Number of Particles"
		
		#If Y data is the surface
		if "Surface vs" in self.histogram_type.get():
			data_weights = source.clusters_surface
			density = True
			self.ylabel = "Total Particle Surface Fraction"
			
		#If Y data is the mass (proportional to volume because we assume all particles have the same mass density)
		if "Mass vs" in self.histogram_type.get():
			data_weights = source.clusters_volume
			self.ylabel = "Total Particle Mass Fraction"
			density = True
			
		if "Extract vs" in self.histogram_type.get():
			density = True
			self.ylabel = "Beverage Mass Fraction"
			
			#Refresh the user interface status
			self.status_var.set("This option has not been coded yet...")
			
			#Refresh the state of the user interface window
			self.master.update()
			
			return
		
		#If weights are still empty then the selection was not recognized
		if data_weights is None:
			raise ValueError("The histogram option "+self.histogram_type.get()+" was not recognized properly")
		
		#Read x range from internal variables
		if self.xaxis_auto_var.get() == 1:
			xmin = np.nanmin(data)
			xmax = np.nanmax(data)
		else:
			xmin = float(self.xmin_var.get())
			xmax = float(self.xmax_var.get())
		
		#Set histogram range
		histrange = np.array([xmin, xmax])
		
		if bins_input is None:
			#Read number of bins from internal variables
			if self.nbins_auto_var.get() == 1:
				#Count the number of bins that are required
				if self.xlog_var.get() == 1:
					nbins = int(np.ceil( np.log10(float(histrange[1]) - np.log10(histrange[0]))/float(default_log_binsize) ))
				else:
					nbins = int(np.ceil( float(histrange[1] - histrange[0])/float(default_binsize) ))
			else:
				nbins = int(np.round(float(self.nbins_var.get())))
			
			#Create a list of bins for plotting
			if self.xlog_var.get() == 1:
				bins_input = np.logspace(np.log10(histrange[0]), np.log10(histrange[1]), nbins)
			else:
				bins_input = np.linspace(histrange[0], histrange[1], nbins)
		
		#Plot the histogram
		hist_color_fm = (hist_color[0]/255, hist_color[1]/255, hist_color[2]/255)
		ypdf, xpdf, patches = plt.hist(data, bins_input, histtype=histtype, color=hist_color_fm, label=hist_label, weights=data_weights, density=density, lw=2, rwidth=.8)
		
		return bins_input
	
	#Method to create histogram
	def create_histogram(self, event):
		
		#Verify that clusters were defined
		if self.nclusters is None:
			
			#Update the user interface status
			self.status_var.set("Coffee Particles not Detected Yet... Use Launch Particle Detection Button...")
			
			#Update the user interface
			self.master.update()
			
			#Return to caller
			return
		
		#Check that a physical size was set
		if self.pixel_scale_var.get() == "None":
			
			#Update the user interface status
			self.status_var.set("The Pixel Scale Has Not Been Defined Yet... Use the Left Mouse Button to Draw a Line on a Reference Object and Choose a Reference Length in mm...")
			
			#Update the user interface
			self.master.update()
			
			#Return to caller
			return
		
		#Size of figure in pixels
		figsize_pix = (self.canvas_width, self.canvas_height)
		
		#Transform these in pixels with the default DPI value
		my_dpi = 192
		figsize_inches = (figsize_pix[0]/my_dpi, figsize_pix[1]/my_dpi)
		
		#Prepare a figure to display the plot
		fig = plt.figure(figsize=figsize_inches, dpi=my_dpi)
		
		# === Generate histogram from data ===
		
		bins_input = self.psd_hist_from_data(self)
		
		#If comparison data is loaded plot it
		if self.comparison.nclusters is not None:
			self.psd_hist_from_data(self.comparison, hist_color=[74, 124, 179], hist_label=self.comparison_data_label_var.get(), bins_input=bins_input, histtype="step")
		#self.comparison_clusters_surface = dataframe["SURFACE"].values
		#self.comparison_clusters_roundness = dataframe["ROUNDNESS"].values
		#self.comparison_clusters_long_axis = dataframe["LONG_AXIS"].values
		#self.comparison_clusters_short_axis = dataframe["SHORT_AXIS"].values
		#self.comparison_clusters_volume = dataframe["VOLUME"].values
		#self.comparison_nclusters = self.comparison_clusters_surface.size
		#self.comparison_pixel_scale = dataframe["PIXEL_SCALE"].values[0]
		
		#Make xlog if needed
		if self.xlog_var.get() == 1:
			plt.xscale("log")
		
		#Set X and Y labels
		plt.xlabel(self.xlabel, fontsize=16)
		plt.ylabel(self.ylabel, fontsize=16)
		
		#Add legend
		plt.legend()
		
		# Change size and font of tick labels
		#tick_fontsize = 14
		ax = plt.gca()
		#for tick in ax.xaxis.get_major_ticks():
		#	tick.label1.set_fontsize(tick_fontsize)
		#for tick in ax.yaxis.get_major_ticks():
		#	tick.label1.set_fontsize(tick_fontsize)
		
		#Set the label fonts
		minortick_fontsize = 5
		majortick_fontsize = 8
		plt.tick_params(axis='both', which='major', labelsize=majortick_fontsize)
		
		#if self.xlog_var.get() == 1:
		#	plt.tick_params(axis='x', which='major', labelrotation=90, pad=None)
		#	plt.tick_params(axis='x', which='minor', labelrotation=90, labelsize=minortick_fontsize)
		
		#Make ticks longer and thicker
		ax.tick_params(axis="both", length=5, width=2, which="major")
		ax.tick_params(axis="both", length=4, width=1, which="minor")
		
		#Use a tight layout
		plt.tight_layout()
		
		#In xlog mode do not use scientific notation
		if self.xlog_var.get() == 1:
			ax.xaxis.set_minor_formatter(mticker.LogFormatter())
			ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
		
		# === Transform the figure to a PIL object ===
		
		#Draw the figure in the buffer
		fig.canvas.draw()
		
		#Tranform the figure in a numpy array
		figdata = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
		figdata = figdata.reshape(fig.canvas.get_width_height()[::-1] + (3,))
		
		#Read the shape of the numpy array
		fw, fh, fd = figdata.shape
		
		#Transform numpy array in a PIL image
		self.img_histogram = Image.frombytes("RGB", (fh, fw), figdata)
		
		#Set the cluster map image as the currently plotted object
		self.display_type.set(histogram_image_display_name)
		self.img = self.img_histogram
		
		#Remove the no label image if no image was loaded yet
		if self.img_source is None:
			self.noimage_label.pack_forget()
		
		#Refresh the image that is displayed
		self.redraw(x=self.last_image_x, y=self.last_image_y)
		
		#Refresh the user interface status
		self.status_var.set("Histogram Image is Now Displayed...")
		
		#Refresh the state of the user interface window
		self.master.update()
	
	#Method to load data from disk
	def load_data(self):
		
		#Update root to avoid problems with file dialog
		self.master.update()
		
		#Invoke a file dialog to select data file
		csv_data_filename = filedialog.askopenfilename(initialdir=self.output_dir,title="Select a CSV data file",filetypes=(("csv files","*.csv"),("all files","*.*")))
		
		#Create a Pandas dataframe from the CSV data
		dataframe = pd.read_csv(csv_data_filename)
		
		#Ingest data in system variables
		self.clusters_surface = dataframe["SURFACE"].values
		self.clusters_roundness = dataframe["ROUNDNESS"].values
		self.clusters_long_axis = dataframe["LONG_AXIS"].values
		self.clusters_short_axis = dataframe["SHORT_AXIS"].values
		self.clusters_volume = dataframe["VOLUME"].values
		self.nclusters = self.clusters_surface.size
		self.pixel_scale_var.set(str(dataframe["PIXEL_SCALE"].values[0]))
		
		#Update the user interface status
		self.status_var.set("Data Loaded into Memory...")
		
		#Refresh histogram
		self.create_histogram(None)
		
	#Method to load comparison data from disk
	def load_comparison_data(self):
		
		#Update root to avoid problems with file dialog
		self.master.update()
		
		#Invoke a file dialog to select data file
		csv_data_filename = filedialog.askopenfilename(initialdir=self.output_dir,title="Select a CSV data file",filetypes=(("csv files","*.csv"),("all files","*.*")))
		
		#Create a Pandas dataframe from the CSV data
		dataframe = pd.read_csv(csv_data_filename)
		
		#Ingest data in system variables
		self.comparison.nclusters = dataframe["SURFACE"].values.size
		self.comparison.clusters_surface = dataframe["SURFACE"].values
		self.comparison.clusters_roundness = dataframe["ROUNDNESS"].values
		self.comparison.clusters_long_axis = dataframe["LONG_AXIS"].values
		self.comparison.clusters_short_axis = dataframe["SHORT_AXIS"].values
		self.comparison.clusters_volume = dataframe["VOLUME"].values
		
		self.comparison.pixel_scale_var = StringVar()
		self.comparison.pixel_scale_var.set(str(dataframe["PIXEL_SCALE"].values[0]))
		
		#Activate the comparison data label
		self.comparison_data_label_id.config(state=NORMAL)
		
		#If there is already a histogram in play, refresh it
		if self.img_histogram is not None:
			self.create_histogram(None)
		
		#Update the user interface status
		self.status_var.set("Comparison Data Loaded into Memory...")
	
	#Method to flush comparison data
	def flush_comparison_data(self):
		
		#Reset system variables
		self.comparison.clusters_surface = None
		self.comparison.clusters_roundness = None
		self.comparison.clusters_long_axis = None
		self.comparison.clusters_short_axis = None
		self.comparison.clusters_volume = None
		self.comparison.nclusters = None
		self.comparison.pixel_scale_var.set(None)
		
		#Deactivate the comparison data label
		self.comparison_data_label_id.config(state=DISABLED)
		
		#If there is already a histogram in play, refresh it
		if self.img_histogram is not None:
			self.create_histogram(None)
		
		#Update the user interface status
		self.status_var.set("Comparison Data Flushed from Memory...")
		
	#Method to save data to disk
	def save_data(self):
		
		#Verify if PSD analysis was done
		if self.cluster_data is None:
			
			#Update the user interface status
			self.status_var.set("Particles not Detected Yet... Use Launch Particle Detection Button...")
			
			#Update the user interface
			self.master.update()
			
			#Return to caller
			return
		
		#Create a Pandas dataframe for easier saving
		dataframe = pd.DataFrame({"SURFACE":self.clusters_surface,"ROUNDNESS":self.clusters_roundness,"SHORT_AXIS":self.clusters_short_axis,"LONG_AXIS":self.clusters_long_axis,"VOLUME":self.clusters_volume,"PIXEL_SCALE":float(self.pixel_scale_var.get())})
		dataframe.index.name = "ID"
		
		#Save file to CSV
		filename = self.session_name_var.get()+"_data.csv"
		full_filename = self.output_dir+os.sep+filename
		dataframe.to_csv(full_filename)
		
		#Update the user interface status
		self.status_var.set("Data Saved to "+filename+"...")
		
		#Update the user interface
		self.master.update()
	
	#Method to save figure to disk
	def save_histogram(self):
		
		#Verify that a figure exists
		if self.img is None:
			
			#Update the user interface status
			self.status_var.set("No View Created Yet...")
			
			#Update the user interface
			self.master.update()
			
			#Return to caller
			return
		
		#Update the user interface status
		self.status_var.set("Saving View...")
		
		#Update the user interface
		self.master.update()
		
		#If display is source image
		image_code = ""
		if self.display_type.get() == original_image_display_name:
			image_code = "source_image"
		
		#If display is threshold image
		if self.display_type.get() == threshold_image_display_name:
			image_code = "threshold_image"
		
		#If display is outlines image
		if self.display_type.get() == outlines_image_display_name:
			image_code = "outlines_image"
				
		#If display is histogram
		if self.display_type.get() == histogram_image_display_name:
			#Determine filename code for this type of histogram
			ihist = np.where(np.array(self.hist_choices) == self.histogram_type.get())
			image_code = self.hist_codes[ihist[0][0]]
		
		#Save file to PNG
		filename = self.session_name_var.get()+"_hist_"+image_code+".png"
		full_filename = self.output_dir+os.sep+filename
		
		self.img.save(full_filename)
		
		#Update the user interface status
		self.status_var.set("Current View Saved to "+filename+"...")
		
		#Update the user interface
		self.master.update()
	
	#Method to quit user interface
	def quit_gui(self):
		root.destroy()
	
	#Method to display help
	def launch_help(self):
		webbrowser.open("https://www.dropbox.com/s/m2af0aer2e17xie/coffee_grind_size_manual.pdf?dl=0")
	
	def view_statistics(self):
		
		#Define some padding parameters
		xpad = 20
		ypad = 1
		current_row = 0
		
		#Create a popup help window
		help_window = Toplevel()
		
		#Create a frame for the text
		help_frame = Frame(help_window, width=400, height=300)
		help_frame.pack()
		
		#Prevent the frame to shrink when labels are placed in it
		#help_frame.grid_propagate(False)
		
		#Set the window title
		help_window.title = "Help"# - Coffee Particle Size Distribution by Jonathan Gagne"
		
		#Set a vertical space
		separator_label = Label(help_frame, text="")
		separator_label.grid(row=current_row)
		current_row += 1
		
		#Display title
		title_label = Label(help_frame, text="Help - Coffee Particle Size Distribution", font='Helvetica 18 bold', padx=xpad, pady=ypad)
		title_label.grid(row=current_row)
		current_row += 1
		
		#Display text
		separator_label = Label(help_frame, text="")
		separator_label.grid(row=current_row)
		current_row += 1
		
		t1_label = Label(help_frame,text="This program is intended to measure the size distribution of coffee grounds from a picture \ntaken on a white background.", padx=xpad, pady=ypad, justify=LEFT)
		t1_label.grid(column=0, row=current_row, sticky=W)
		current_row += 1
		
		#Display subtitle
		separator_label = Label(help_frame, text="")
		separator_label.grid(row=current_row)
		current_row += 1
		
		subtitle_label = Label(help_frame, text="Image Thresholding", font='Helvetica 16 bold', padx=xpad, pady=ypad)
		subtitle_label.grid(row=current_row, sticky=W)
		current_row += 1
		
		separator_label = Label(help_frame, text="")
		separator_label.grid(row=current_row)
		current_row += 1
		
		#Display more text
		t2_label = Label(help_frame, text="The first step after loading an image is to threshold it. The program will use the blue channel \nof the color image because coffee grinds tend to be brown, which is very faint in the blue \nchannel, therefore increasing contrast with the white background. A reference for the white \nbackground will be determined from the median value of the image, and all pixels darker than \nthe threshold fraction of the white background will be grouped as potential coffee grounds.", padx=xpad, pady=ypad, justify=LEFT)
		t2_label.grid(column=0, row=current_row, sticky=W)
		current_row += 1
		
		#Display subtitle
		separator_label = Label(help_frame, text="")
		separator_label.grid(row=current_row)
		current_row += 1
		
		subtitle_label = Label(help_frame, text="Particle Detection", font='Helvetica 16 bold', padx=xpad, pady=ypad)
		subtitle_label.grid(row=current_row, sticky=W)
		current_row += 1
		
		separator_label = Label(help_frame, text="")
		separator_label.grid(row=current_row)
		current_row += 1
		
		#Display more text
		t2_label = Label(help_frame, text="The program will first order all thresholded pixels from the darkest to the brightest, and will \nstart working with the darkest ones first because they are more likely to be near the core of \na coffee particle. It will then start from one pixel and use it as the seed of a cluster. Any \nimmediately adjacent pixel that is also thresholded will be included in the cluster, and the \nones adjacent to them will also be included until no thresholded pixels touch the current \ncluster. Once a cluster is completed, various steps will be taken to determine whether it is \nvalid [MORE].", padx=xpad, pady=ypad, justify=LEFT)
		t2_label.grid(column=0, row=current_row, sticky=W)
		current_row += 1
		
		#Quit button
		quit_button = Button(help_frame, text="Quit", padx=20, pady=20, command=lambda : help_window.destroy())
		quit_button.grid(row=current_row, column=0)

# === Main loop and call to the user interface window ===

#Invoke tkinter package
root = Tk()

#Call the user interface
coffeegrindsize_GUI(root)

#Refresh user interface in a try statement to avoid UTF-8 crashes when the user interface tries to interpret unrecognized inputs like an Apple trackpad
while True:
	try:
		root.mainloop()
		break
	except UnicodeDecodeError:
		pass