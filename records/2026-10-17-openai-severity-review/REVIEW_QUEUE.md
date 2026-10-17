# Severity-first review queue

Snapshot: October 17, 2026; openai/openai-agents-python main `9abc9182d06dbd28330af888306031269d57a175`. The open issue collection contained nine issues and three pull requests. The order below is this project's triage judgment based on impact and available evidence, not an upstream severity rating, exhaustive security review or guarantee that no higher-impact defect exists elsewhere.

| Order | Area | Evidence and current disposition |
| --- | --- | --- |
| 1 | Unexpected continued actions after the stream consumer exits | Existing [issue 5386](https://github.com/openai/openai-agents-python/issues/5386); the preceding owner study supplied and tested an optional ownership wrapper. Preserve that edition and its limits; unchanged tests were not rerun here. |
| 1 | Approval and invocation binding | Eight bounded checks in this edition pass. No new bypass is established; no authorization fix is invented. |
| 2 | Silent shell-result corruption | Existing [issue 5348](https://github.com/openai/openai-agents-python/issues/5348), independently reproduced here. One-line isolated correction passes this edition's 32 cases. No production incident established. |
| 3 | Invalid history replay sequence | Existing [issue 5342](https://github.com/openai/openai-agents-python/issues/5342): multiple messages between a call and its result can produce invalid Chat Completions input. Next correctness candidate; not reproduced or corrected in this edition. |
| 3 | Redis Cluster session writes fail | Existing [issue 5322](https://github.com/openai/openai-agents-python/issues/5322): pipeline incompatibility and key-slot constraints. Requires representative cluster verification; no local cluster test or fix here. A failed write is not evidence that existing stored records were destroyed. |
| 4 | Repeated fingerprint work | Existing [issue 5382](https://github.com/openai/openai-agents-python/issues/5382). Deferred after the owner's severity direction. Reporter and another contributor already supplied fork proposals. No performance gain is claimed here. |
| 5 | Dependency compatibility and typing | Open [PR 5384](https://github.com/openai/openai-agents-python/pull/5384) and [issue 5387](https://github.com/openai/openai-agents-python/issues/5387); do not duplicate pending work without a separate verified need. |
| Separate | Feature requests and provider lifecycle | Issues 5336, 5353, 5383 and PRs 5369/5370 concern model defaults, Decisions API, sandbox providers or removal work. These are not automatically confirmed defects or part of this correction. |

Further review should follow reachable failure consequences and fresh evidence. An undisclosed security finding would require a separate private disclosure decision; the present public packet contains no newly identified security exploit. Publication remains in the owner's repository, with third-party rights and attribution intact.
