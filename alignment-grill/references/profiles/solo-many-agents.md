# Solo with many agents

One person, several agents in parallel. The person is the manager and the only voter.

- **Lease:** 1h
- **Decision deadline:** none; the person decides when asked
- **Extra task fields:** none
- **Default grouping:** Area
- **Default stages:** implement, review; plan, implement, review for anything over a day
- **Who votes:** the person alone, so every decision is decided by one `/vote`
- **Extra kickoff questions:**
  - Which areas of the code can agents work on at the same time without touching the same files?
  - Which changes always need you to look before merge?
  - How many agents at once can you actually review?
