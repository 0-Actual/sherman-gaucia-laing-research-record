# Finding and mathematical purpose

## Purpose and definition

The engineering problem is ownership of asynchronous work. A consumer reads events while a separate producer continues the agent run. Stopping the consumer, requesting producer cancellation, and observing producer settlement are three different events. This is established concurrency reasoning, not a new mathematical theorem or a quantum result.

Let C denote consumer activity, R producer activity, and X completion of the owning context. For this wrapper's cooperative, single-owner scope, the tested postcondition is: **X implies the producer has settled and the synthetic tool's finalization has been observed**. C becoming inactive alone does not establish that postcondition. Cancellation sends a request; settlement is established by awaiting the SDK's drain/cleanup boundary.

Assumptions: one application owner; one stream consumer; supported SDK public APIs; an active event loop; cooperative model/tool implementations. No guarantee is made for an independent process, an external side effect, another consumer, or application code that deliberately refuses to settle.

## Existing report and corroboration

The independently authored [issue 5386](https://github.com/openai/openai-agents-python/issues/5386) reports continued background work after consumer failure during event handling. Its proposed expectation includes automatic cancellation on abandonment. This packet does not silently impose that policy on every SDK user; explicit ownership is the opt-in application contract.

The pinned source is [result.py at 9abc9182](https://github.com/openai/openai-agents-python/blob/9abc9182d06dbd28330af888306031269d57a175/src/agents/result.py). Its Git blob is `36c9cc9c0d901821a65dbc3725a06c6687079f7f`. The public snapshot in this packet matches that blob exactly.

| Scenario | Observed source-method behavior | Interpretation |
| --- | --- | --- |
| Consumer cancelled while waiting on the event queue | Cancellation requested; producer settles | Existing cancellation path works in the bounded probe |
| Consumer cancelled during its own event handler | Consumer unregisters; producer remains pending and uncancelled | Stopping the reader is not equivalent to stopping the run |
| Consumer raises during its event handler | Same producer continuation | Same lifecycle mechanism, a different exit trigger |
| Explicit iterator close before producer release | Close waits for the still-running producer | Closing alone does not request cancellation in this path |
| Explicit cancellation followed by close | Producer cancellation/finalization observed | Existing public controls provide a remedy |
| Normal exhaustion | Completes without a cancellation request | Control case to preserve |

The source-method harness substitutes an in-memory producer and queues and stubs error, provider and sandbox boundaries. It establishes the selected method behavior; it does not independently reproduce the report's model-call counts or measure charges.

## Cause and correction

In the inspected source, the queue-wait exception handler calls `cancel()` (lines 1079–1085). The consumer task's completion callback unregisters a failed consumer (lines 1037–1041), without requesting producer cancellation. The generator's ordinary finalization waits for the run task (lines 1116–1125). These different paths account for the observed cases. The SDK's streaming documentation already tells callers to use explicit cancellation and finish consuming the stream; upstream maintainer intent about every abandonment scenario is not inferred from the code alone.

`owned_stream.py` supplies an explicit application ownership boundary. It tracks normal exhaustion. On early exit, it requests cancellation unless the result is already marked complete, then drains the stream through cleanup. If cancellation already closed the original iterator, it re-enters the public stream-drain path. A separately owned, shielded cleanup task retains responsibility through further cancellation of the waiting caller. The original body error remains primary; secondary failure types are added as notes without copying their messages. If there is no primary error, cleanup failure or cancellation remains visible.

The full SDK integration checks cover normal output, early break, leaving before the first event, body failure, cancellation inside the body, cancellation while awaiting the next event, repeated cancellation during delayed tool cleanup, and a body error followed by cancellation during cleanup. Two smaller protocol checks cover secondary cleanup failures. The wrapper does not modify SDK internals or automatically govern callers that do not use its context.

## Relationship to Priority Zero

The recent GAUCIA correction also distinguished a termination request from observed process exit. That is a useful conceptual connection: preserve ownership until the relevant completion evidence exists. The processes, APIs and implementations differ. This comparison establishes neither common source code nor copying, priority, novelty or institutional misconduct.

## Remaining questions

Real model transports, persisted sessions, sandbox resources, multiple readers, noncooperative tools and other platforms need their own supported scenarios and verification. They are not covered by the synthetic results here. A bounded deadline cannot by itself make uncooperative work stop, so this wrapper does not pretend that timeout equals completed cleanup. The existing public issue remains with its upstream maintainers; no new report or contribution was sent.
