# Rubric: review report (starter, tune before use)

The grader scores the review report at `/mnt/session/outputs/review.md`, not the manuscript. Each criterion passes or fails on its own.

1. The report exists at `/mnt/session/outputs/review.md` and is written in the manuscript's language.
2. The Release gate section contains the gate's verdict and exit code, and every blocking item from the gate output, unchanged.
3. If the gate exit code was 1, the overall verdict is `fail`.
4. The Verdict section states that the report is an AI pre-review and not a human or reader check.
5. Every finding gives a location (line number or section heading) and a concrete fix.
6. Every claim of type fact, data, quote or cause in `work.json` appears in the claim and evidence table with one of: supports, weaker, does not support, not opened.
7. No claim is marked `supports` when its source file was not provided in the review folder.
8. The report contains no wording that approves, validates or certifies the manuscript for release.
9. The report does not propose changing `verification`, `author_acceptance` or `external_facts`, and the manuscript and `work.json` are unchanged.
10. The Not checked section lists at least the checks that needed unavailable sources or a real reader.
