# Example: Repository refactor

## Invocation

```text
/amir:use_subagent Review this repository and implement the requested feature.
```

## Expected behaviors

- Inspect before asking; ask only material scope forks.
- Discovery tasks produce shared summaries reused by workers (no duplicate full-repo discovery per agent).
- Feature split into atomic implementation + tests + integration.
- Avoid unrelated formatting/dependency churn.
- Final requirement→evidence matrix; unverified REQs listed.
