## **The Chromatic Tuner**


*Real real-time analysis software* with the source code written in Python. It uses the Pc's microphone to record sound and determine the pitch. 

The software application can be used for tunning a guitar, for example. 


**More detailed explanation:**


This project is a generic musical tuner. The application uses the Short-Time Fourier Transform (*STFT*)
 algorithm applied on a input stream of audio data. Further, the tuner
has a sound trigger (*level threshold trigger*), applies a high pass filter with a *cutoff frequency of 50 Hz* (the AC frequency in
Europe) and uses the Harmonic Product Spectrum (*HPS*) for robustness and efficiency. In the last part, it
computes the closest musical note to the input signal frequency, calculates the the 'Target Frequency' i.e
the actual frequency of the musical note and and it prints in console all of this, together with the obtained
frequency of the input signal.