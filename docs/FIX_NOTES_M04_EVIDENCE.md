# M04 evidence-status fix

- The API now passes M03 `skill_evidence` into M04 skill-gap matching.
- M04 keeps initial skill-gap counts based on resume claims, so `NO_GAP` means no claimed-skill gap was detected; it does not mean practical proficiency is verified.
- Each semantic match now includes `evidence_found` and `evidence` when evidence data is supplied.
- Exact or semantic matches without supporting evidence use status `Claimed; evidence not found` instead of `Well claimed`.
- Regression coverage verifies Docker can remain an exact claim match while being explicitly marked as lacking supporting evidence, and REST APIs evidence is recognized.
