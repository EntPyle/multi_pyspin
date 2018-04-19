#!/usr/bin/env python

""" GUI for setting up stereo cameras with PySpin library """

# pylint: disable=line-too-long,global-statement

import sys
import threading
from warnings import warn
from tkinter import messagebox

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from matplotlib.widgets import Slider

import stereo_pyspin

# These are min/max values for BFS-U3-32S4M camera
__FPS_MIN = 1
__FPS_MAX = 118
__GAIN_MIN = 0        # Units are dB
__GAIN_MAX = 47       # Units are dB
__EXPOSURE_MIN = 5e-6 # Units are seconds
__EXPOSURE_MAX = 30   # Units are seconds

# Set up streaming params
__THREAD_PRIMARY = None
__THREAD_SECONDARY = None
__STREAM_PRIMARY = False
__STREAM_SECONDARY = False
__IMSHOW_PRIMARY_DICT = {'imshow': None, 'imshow_size': None}
__IMSHOW_SECONDARY_DICT = {'imshow': None, 'imshow_size': None}
__HIST_PRIMARY_DICT = {'bar': None}
__HIST_SECONDARY_DICT = {'bar': None}

# GUI
__GUI_DICT = None

# -------------- #
# Callbacks      #
# -------------- #

def __message_box_func_wrapper(func):
    """ wraps function in try/except and pops up message box with exception """

    def __wrapped_func(*args, **kwargs):
        """ wrapped function """

        try:
            func(*args, **kwargs)
        except Exception as e: # pylint: disable=broad-except,invalid-name
            messagebox.showerror("Error", str(e))
    return __wrapped_func

def __find_primary(_=None):
    """ Finds primary camera """

    print('Finding primary camera...')
    find_text = __GUI_DICT['cam_plot_primary_dict']['find_text'].text
    if find_text.isdigit():
        stereo_pyspin.find_primary(int(find_text))
    else:
        stereo_pyspin.find_primary(find_text)

def __find_secondary(_=None):
    """ Finds secondary camera """

    print('Finding secondary camera...')
    find_text = __GUI_DICT['cam_plot_secondary_dict']['find_text'].text
    if find_text.isdigit():
        stereo_pyspin.find_secondary(int(find_text))
    else:
        stereo_pyspin.find_secondary(find_text)

def __init_primary(_=None):
    """ Initializes primary camera """

    print('Initializing primary camera...')
    init_text = __GUI_DICT['cam_plot_primary_dict']['init_text'].text
    stereo_pyspin.init_primary(init_text)

def __init_secondary(_=None):
    """ Initializes secondary camera """

    print('Initializing secondary camera...')
    init_text = __GUI_DICT['cam_plot_secondary_dict']['init_text'].text
    stereo_pyspin.init_secondary(init_text)

def __start_acquisition_primary(_=None):
    """ Starts acquisition of primary camera """
    global __THREAD_PRIMARY, __STREAM_PRIMARY

    print('Starting primary camera acquisition...')
    # Make sure it isn't already streaming
    if not __STREAM_PRIMARY:
        stereo_pyspin.start_acquisition_primary()
        __STREAM_PRIMARY = True
        __THREAD_PRIMARY = threading.Thread(target=__stream_image_primary)
        __THREAD_PRIMARY.start()

def __start_acquisition_secondary(_=None):
    """ Starts acquisition of secondary camera """
    global __THREAD_SECONDARY, __STREAM_SECONDARY

    print('Starting secondary camera acquisition...')
    # Make sure it isn't already streaming
    if not __STREAM_SECONDARY:
        stereo_pyspin.start_acquisition_secondary()
        __STREAM_SECONDARY = True
        __THREAD_SECONDARY = threading.Thread(target=__stream_image_secondary)
        __THREAD_SECONDARY.start()

def __stop_acquisition_primary(_=None):
    """ Stops acquisition of primary camera """
    global __THREAD_PRIMARY, __STREAM_PRIMARY

    # Make sure we're actually streaming
    print('Stopping primary camera acquisition...')
    if __STREAM_PRIMARY:
        stereo_pyspin.end_acquisition_primary()
        __STREAM_PRIMARY = False
        __THREAD_PRIMARY.join()
        __THREAD_PRIMARY = None

def __stop_acquisition_secondary(_=None):
    """ Stops acquisition of secondary camera """
    global __THREAD_SECONDARY, __STREAM_SECONDARY

    # Make sure we're actually streaming
    print('Stopping secondary camera acquisition...')
    if __STREAM_SECONDARY:
        stereo_pyspin.end_acquisition_secondary()
        __STREAM_SECONDARY = False
        __THREAD_SECONDARY.join()
        __THREAD_SECONDARY = None

def __fps_slider(_=None):
    """ FPS slider callback """

    fps = __GUI_DICT['fps_slider'].val

    try:
        # Set frame rate for cameras
        stereo_pyspin.set_frame_rate(fps)
    except Exception as e: # pylint: disable=broad-except,invalid-name
        # Just print exception, the message box seems to mess up
        # the matplotlib widgets
        warn(str(e))

    # Update text to match slider
    __GUI_DICT['fps_text'].eventson = False
    __GUI_DICT['fps_text'].set_val(fps)
    __GUI_DICT['fps_text'].eventson = True

def __fps_text(_=None):
    """ FPS text callback """

    fps = float(__GUI_DICT['fps_text'].text)

    try:
        # Set frame rate for cameras
        stereo_pyspin.set_frame_rate(fps)
    except Exception as e: # pylint: disable=broad-except,invalid-name
        # Just print exception, the message box seems to mess up
        # the matplotlib widgets
        warn(str(e))

    # Update slider to match text
    __GUI_DICT['fps_slider'].eventson = False
    __GUI_DICT['fps_slider'].set_val(fps)
    __GUI_DICT['fps_slider'].eventson = True

def __gain_slider(_=None):
    """ Gain slider callback """

    gain = __GUI_DICT['gain_slider'].val

    try:
        # Set gain for cameras
        stereo_pyspin.set_gain(gain)
    except Exception as e: # pylint: disable=broad-except,invalid-name
        # Just print exception, the message box seems to mess up
        # the matplotlib widgets
        warn(str(e))

    # Update text to match slider
    __GUI_DICT['gain_text'].eventson = False
    __GUI_DICT['gain_text'].set_val(gain)
    __GUI_DICT['gain_text'].eventson = True

def __gain_text(_=None):
    """ gain text callback """

    gain = float(__GUI_DICT['gain_text'].text)

    try:
        # Set gain for cameras
        stereo_pyspin.set_gain(gain)
    except Exception as e: # pylint: disable=broad-except,invalid-name
        # Just print exception, the message box seems to mess up
        # the matplotlib widgets
        warn(str(e))

    # Update slider to match text
    __GUI_DICT['gain_slider'].eventson = False
    __GUI_DICT['gain_slider'].set_val(gain)
    __GUI_DICT['gain_slider'].eventson = True

def __exposure_slider(_=None):
    """ Exposure slider callback """

    exposure = __GUI_DICT['exposure_slider'].val

    try:
        # Set exposure for cameras
        stereo_pyspin.set_exposure(exposure)
    except Exception as e: # pylint: disable=broad-except,invalid-name
        # Just print exception, the message box seems to mess up
        # the matplotlib widgets
        warn(str(e))

    # Update text to match slider
    __GUI_DICT['exposure_text'].eventson = False
    __GUI_DICT['exposure_text'].set_val(exposure)
    __GUI_DICT['exposure_text'].eventson = True

def __exposure_text(_=None):
    """ exposure text callback """

    exposure = float(__GUI_DICT['exposure_text'].text)

    try:
        # Set exposure for cameras
        stereo_pyspin.set_exposure(exposure)
    except Exception as e: # pylint: disable=broad-except,invalid-name
        # Just print exception, the message box seems to mess up
        # the matplotlib widgets
        warn(str(e))

    # Update slider to match text
    __GUI_DICT['exposure_slider'].eventson = False
    __GUI_DICT['exposure_slider'].set_val(exposure)
    __GUI_DICT['exposure_slider'].eventson = True

# -------------- #
# GUI            #
# -------------- #

def __cam_plot(fig, pos, cam_str, options_height, padding): # pylint: disable=too-many-locals
    """ Creates 'camera' plot; make one of these per camera """

    # Set position params
    num_options = 3
    residual_height = pos[3]-(3+num_options)*padding-num_options*options_height
    image_height = residual_height*0.85
    image_width = pos[2]-2*padding
    hist_height = residual_height-image_height

    # Set axes
    image_pos = [pos[0]+padding, pos[1]+pos[3]-image_height-padding, image_width, image_height]
    image_axes = fig.add_axes(image_pos)

    hist_pos = [image_pos[0], image_pos[1]-hist_height-padding, image_width, hist_height]
    hist_axes = fig.add_axes(hist_pos)

    find_button_pos = [image_pos[0],
                       hist_pos[1]-options_height-padding,
                       image_width*0.25,
                       options_height]
    find_button_axes = fig.add_axes(find_button_pos)

    find_text_pos = [find_button_pos[0]+find_button_pos[2]+padding,
                     find_button_pos[1],
                     image_width-find_button_pos[2]-padding,
                     options_height]
    find_text_axes = fig.add_axes(find_text_pos)

    init_button_pos = [find_button_pos[0],
                       find_button_pos[1]-options_height-padding,
                       image_width*0.25,
                       options_height]
    init_button_axes = fig.add_axes(init_button_pos)

    init_text_pos = [init_button_pos[0]+init_button_pos[2]+padding,
                     init_button_pos[1],
                     image_width-init_button_pos[2]-padding,
                     options_height]
    init_text_axes = fig.add_axes(init_text_pos)

    start_acquisition_pos = [init_button_pos[0],
                             init_button_pos[1]-options_height-padding,
                             (image_width-padding)*0.5,
                             options_height]
    start_acquisition_axes = fig.add_axes(start_acquisition_pos)

    stop_acquisition_pos = [start_acquisition_pos[0]+start_acquisition_pos[2]+padding,
                            start_acquisition_pos[1],
                            (image_width-padding)*0.5,
                            options_height]
    stop_acquisition_axes = fig.add_axes(stop_acquisition_pos)

    # Set widgets
    find_button = Button(find_button_axes, 'Find ' + cam_str)
    find_button.label.set_fontsize(7)
    find_text = TextBox(find_text_axes, '')
    init_button = Button(init_button_axes, 'Init ' + cam_str)
    init_button.label.set_fontsize(7)
    init_text = TextBox(init_text_axes, '')
    start_acquisition_button = Button(start_acquisition_axes, 'Start Acquisition')
    start_acquisition_button.label.set_fontsize(7)
    stop_acquisition_button = Button(stop_acquisition_axes, 'Stop Acquisition')
    stop_acquisition_button.label.set_fontsize(8)

    return {'image_axes': image_axes,
            'hist_axes': hist_axes,
            'find_button': find_button,
            'find_text': find_text,
            'init_button': init_button,
            'init_text': init_text,
            'start_acquisition_button': start_acquisition_button,
            'stop_acquisition_button': stop_acquisition_button}

def __slider_with_text(fig, pos, slider_str, val_min, val_max, val_default, padding): # pylint: disable=too-many-arguments
    """ Creates a slider with text box given a position """

    # Set position params
    slider_padding = 0.1
    slider_text_width = 0.2

    # Slider
    slider_pos = [pos[0]+slider_padding+padding,
                  pos[1],
                  pos[2]-slider_padding-3*padding-slider_text_width,
                  pos[3]]
    slider_axes = fig.add_axes(slider_pos)
    slider = Slider(slider_axes,
                    slider_str,
                    val_min,
                    val_max,
                    valinit=val_default,
                    dragging=False)
    slider.label.set_fontsize(7)
    slider.valtext.set_visible(False)

    # Text
    text_pos = [slider_pos[0]+slider_pos[2]+padding,
                slider_pos[1],
                slider_text_width,
                pos[3]]
    text_axes = fig.add_axes(text_pos)
    text = TextBox(text_axes, '')

    return (slider, text)

def __stereo_gui(): # pylint: disable=too-many-locals
    """ Main function for GUI for setting up stereo cameras with PySpin library """

    # Get figure
    fig = plt.figure()

    # Set position params
    padding = 0.01
    options_height = 0.02
    num_options = 8
    cam_plot_height_offset = num_options*options_height+num_options*padding
    cam_plot_width = 0.5
    cam_plot_height = 1-cam_plot_height_offset

    # Primary camera plot
    cam_primary_pos = [0,
                       cam_plot_height_offset,
                       cam_plot_width,
                       cam_plot_height]
    cam_plot_primary_dict = __cam_plot(fig,
                                       cam_primary_pos,
                                       'Primary',
                                       options_height,
                                       padding)
    # Set initial values
    cam_plot_primary_dict['init_text'].set_val('primary.yaml')
    # Set callbacks
    cam_plot_primary_dict['find_button'].on_clicked(__message_box_func_wrapper(__find_primary))
    cam_plot_primary_dict['init_button'].on_clicked(__message_box_func_wrapper(__init_primary))
    cam_plot_primary_dict['start_acquisition_button'].on_clicked(__message_box_func_wrapper(__start_acquisition_primary))
    cam_plot_primary_dict['stop_acquisition_button'].on_clicked(__message_box_func_wrapper(__stop_acquisition_primary))

    # Secondary camera plot
    cam_secondary_pos = [cam_primary_pos[0]+cam_primary_pos[2],
                         cam_plot_height_offset,
                         cam_plot_width,
                         cam_plot_height]
    cam_plot_secondary_dict = __cam_plot(fig,
                                         cam_secondary_pos,
                                         'Secondary',
                                         options_height,
                                         padding)
    # Set initial values
    cam_plot_secondary_dict['init_text'].set_val('secondary.yaml')
    # Set callbacks
    cam_plot_secondary_dict['find_button'].on_clicked(__message_box_func_wrapper(__find_secondary))
    cam_plot_secondary_dict['init_button'].on_clicked(__message_box_func_wrapper(__init_secondary))
    cam_plot_secondary_dict['start_acquisition_button'].on_clicked(__message_box_func_wrapper(__start_acquisition_secondary))
    cam_plot_secondary_dict['stop_acquisition_button'].on_clicked(__message_box_func_wrapper(__stop_acquisition_secondary))

    # FPS
    fps_pos = [0, cam_primary_pos[1]-options_height-padding, 1, options_height]
    (fps_slider, fps_text) = __slider_with_text(fig,
                                                fps_pos,
                                                'FPS',
                                                __FPS_MIN,
                                                __FPS_MAX,
                                                __FPS_MIN,
                                                padding)
    # Set callbacks
    fps_slider.on_changed(__fps_slider)
    fps_text.on_submit(__fps_text)

    # Gain
    gain_pos = [0, fps_pos[1]-options_height-padding, 1, options_height]
    (gain_slider, gain_text) = __slider_with_text(fig,
                                                  gain_pos,
                                                  'Gain',
                                                  __GAIN_MIN,
                                                  __GAIN_MAX,
                                                  __GAIN_MIN,
                                                  padding)
    # Set callbacks
    gain_slider.on_changed(__gain_slider)
    gain_text.on_submit(__gain_text)

    # Exposure
    exposure_pos = [0, gain_pos[1]-options_height-padding, 1, options_height]
    (exposure_slider, exposure_text) = __slider_with_text(fig,
                                                          exposure_pos,
                                                          'Exposure',
                                                          __EXPOSURE_MIN,
                                                          __EXPOSURE_MAX,
                                                          __EXPOSURE_MIN,
                                                          padding)
    # Set callbacks
    exposure_slider.on_changed(__exposure_slider)
    exposure_text.on_submit(__exposure_text)

    return {'fig': fig,
            'cam_plot_primary_dict': cam_plot_primary_dict,
            'cam_plot_secondary_dict': cam_plot_secondary_dict,
            'fps_slider': fps_slider,
            'fps_text': fps_text,
            'gain_slider': gain_slider,
            'gain_text': gain_text,
            'exposure_slider': exposure_slider,
            'exposure_text': exposure_text}

# -------------- #
# Set up streams #
# -------------- #

def __plot_image(image, image_axes, imshow_dict):
    """ plots image somewhat fast """

    # TODO: need to adjust max intensity based on bit depth

    max_val = 255

    if image is not None:
        if image.shape == imshow_dict['imshow_size']:
            # Can just "set_data" since data is the same size
            imshow_dict['imshow'].set_data(image)
        else:
            # Must reset axes and re-imshow()
            image_axes.cla()
            imshow_dict['imshow'] = image_axes.imshow(image, cmap='gray', vmin=0, vmax=max_val)
            imshow_dict['imshow_size'] = image.shape
            image_axes.set_xticklabels([])
            image_axes.set_yticklabels([])
            image_axes.set_xticks([])
            image_axes.set_yticks([])

    return imshow_dict

def __plot_hist(image, hist_axes, hist_dict):
    """ plots histogram """

    # TODO: need to adjust max intensity based on bit depth

    num_bins = 100
    max_val = 255

    hist, bins = np.histogram(image.ravel(), normed=True, bins=num_bins, range=(0, max_val))
    if hist_dict['bar'] is not None:
        # Just reset height
        for i, bar in enumerate(hist_dict['bar']): # pylint: disable=blacklisted-name
            bar.set_height(hist[i])
    else:
        # Must reset axes and plot hist
        hist_axes.cla()
        hist_dict['bar'] = hist_axes.bar(bins[:-1], hist, color='k', width=(max_val+1)/num_bins)
        hist_axes.set_xticklabels([])
        hist_axes.set_yticklabels([])
        hist_axes.set_xticks([])
        hist_axes.set_yticks([])

    return hist_dict

def __stream_image_primary():
    """ stream update of primary image """
    global __IMSHOW_PRIMARY_DICT, __HIST_PRIMARY_DICT

    print('Primary image stream starting...')

    while __STREAM_PRIMARY and plt.fignum_exists(__GUI_DICT['fig'].number):
        # Get image
        image = stereo_pyspin.get_image_primary()

        # Plot image
        __IMSHOW_PRIMARY_DICT = __plot_image(image,
                                             __GUI_DICT['cam_plot_primary_dict']['image_axes'],
                                             __IMSHOW_PRIMARY_DICT)

        # Plot histogram
        __HIST_PRIMARY_DICT = __plot_hist(image,
                                          __GUI_DICT['cam_plot_primary_dict']['hist_axes'],
                                          __HIST_PRIMARY_DICT)

    print('Primary image stream ended.')

def __stream_image_secondary():
    """ stream update of secondary image """
    global __IMSHOW_SECONDARY_DICT, __HIST_SECONDARY_DICT

    print('Secondary image stream starting...')

    while __STREAM_SECONDARY and plt.fignum_exists(__GUI_DICT['fig'].number):
        # Get image
        image = stereo_pyspin.get_image_secondary()

        # Plot image
        __IMSHOW_SECONDARY_DICT = __plot_image(image,
                                               __GUI_DICT['cam_plot_secondary_dict']['image_axes'],
                                               __IMSHOW_SECONDARY_DICT)

        # Plot histogram
        __HIST_SECONDARY_DICT = __plot_hist(image,
                                            __GUI_DICT['cam_plot_secondary_dict']['hist_axes'],
                                            __HIST_SECONDARY_DICT)

    print('Secondary image stream ended.')

# -------------- #
# Start gui      #
# -------------- #

def main():
    """ Main program """
    global __THREAD_PRIMARY, __THREAD_SECONDARY
    global __STREAM_PRIMARY, __STREAM_SECONDARY
    global __IMSHOW_PRIMARY_DICT, __IMSHOW_SECONDARY_DICT
    global __HIST_PRIMARY_DICT, __HIST_SECONDARY_DICT
    global __GUI_DICT

    # Set GUI
    __GUI_DICT = __stereo_gui()

    # Update plot while figure exists
    while plt.fignum_exists(__GUI_DICT['fig'].number): # pylint: disable=unsubscriptable-object
        try:
            plt.pause(sys.float_info.min)
        except: # pylint: disable=bare-except
            if plt.fignum_exists(__GUI_DICT['fig'].number):
                # Only re-raise error if figure is still open
                raise

    print('Exiting...')

    # Clean up threads
    __stop_acquisition_primary()
    __stop_acquisition_secondary()
    __IMSHOW_PRIMARY_DICT = {'imshow': None, 'imshow_size': None}
    __IMSHOW_SECONDARY_DICT = {'imshow': None, 'imshow_size': None}
    __HIST_PRIMARY_DICT = {'bar': None}
    __HIST_SECONDARY_DICT = {'bar': None}

    # Clean up GUI
    __GUI_DICT = None

    return 0

if __name__ == '__main__':
    sys.exit(main())