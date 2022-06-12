## **The Chromatic Tuner**


Real real-time analysis software written in Python. It uses the PC's microphone to record sound and determine the pitch. 

The software application can be used for tunning a guitar, a violin etc. 


**More detailed explanation:**


This project contains a generic musical tuner. The application uses the Short-Time Fourier Transform (STFT)
algorithm which is applied to an input stream of audio data. Further, the tuner
has a sound trigger (level threshold trigger), applies a high pass filter with a cutoff frequency of 50 Hz (the AC frequency in
Europe) and uses the Harmonic Product Spectrum (HPS) for robustness and efficiency. In the last part, it
computes the closest musical note to the input signal frequency, calculates the 'Target Frequency' i.e
the actual frequency of the musical note and it prints in the console together with the obtained
frequency of the input signal.

