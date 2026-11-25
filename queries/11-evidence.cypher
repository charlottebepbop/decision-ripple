// Every signal up to $as_of on $assumptions, so a support in the window
// can be shown next to an earlier break on the same assumption.
MATCH (s:Signal)-[hit:BREAKS|WEAKENS|SUPPORTS|CONFIRMS]->(a:Assumption)
WHERE a.name IN $assumptions AND s.date <= $as_of
RETURN a.name AS assumption, s.date AS date, s.title AS signal, s.source AS source,
       type(hit) AS effect
ORDER BY assumption, date, effect;
