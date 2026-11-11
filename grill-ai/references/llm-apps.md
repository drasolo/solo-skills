# LLM application catalog

Anything that calls an LLM, including prompts, RAG, structured extraction and LLM judges.

## Decision branches

- **Model tier.** Which is the cheapest model that passes the eval, and what would the top tier add in measured terms?
- **Context source.** Does the task need retrieval, or does the data fit in the prompt? Does keyword search reach the bar before embeddings?
- **Wrong-answer policy.** May the system say it doesn't know? What must it refuse?
- **Grader.** What does correct mean for this task, and can code check it before a judge model is used?
- **Change control.** What must pass before a prompt, model or index change ships?

## Mechanics

- **Floating model alias.** An undated or latest alias changes behavior without a commit. Pin a version and log it with each response.
- **Unhandled stop reasons.** Truncated, refused or empty responses are parsed as complete answers. Branch on the stop reason.
- **Silent context overflow.** Code truncates history or documents and drops the instructions or the key passage. Count tokens and log what was cut.
- **Unvalidated structured output.** Parse against a schema and check semantic constraints, such as whether an ID exists.
- **Prompt assembly bugs.** Empty variables, wrong ordering, duplicated instructions or stale few-shot examples. Log and read the final rendered prompt.
- **Index and query mismatch.** Different embedding models, normalization or chunk versions between indexing and querying.
- **Stale index.** Deleted or edited documents remain retrievable. Test a delete from end to end.
- **Chunking errors.** Chunks split tables, code or the sentence that answers the question. Read samples of retrieved chunks.
- **Unsafe retries.** Retries repeat side effects, or retry on errors that cannot succeed. Use idempotency keys and back off only on transient errors.

## Exposure

- **Prompt injection.** Retrieved pages, emails, files or tool results carry instructions the model follows. Plant test instructions in each untrusted source and observe the result.
- **Output as code.** Model output reaches HTML, markdown image URLs, SQL, shell or a template without escaping. Test for script execution and data exfiltration through URLs.
- **Secrets in prompts.** Assume any prompt content can be extracted. Keep credentials outside the model's context.
- **Retrieval across permissions.** A user can retrieve documents they cannot open. Enforce access at query time.
- **Tail cost and latency.** Averages hide long documents and retry storms. Measure the 95th and 99th percentiles and cap both.
- **Provider data terms.** Confirm retention, training use and region for the data sent.
