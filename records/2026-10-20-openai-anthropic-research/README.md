# OpenAI and Anthropic: completed contributions and bounded research

Research date: October 20, 2026. Prepared by **Sherman G. Laing**, with disclosed Codex assistance. This additive edition publishes the completed technical work identified in the October 20 reconciliation. Publication time is the actual GitHub commit time; ZIP member dates are fixed to the research date for deterministic packaging and are not timestamps of creation or publication.

The archives contain implementations, patches, test programs, result evidence, reproduction instructions, attribution and integrity manifests. They are not merely reviews. Unresolved candidates are disclosed with their remaining questions. Publication here does not mean acceptance by OpenAI or Anthropic.

| Work | Read the scope | Download complete code and evidence |
|---|---|---|
| OpenAI Agents SDK: shell correction, optional stream ownership, expanded checks, experimental history replay, Redis verification and history operation counts | [OpenAI infrastructure](OpenAI-Infrastructure.md) | [OpenAI-Infrastructure.zip](OpenAI-Infrastructure.zip) |
| Anthropic TypeScript integration: 99 existing + 24 added cases; Python: 32 behavior characterizations | [Anthropic streaming](Anthropic-Streaming-Research.md) | [Anthropic-Streaming-Research.zip](Anthropic-Streaming-Research.zip) |
| OpenAI mathematics: family 271 finite audits and selected source review, with broader coverage reconciliation | [Mathematics continuation](OpenAI-Mathematics-Continuation.md) | [OpenAI-Mathematics-Continuation.zip](OpenAI-Mathematics-Continuation.zip) |

Download and extract each ZIP, then start with its enclosed README and REPRODUCE instructions. Preview documents retain archive-relative links. Each archive's MANIFEST.json identifies every payload file except that manifest itself. The outer [MANIFEST.json](MANIFEST.json) identifies these downloads and previews. Saved result logs are historical executions; packaging and upload did not rerun the SDK tests or formal mathematics checks.

## Technical status

- **OpenAI #5348:** correction and 32-case suite already [posted upstream](https://github.com/openai/openai-agents-python/issues/5348#issuecomment-6297534362). Baseline: 28 pass/four fail; corrected: 32 pass. Existing reporters and earlier proposals retain credit.
- **OpenAI #5386:** optional ownership helper and ten-case suite already [posted upstream](https://github.com/openai/openai-agents-python/issues/5386#issuecomment-6297538696). The archive adds the later failure-path checks and evidence.
- **OpenAI #5342:** candidate patch and final 13-case test are disclosed for review. No supported originating history or live provider rejection has been established; refusal concatenation remains an open contract decision. The complete final SDK verification stack and strict final-review protocol remain incomplete. This is not a resolved production fix.
- **Anthropic TypeScript:** existing work by qiyuhuating, ax3cubed and sylvesterkaczmarek retains credit. Combining the locally ported completion guard and retained iterator error passes 123 selected tests; guard alone passes 109/123. The pinned base and environment limitations are included. This is not the full SDK or a live-service result.
- **Anthropic Python:** 32 mock characterizations matched the recorded behavior. No Python fix, production incident or novelty claim is made. Completion semantics need an actual affected workflow and an explicit compatibility decision before changing the API.
- **Mathematics:** no confirmed defect in the selected family 271 source passage; finite checks are not proof certification. Verified Lean builds and whole-family certifications remain **zero**. The broader register covers selected proofs in 23 families/26 manuscripts, plus three statement-only manuscripts, not the entire catalogue.

## Attribution, licenses and privacy

Original upstream authors retain their credit and applicable licenses. The contributed OpenAI and Anthropic SDK code carries its scoped MIT contribution notices and upstream MIT notices inside the corresponding archives. The mathematics review retains its stated research-license boundaries; the upstream mathematics is not claimed as this project's invention. Nothing here retroactively relicenses unrelated historical editions.

Private credentials, raw personal conversations, medical/financial information and the governance/accountability metrics previously designated private are outside this technical publication. Local absolute paths in evidence are replaced in explicitly marked derivatives; original evidence is preserved privately with its source hashes. The result is a screened technical release, not a mirror of a laptop or private archive.

No new mathematical theorem, formal proof acceptance, upstream merge, deployment or full release certification is asserted. Maintainers retain their review and submission processes. The owner-repository publication and upstream comments must be distinguished in the publication receipt.
