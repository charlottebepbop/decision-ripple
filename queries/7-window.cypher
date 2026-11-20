// Signals dated from $since through $as_of, inclusive (YYYY-MM-DD).
// Every effect is returned, so a break and a support on the same assumption
// can sit together in the weekly briefing. The six product queries are unchanged.
MATCH (s:Signal)-[hit:BREAKS|WEAKENS|SUPPORTS|CONFIRMS]->(a:Assumption)
WHERE s.date >= $since AND s.date <= $as_of
RETURN s.date AS date, s.title AS signal, s.source AS source, s.name AS signal_name,
       type(hit) AS effect, a.name AS assumption, a.statement AS statement
ORDER BY date, effect, assumption;
