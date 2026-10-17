# Preserve the review's own errors

The first catalogue path matcher excluded a closing parenthesis within a path.
It omitted the CAT(0) manuscript and produced a count of 718. The corrected matcher
includes that existing file and reconciles 719 current links with 719 unique paths.
The first parser and affected reports remain in the private `audit/first-parser/`
directory. This was not an OpenAI error. Full-file byte verification and the
independent finite mathematics checks were unaffected.

Local setup also encountered an orchestration resource interruption, a Windows
long-path sparse-checkout failure, an unavailable optional YAML package, and a
one-off default-text-encoding read error. These do not count as upstream findings.
The corrected workflow uses a pinned compressed archive, verified UTF-8 sources,
explicitly scoped metadata extraction and resumable records. Detailed setup notes
are retained privately. No original source, failed attempt or withdrawn paper was
silently replaced by a successful successor.
