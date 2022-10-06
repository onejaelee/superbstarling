# superbstarling

superbstarling is a project with Dr. Shana Caro to attempt to retrain a image classifier, Inception v3, to be able to capture the presence of adult nesting superb
starling for the purpose of labeling bird nest footage for behavioral research. Normally, one would have to manually watch hundreds of hours of footage to be
able to properly able to label the video for the research project, but a image classifier could potentially expedite this manual task greatly.

autosorter.py in particular creates second by second frames of every single bird nest footage and corresponds them with a time stamp using
optical character recognition, due to metadata from the video being lost, and also labels any frame that has been previously described
by a human as having an adult bird present or not in the frame of the video. It then properly sorts the labeled images into absent or present
to be used by the retrainer to retrain Inception v3 for Image Classification purposes.

Example of Adult Bird being Present
![image](https://user-images.githubusercontent.com/51391902/194206703-2e0d1dd8-f796-4841-adff-bba774a9ed97.png)
Example of Adult Bird being Absent
![image](https://user-images.githubusercontent.com/51391902/194206833-b11cf852-b839-4a0e-92b9-f3f8c0217af6.png)
