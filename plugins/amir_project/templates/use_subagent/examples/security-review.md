# Example: Security-sensitive change

## Invocation

```text
/amir:use_subagent Refactor this authentication module and add tests.
```

## Required behaviors

- Separate discovery, design (frozen token/session contracts), implementation, tests, and **independent security review**.
- Reviewer is not the implementer; receives diff + test evidence.
- Medium/high `risk_level` on auth tasks.
- No parallel writers on the same auth files.
- Secrets never copied into worker prompts.
