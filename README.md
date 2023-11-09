# synchronization

This is some simple data processing for a Northwestern ESAM project on the synchronization of a system of fireflies and crickets in Amphawa, Thailand.  The term "synchronization" refers to all three of the following:
- fireflies with other fireflies
- crickets with other crickets
- fireflies with crickets

The short-term goals of the project are the following:
1. Determine whether this syncrhonization is present, both within and across species.
2. Characterize the synchronization mathematically.  Does it follow the Kuramoto model for coupled oscillators?

This small repo has some processing that enables this analysis.  As of right now, it only concerns the crickets (audio) portion of the project. 
 There are two main parts:
1. Filtering.  `filter.py` applies a high and a low pass filter to an input audio track in order to isolate the crickets' chirps from other sounds.  The chirps are around 8kHz, so it filters for frequencies from 7.5-8.5kHz.
2. Alignment.  The recordings have two sets of audio recordings per video - left and right - each in stereo format.  These audio tracks are not perfectly aligned, sometimes starting seconds apart.  `audio_align.py` finds the time offset between two such audio tracks in order to precisely align the two.  It tests 1-minute intervals at 30-minute increments in each track, finding the time offset of each interval and storing the results in a text file.  The actual alignment work is done via Ben Miller's `audalign` library (github.com/benfmiller/audalign).
