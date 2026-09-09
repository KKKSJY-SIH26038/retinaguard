# Module 1 tonight - the plain-English version

Module 1 is the front door of the screening pipeline. Before any image is
graded for diabetic retinopathy, this module asks one question: is this photo
good enough to trust?

It works entirely with classical image processing - no neural network. First it
finds the round camera view inside the photo, crops to it, and blacks out
everything else. Then it measures four things: how sharp the picture is, how
evenly it is lit (by splitting the retina into sixteen wedge-and-ring cells and
comparing their brightness), how much of the expected circle is actually filled
in, and whether the overall exposure is sensible.

The image then gets one of three verdicts. Good: send straight to grading.
Needs work: run a quick clean-up - boost local contrast, flatten the lighting,
gently denoise - and then grade it. Reject: do not grade it at all; instead
show the camera operator a specific instruction, such as "too blurred, steady
the camera and retake" or "too dark, increase the illumination".

We tested it on twenty-six images: twenty real retina photos and six we
deliberately damaged in six different ways. Every damaged image was caught, and
no clean image was wrongly rejected.

What it does not do yet: the cut-offs were set by eye tonight, not tuned on a
labelled quality dataset; it does not use a learned model; and it has only been
run on one small public image set, not on real portable-camera photos from a
clinic.
