########################################################################
# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/Core/Utilities/Graphs/PlotBase.py,v 1.9 2009/11/03 15:56:47 atsareg Exp $
########################################################################

""" PlotBase is a base class for various Graphs plots
    
    The DIRAC Graphs package is derived from the GraphTool plotting package of the
    CMS/Phedex Project by ... <to be added>
"""

__RCSID__ = "$Id: PlotBase.py,v 1.9 2009/11/03 15:56:47 atsareg Exp $"

import types, random
from DIRAC.Core.Utilities.Graphs.Palette import Palette
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from DIRAC.Core.Utilities.Graphs.GraphUtilities import *
from matplotlib.axes import Axes    
from matplotlib.pylab import setp

class PlotBase:

  def __init__(self,data=None,axes=None,*aw,**kw):
  
    self.ax_contain = axes
    self.canvas = None
    self.figure = None
    if self.ax_contain:
      self.figure = self.ax_contain.get_figure()
      self.canvas = self.figure.canvas
      self.dpi = self.ax_contain.figure.get_dpi()
      self.ax_contain.set_axis_off()
    self.prefs = evalPrefs(*aw,**kw)
    self.coords = {}
    self.palette = Palette()

  def dumpPrefs(self):
  
    for key in self.prefs:
      print key.rjust(20),':',str(self.prefs[key]).ljust(40)
      
  def setAxes(self,axes):
  
    self.ax_contain = axes  
    self.ax_contain.set_axis_off()
    self.figure = self.ax_contain.get_figure()
    self.canvas = self.figure.canvas
    self.dpi = self.ax_contain.figure.get_dpi()

  def draw(self):
  
    prefs = self.prefs
    dpi = self.ax_contain.figure.get_dpi()
    
    # Update palette
    palette = prefs.get('colors',{})
    if palette:
      self.palette.addPalette(palette)
    
    
    xlabel = prefs.get('xlabel','') 
    ylabel = prefs.get('ylabel','') 
    xticks_flag = prefs.get('xticks',True)
    yticks_flag = prefs.get('yticks',True)
    
    text_size = prefs['text_size']
    text_padding = prefs['text_padding']
    
    label_text_size = prefs.get('label_text_size',text_size)
    label_text_size_point = pixelToPoint(label_text_size,dpi)
    tick_text_size = prefs.get('tick_text_size',text_size)
    tick_text_size_point = pixelToPoint(tick_text_size,dpi)
    
    ytick_length = prefs.get('ytick_length',7*tick_text_size)
    
    plot_title = prefs.get('plot_title','')
    if not plot_title or plot_title == 'NoTitle':
      plot_title_size = 0
      plot_title_padding = 0
    else:
      plot_title_size = prefs.get('plot_title_size',text_size)
      plot_title_padding = prefs.get('plot_text_padding',text_padding)  
    plot_title_size_point = pixelToPoint(plot_title_size,dpi)

    plot_padding = prefs['plot_padding']
    plot_left_padding = prefs.get('plot_left_padding',plot_padding)
    plot_right_padding = prefs.get('plot_right_padding',0)
    plot_bottom_padding = prefs.get('plot_bottom_padding',plot_padding)
    plot_top_padding = prefs.get('plot_top_padding',0)
    frame_flag = prefs['frame']
    
    # Create plot axes, and set properties
    left,bottom,width,height = self.ax_contain.get_window_extent().bounds
    l,b,f_width,f_height = self.figure.get_window_extent().bounds
        
    # Space needed for labels and ticks
    x_label_space = 0    
    if xticks_flag:
      x_label_space += tick_text_size*1.5
    if xlabel:
      x_label_space += label_text_size*1.5
    y_label_space = 0
    if yticks_flag:
      y_label_space += ytick_length
    if ylabel:
      y_label_space += label_text_size*1.5  
        
    ax_plot_rect = (float(plot_left_padding+left+y_label_space)/f_width,
                    float(plot_bottom_padding+bottom+x_label_space)/f_height,
                    float(width-plot_left_padding-plot_right_padding-y_label_space)/f_width,
                    float(height-plot_bottom_padding-plot_top_padding-x_label_space- \
                          plot_title_size-2*plot_title_padding)/f_height)
    ax = Axes(self.figure,ax_plot_rect)                
    if prefs['square_axis']:
      l,b,a_width,a_height = ax.get_window_extent().bounds
      delta = abs(a_height-a_width)
      if a_height > a_width:
        a_height = a_width
        ax_plot_rect = (float(plot_left_padding+left)/f_width,
                        float(plot_bottom_padding+bottom+delta/2.)/f_height,
                        float(width-plot_left_padding-plot_right_padding)/f_width,
                        float(height-plot_bottom_padding-plot_title_size-2*plot_title_padding-delta)/f_height)
      else:
        a_width = a_height
        ax_plot_rect = (float(plot_left_padding+left+delta/2.)/f_width,
                        float(plot_bottom_padding+bottom)/f_height,
                        float(width-plot_left_padding-delta)/f_width,
                        float(height-plot_bottom_padding-plot_title_size-2*plot_title_padding)/f_height)
      ax.set_position(ax_plot_rect)                  
                              
                    
    self.figure.add_axes(ax)   
    self.ax = ax                
    frame = ax.patch
    frame.set_fill( False )

    if frame_flag.lower() == 'off':
      self.ax.set_axis_off()
      self.log_xaxis = False
      self.log_yaxis = False
    else:  
      # If requested, make x/y axis logarithmic
      if prefs.get('log_xaxis','False').find('r') >= 0:
        ax.semilogx()
        self.log_xaxis = True
      else:
        self.log_xaxis = False
      if prefs.get('log_yaxis','False').find('r') >= 0:
        ax.semilogy()
        self.log_yaxis = True
      else:
        self.log_yaxis = False

      if xticks_flag:
        setp( ax.get_xticklabels(), family=prefs['font_family'] )
        setp( ax.get_xticklabels(), fontname=prefs['font'] )
        setp( ax.get_xticklabels(), size=tick_text_size_point)
      else:
        setp( ax.get_xticklabels(), size=0)  

      if yticks_flag: 
        setp( ax.get_yticklabels(), family=prefs['font_family'] )
        setp( ax.get_yticklabels(), fontname=prefs['font'] )
        setp( ax.get_yticklabels(), size=tick_text_size_point )
      else:  
        setp( ax.get_yticklabels(), size=0 )

      setp( ax.get_xticklines(),  markeredgewidth=pixelToPoint(0.5,dpi) )
      setp( ax.get_xticklines(),  markersize=pixelToPoint(text_size/2.,dpi) )
      setp( ax.get_yticklines(),  markeredgewidth=pixelToPoint(0.5,dpi) )
      setp( ax.get_yticklines(),  markersize=pixelToPoint(text_size/2.,dpi) )
      setp( ax.get_xticklines(),  zorder=4.0 )

      line_width = prefs.get('line_width',1.0)
      frame_line_width  = prefs.get('frame_line_width',line_width)
      grid_line_width  = prefs.get('grid_line_width',0.1)
      plot_line_width = prefs.get('plot_line_width',0.1)

      setp( ax.patch, linewidth=pixelToPoint(plot_line_width,dpi) )
      setp( ax.axesFrame, linewidth=pixelToPoint(frame_line_width,dpi) )
      #setp( ax.axvline(), linewidth=pixelToPoint(1.0,dpi) ) 
      axis_grid_flag = prefs.get('plot_axis_grid',True)
      if axis_grid_flag:  
        ax.grid( True, color='#555555', linewidth=pixelToPoint(grid_line_width,dpi) )
      
      plot_axis_flag = prefs.get('plot_axis',True)
      if plot_axis_flag:
      # Set labels
        if xlabel:
          t = ax.set_xlabel( xlabel )
          t.set_family(prefs['font_family'])
          t.set_fontname(prefs['font'])
          t.set_size(label_text_size)
  
        if ylabel:
          t = ax.set_ylabel( ylabel )
          t.set_family(prefs['font_family'])
          t.set_fontname(prefs['font'])
          t.set_size(label_text_size) 
      else:
        self.ax.set_axis_off()    
        

    # Create a plot title, if necessary
    if plot_title:    
      self.ax.title = self.ax.text( 0.5, 
                                    1.+float(plot_title_padding)/height,
                                    plot_title,
                                    verticalalignment='bottom', 
                                    horizontalalignment='center',
                                    size = pixelToPoint(plot_title_size,dpi),
                                    family=prefs['font_family'],
                                    fontname=prefs['font']
                                    )
      self.ax.title.set_transform(self.ax.transAxes)                                                  
      self.ax.title.set_family( prefs['font_family'] )
      self.ax.title.set_fontname( prefs['font'] )
                                              
     