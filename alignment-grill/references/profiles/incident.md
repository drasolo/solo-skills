# Incident response

Something is broken in production now. Speed matters, and two people fixing the same thing is the main danger.

- **Lease:** 30m
- **Decision deadline:** 15 minutes; past it, the manager (incident lead) decides
- **Extra task fields:** Severity (SINGLE_SELECT: SEV1, SEV2, SEV3), Workstream
- **Default grouping:** Workstream
- **Default stages:** implement; implement, review for any change to production
- **Who votes:** the incident lead decides alone; others propose
- **Extra kickoff questions:**
  - What is broken, for whom, since when?
  - Who is incident lead?
  - Which actions are allowed without asking (restart, roll back), and which need the lead?
  - Where do status updates go, and how often?
