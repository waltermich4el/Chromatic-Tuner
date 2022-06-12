""" This project is a generic musical tuner. The application uses the Short-Time Fourier Transform (STFT)
 algorithm applied on a input stream of audio data. Further, the tuner
has a sound trigger (level threshold trigger), applies a high pass filter with a cutoff frequency of 50 Hz (the AC frequency in
Europe) and uses the Harmonic Product Spectrum (HPS) for robustness and efficiency. In the last part, it
computes the closest musical note to the input signal frequency, calculates the the 'Target Frequency' i.e
the actual frequency of the musical note and and it prints in console all of this, together with the obtained
frequency of the input signal."""

#Author: Walter Buchholtzer


#Version: 6.2
#Date: 2 March 2022, 1:24 AM

#------------------------------Library imports----------------------------------
# The following descriptions of the libraries are cited from their official website pages:

import time # This module provides various time-related functions.
#Source at: https://docs.python.org/3/library/time.html
import copy # "Assignment statements in Python do not copy objects,
# they create bindings between a target and an object. For collections
# that are mutable or contain mutable items, a copy is sometimes needed
# so one can change one copy without changing the other. This module provides
# generic shallow and deep copy operations (explained below)."
#Source at: https://docs.python.org/3/library/copy.html
import matplotlib.pyplot as plt # is a state-based interface to matplotlib.
# It provides an implicit, MATLAB-like, way of plotting.
# It also opens figures on your screen, and acts as the figure GUI manager.
#Source at: https://matplotlib.org/3.5.1/api/_as_gen/matplotlib.pyplot.html
import numpy as np # NumPy is the fundamental package for scientific computing in Python.
# It is a Python library that provides a multidimensional array object,
# various derived objects (such as masked arrays and matrices),
# and an assortment of routines for fast operations on arrays,
# including mathematical, logical, shape manipulation, sorting,
# selecting, I/O, discrete Fourier transforms, basic linear algebra,
# basic statistical operations, random simulation and much more.
#Source at: https://numpy.org/doc/stable/


#SciPy is a collection of mathematical algorithms and convenience
# functions built on the NumPy extension of Python.
# It adds significant power to the interactive Python session
# by providing the user with high-level commands and classes for manipulating
# and visualizing data.
#Source at: https://scipy.org/
import scipy.fftpack # Fourier analysis is a method for expressing a
# function as a sum of periodic components, and for recovering the signal
# from those components. When both the function and its Fourier transform are
# replaced with discretized counterparts, it is called the discrete Fourier transform (DFT).
# The DFT has become a mainstay of numerical computing in part because of a very fast
# algorithm for computing it, called the Fast Fourier Transform (FFT), which was known to Gauss (1805)
# and was brought to light in its current form by Cooley and Tukey [CT65].
import scipy.signal # The signal processing toolbox currently contains some filtering functions,
# a limited set of filter design tools, and a few B-spline interpolation algorithms for 1- and 2-D data.

import sounddevice as sd # This Python module provides bindings for the PortAudio library
# and a few convenience functions to play and record NumPy arrays containing audio signals.
#Source at: https://python-sounddevice.readthedocs.io/en/0.4.4/




#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Beginning of application>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#Defining needed variables
fs = 44100  # sampling rate
M =  32768 # window size of STFT
H = int(M / 2)  # hop size with the minimum size required, smaller ratios -> larger window overlap -> more reliable results
harm = 7  # number of harmonics that we consider for the HPS
A_4 = 440  # concert pitch in Hz
notes = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"] # the list of all musical notes to be printed in order to get a
# a better understanding of the pitch that you tune your instrument to




#The main function that is called with the audio input stream
def callback(indata, frames, time, status): # the standard input variables

    windowBuffer = list(np.zeros(M))  # initialize buffer for FFT where we will store the input data

    # in order to obtain the input data the status needs to be printed,
    if status: # to get info about the over and underflows in rec()
        print(status) # it holds information about the last invocation

    if any(indata): # if there exists any input data then execute the following code blocks...
        ## Sound trigger
        # The volume_norm, and VolumeLevel are variables computed in order to implement the sound trigger
        # for the tuner algorithm using a certain minimum amplitutde of the input signal as a threshold

        volume_norm = np.linalg.norm(indata) * 10 # numpy.linalg.norm --> linalg.norm(x, ord=None, axis=None, keepdims=False)
        # matrix or vector norm.
        # this function is able to return one of eight different matrix norms,
        # or one of an infinite number of vector norms (described below),
        # depending on the value of the ord parameter.
        # Source at: https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html

        VolumeLevel = int(volume_norm) # convert to integer value

        if VolumeLevel > 10: # if the VolumeLevel is larger then threshold, execute the next block of code, else jump to line 162

            ## In order to obtain reliable results from the analysis of the input signal, a method has been
            # implemented where we always have a half-window size overlap between sampling windows. In rough lines,
            # to the current window (aa), new samples are added (b) increasing the effective window lenght by the
            # hop size(H), i.e len(a) = len(b) and the new window has is (aab), the next line then deletes the first half
            # an keeps only the last two halfes, i.e (ab)..and so on

            windowBuffer = np.concatenate((windowBuffer, indata[:, 0])) # adding to the end of the window the new samples
            windowBuffer = windowBuffer[H:] # discarding the first half of the old samples, and reverting back to the
            # original window size

            X = windowBuffer * np.hanning(M) # we multiply the signal with a window function to avoid artefacts that could appear
            # due to the abrupt cutting of the windowBuffer

            X = scipy.fftpack.fft(windowBuffer)  # performing the FFT on the windows signal
            # the first bin in the FFT is DC (0 Hz)

            ## Adding a high pass filter in order to suppress AC 50 Hz hum and other low frequency disruptive interference
            cutoff_frequency_bin = int(60 * M / fs)  # obtaining the frequency bin for 50 Hz cutoff frequency
            for i in range(cutoff_frequency_bin): # looping through the amplitude spectrum, and...
                X[i] = 0 # replacing everything with 0

            ## Implementing the HPS

            hps = copy.copy(X) # Return a shallow copy of magnitutde spectrum X that can be downsampled

            for h in range(1,harm+1): # looping through the number of harmonics in order to obtained the wanted downsample degree
                dec = scipy.signal.decimate(X, h) #scipy.signal.decimate - Downsample the signal after applying an anti-aliasing filter.
                hps[:len(dec)] *= dec # multiplying the spectra

            ## Computing the frequency with the maximum magnitutde from the spectrum
            i_peak = np.argmax(hps[:len(dec)]) # obtaining the index of the frequency bin
            # where the maximum amplitude is located, and
            # using only the positive side of the spectrum while applying modulus

            freq_ = i_peak * fs / M  # we convert from frequency bin to Hz by using the standard equation,
            # and to express this in general terms, the nth bin is used in 'n * fs / M';

            ## Calculate the closest note
            semitone = int(np.round(12 * np.log2(freq_ / A_4)))  # the number of semitones from A4 using the general formula
            # we round it and the convert to an integer because the number of semitones is expressed in them;

            note_name = notes[semitone % len(notes)]  # we do a wrapped around indexing using the  % operator to produce a modulus
            # together with the int(semitone) we index through the notes list
            note_octave = ((semitone + 9) // 12 + 4) # we determine the octave and do floor division to keep the notes tight
            # in that particular octave

            note_freq = A_4 * 2 ** (semitone / 12) # we obtain the Target Frequency or the actual frequency of that particular

            # note in the equally tempered system of the western music

            ## We print the ouput in a fashinable way
            # Fancy version
            # print('------------' + note_name  + str(note_octave) + '------------\n' + "Target Freq.: " +
            #        format(note_freq, ".1f") + " \n" + " Input Freq.: " + format(freq_, ".1f") + '\n -----------------------')
            # we use format(freq_, ".2f") in order to print only the first two decimals of the frequency
            # Lightweight version
            print(note_name + str(note_octave) + '->> ' + format(note_freq, ".1f") + ' || ' +  format(freq_,".1f") )


        elif VolumeLevel < 10: # if the signal is too low then...
            # print("Input level too low") # we print this
            pass
    else:# if there is no input signal due to various tehnical, routing or sofware issues we...
        print('No input') # print this


## Starting the audio stream
try:# when an error occurs, or exception as we call it, Python will normally stop and generate an error message;
    # these exceptions can be handled using the try statement:

    with sd.InputStream(channels=1, callback=callback, blocksize=H, samplerate=fs): # this opens an input-only stream on channel 1,
        # that has a length of H and sampling frequency of 44100 Hz
        while True: # while the abose statement is valid
            time.sleep(0.5) # a delay of 0.5 ms is added for the user to read the output
except Exception as e: # when an error occurs .....
    print(str(e)) # this gets printed


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>End of application<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<