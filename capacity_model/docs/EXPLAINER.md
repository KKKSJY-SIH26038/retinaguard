# Capacity model — plain-English explainer

RetinaGuard isn't only about reading eye photos correctly — it also has to
fit into a real district's clinic, where one small team of graders has to
review everyone's photos. This module answers that logistics question:
if a district screens a certain number of people a year, how many graders
does it actually need so that patients aren't waiting weeks for a result?

We built a year-long computer simulation: photos arrive at random times
through the working day (some days busier than others, just like real
walk-in clinics), and whichever grader finishes their current photo first
picks up the next one waiting in line — the same idea as a single queue
feeding several bank tellers. We tracked, day by day, how many photos are
backed up and how long the average photo waits. To make sure the
simulation itself wasn't wrong, we checked its answer against a
well-known queueing-theory formula (Erlang-C) at a grader count where both
should agree — they matched within 2%, which is the kind of sanity check
that lets us trust the rest of the results.

The headline result: under tonight's working assumptions (100,000 people
screened a year, two photos each, roughly 4 minutes for a grader to review
one), a district needs about 6 graders before the backlog of unreviewed
photos stops growing forever — 5 graders is not enough, no matter how
patient everyone is. We also worked out a second, simpler number for the
pitch: if roughly 15% of photos are too poor-quality to grade at all
(assumed, not measured yet), catching those bad photos right at the
camera — instead of a grader discovering it later — saves about 2,000
grader-hours and avoids about 30,000 patient recall trips per 100,000
people screened per year.

What this does NOT do yet: it doesn't model grader lunch breaks or
holidays as real calendar gaps, it doesn't yet plug into the actual
quality-gate module to see the real (not assumed) rejection rate, and it
isn't the polished Simulink model the full project plan eventually wants
— tonight's version is a fast, honest stand-in built because MATLAB
wasn't available on this laptop. Every number quoted above uses
untuned, stated assumptions, not measured data, and is labelled that way
everywhere it appears.
