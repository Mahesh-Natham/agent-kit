# Workflows

## Supervisor meeting: before
1. Pull the last `SUP` row and its open action items, plus the roadmap rows that were in progress since that date and any `Experiment_Ledger` rows added since then.
2. Build a 5–8 slide deck:
   1. Title (date, both supervisors)
   2. Actions from last meeting (done or not, with a one-line reason)
   3. Progress, with a figure for each result
   4. Problems and what I tried
   5. Decisions I need from you, phrased as A/B questions
   6. Plan to the next meeting
3. Save it to `Advisor_Meetings/YYYY-MM-DD_SUP-00N_<topic>`. Draft (don't send) a short email with the agenda.

Prof. El Kamel (Centrale Lille) cares about the math formulation and AI rigor (CMDP, baselines). Prof. Sreedhar (Mahindra) cares about the SIL and hardware link to the AEV. Make each deck show both sides.

## Supervisor meeting: after
Ask Mahesh for rough notes, or a transcript if there is one. Then:
1. Add a `Supervisor_Decisions` row.
2. Add a calendar reminder for each action item.
3. Draft a recap email to the supervisors in Gmail.
4. Save the minutes in `Advisor_Meetings/`.

## CSI annual review (Jun–Jul each year)
Start 6 weeks before. The report covers the year's progress against the roadmap, publications, training credits earned out of 30, the plan for next year and risks. Slides run 15–20 minutes. Rehearse with him by asking likely committee questions, such as why DRL over ALNS, how the action masking guarantees feasibility, and how he validates.

## Conference or journal paper
Use the target venue's template (IEEE ITSC/IFAC for paper 1, TR-C/E for journal 1, T-ITS or Applied Energy for journal 2). Write in this order: problem and contribution bullets, related-work table from `Literature_Matrix`, method, experiments, intro and abstract last. Keep a `submission_checklist.md` in the paper folder covering page limit, anonymisation, DOIs verified and figures readable in grayscale. Add the submission and rebuttal deadlines to the calendar.

## Reading a paper
Produce a reading note covering:
- Citation, problem, model (routing type, battery model, queue model, mobile chargers), method and results
- Limitations and gap
- **Relevance to our PhD**
- Numbers worth reusing, and the benchmark instances used

Then add the `Literature_Matrix` row. Verify DOIs (Crossref) before citing them. Never invent a reference. If he can't get the PDF, say so and work from the abstract, and mark the note "abstract only".

## Experiments
For each run, add an `Experiment_Ledger` row (read the header row first): ID, date, notebook or commit, config, instance set, metrics, checkpoint path in `04_Saved_Checkpoints`, and what we learned. Compare against the ALNS/OR-Tools baseline on Schneider's instances before claiming an improvement.

## Weekly review (also used by the cloud routine)
This covers the last 7 days and the next 14:
- Milestones moved
- Papers logged versus the MS-01 target
- Experiments run
- Overdue action items
- Upcoming deadlines
- Admin windows open (visa, registration, CVEC, insurance, CSI)
- The three priorities for the week

Keep it under 300 words, plain text, with a short subject line: `[PhD] Weekly review – <date>`.
