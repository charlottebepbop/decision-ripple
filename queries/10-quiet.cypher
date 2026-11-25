// Assumptions with no signal on or after $since. Signals dated after $as_of
// do not count as a touch. No signal at all counts as never touched.
// $since and $as_of are YYYY-MM-DD. There is no review date on an assumption;
// the latest signal date is the review.
MATCH (a:Assumption)
OPTIONAL MATCH (s:Signal)-[:BREAKS|WEAKENS|SUPPORTS|CONFIRMS]->(a)
WHERE s.date <= $as_of
WITH a, max(s.date) AS last_signal
WHERE last_signal IS NULL OR last_signal < $since
OPTIONAL MATCH (latest:Signal)-[hit:BREAKS|WEAKENS|SUPPORTS|CONFIRMS]->(a)
WHERE latest.date = last_signal
RETURN a.name AS assumption, a.statement AS statement, last_signal,
       [t IN collect(DISTINCT type(hit)) WHERE t IS NOT NULL] AS effects,
       [t IN collect(DISTINCT latest.title) WHERE t IS NOT NULL] AS titles
ORDER BY last_signal, statement;
