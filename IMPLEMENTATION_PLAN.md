# Implementation plan

1. Define entities, fields, keys, cardinalities and lifecycle rules.
2. Create deterministic parent/master data.
3. Generate child records and feedback text with rule-derived labels.
4. Add labelled anomaly cases without corrupting unrelated records.
5. Persist source records, bridges and append-only events.
6. Validate PK/FK integrity, enums, dates, duplicate rules, privacy and leakage.
7. Build sentiment/theme baselines and a human-reviewable evaluation set.
8. Calculate trends, priorities, action items and evaluation metrics.
9. Export CSV/JSON/SQL, add API and dashboard.
10. Regenerate twice with the same seed and compare checksums.

## Suggested milestones
- M1: schema + master data
- M2: baseline generation and valid joins
- M3: exception injection and ground truth
- M4: analysis + measurable evaluation
- M5: dashboard + API + docs + reproducibility
