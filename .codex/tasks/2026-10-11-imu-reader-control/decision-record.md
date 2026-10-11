# Bounded decision

Compare fixed400us-request logger wake vs topic poll at constant source/topic/
transport treatment; avoid new firmware/queue/protocol changes or unsupported
integration-rate increase. Strict profile extension preserves legacy defaults,
source/type/freshness guards. Timing cause remains a hypothesis; one trial cannot
prove sustained robustness. Original gates and source/clock/model unknowns remain.

Actual result rejects adopting -r2500 as a no-skip fix: two retained holes and
two observed logger-generation skip increments, with clean UART frames/TX counters.
No statistical worsening claim from one nonrandomized comparison. Separate poll
cursor is not necessary for this observed failure; scheduling/execution cause
still UNKNOWN.317 extended accel windows and197.10Hz remain source-level issues.
Next requires scoped source execution/generation/endpoints observability, not
blind repeats or unapproved firmware/queue/rate changes. No Stage C admission.
