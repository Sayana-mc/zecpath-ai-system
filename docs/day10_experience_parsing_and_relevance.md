# Day 10 — Experience parsing and relevance

The root parses date ranges and role lines using Day 10 rules, selects the
recognized work-experience section where present, and reports total
experience. Dated overlapping ranges now contribute only their calendar-time
union; a regression test covers overlapping roles. Employment gaps and
overlaps can be detected by the stage helpers, but gaps do not enter the
root score.

Important limitations remain: extraction may miss roles when titles and
dates occur on one line, responsibilities and technologies are not reliably
structured, role relevance is not used as a distinct root score component,
undated duration estimates cannot be checked for overlap, and irregular
dates/layouts remain uncertain. The Day 13 experience component compares
available total years with the opening's minimum; it is not a validated
relevance assessment. See `day10_experience_relevance/tests/`.
