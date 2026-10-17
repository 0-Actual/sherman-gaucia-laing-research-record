# Finding and mathematical contract

## S01 — existing approval controls: no defect reproduced in selected checks

**Purpose:** prevent an unapproved or changed invocation from producing a tool side effect. **Domain:** synthetic function tools, the same configured agent, trusted serialized state, normal and streamed Runner paths in SDK 0.24.0. **Invariant:** execution requires the relevant approval decision; a reused call identifier must not silently change its invocation. The final eight tests cover pause, rejection, approved JSON resume and changed-ID rejection before a permitted sibling. All pass on baseline and candidate. Source review follows the [invocation binding](https://github.com/openai/openai-agents-python/blob/9abc9182d06dbd28330af888306031269d57a175/src/agents/run_context.py) and [tool preflight](https://github.com/openai/openai-agents-python/blob/9abc9182d06dbd28330af888306031269d57a175/src/agents/run_internal/tool_planning.py) paths. No correction is claimed for these working cases. This does not test arbitrary agent graphs, external authorization or untrusted snapshot authentication.

## S02 — reproduced structured-result corruption; candidate correction passes

**Purpose:** transfer executor observations into model input and retained run items without inventing observations. **Definition:** the public executor contract permits either plain text or `ShellResult`, whose output is a list of command-output records. **Assumption:** a structured list can be empty; display text and structured observations have different roles.

The required invariant is:

```text
structured result with output = []
    -> model-visible shell output = []
    -> no fabricated shell_output record
```

An explicit quiet command with a known exit code remains a one-entry result. An explicit entry whose exit code is unknown retains that unknown value. Neither is interchangeable with a zero-entry result.

**Counterexample:** the baseline turns `ShellResult(output=[])` into one entry containing stdout `(no output)` and exit code `0`. Its persisted `shell_output` also contains this invented entry. Truncating the display text changes the invented stdout but not the cause. The four failing final baseline tests cover two result shapes in two execution modes.

**Reproduced cause:** in [ShellAction.execute](https://github.com/openai/openai-agents-python/blob/9abc9182d06dbd28330af888306031269d57a175/src/agents/run_internal/tool_actions.py#L627), the truthiness test collapses `None` (no structured result) and `[]` (a valid empty structured result). The false branch promotes the display placeholder into structured stdout. [render_shell_outputs](https://github.com/openai/openai-agents-python/blob/9abc9182d06dbd28330af888306031269d57a175/src/agents/run_internal/tool_execution.py#L975) deliberately supplies that placeholder for display.

Mathematically, the Boolean projection is not injective on the two semantic states: `bool(None) = bool([]) = False`. A later branch cannot recover which state existed. The correction uses the presence predicate `shell_output_payload is not None`, preserving the distinction. This is established optional-value/type reasoning, not a new mathematical discovery.

**Correction:** one predicate changes in an isolated MIT-derived SDK source copy. No output entry, success code, schema, tool permission or extra execution is introduced. **Verification:** the candidate passes all 32 final cases, including the four original counterexamples and unchanged neighboring behavior. Every shell-result case checks the retained item, its input conversion and the next synthetic model request; approval checks verify actual in-memory execution counts. This is stronger than checking only a rendering helper, while remaining bounded to the listed scenarios.

**Interpretation and limits:** this is a data-integrity defect in an accepted executor shape, not demonstrated arbitrary code execution, a deployed incident or institutional misconduct. The original issue, diagnosis and fix direction predate this assessment. No CVSS score is assigned. The project-level lesson is to keep observation, formatting and execution status distinct; similarity to earlier QEL reporting concerns does not establish shared source code or copying.
