# Example: Feature development (RBAC)

## Invocation

```text
/amir:use_subagent Add role-based access control to the application.
```

## Must not

Create a single task “Implement role-based access control”.

## Expected task shape (illustrative)

| ID | Task | Type |
|----|------|------|
| T001 | Inspect existing authn/authz flow | discovery |
| T002 | Inventory user/role data models | discovery |
| T003 | Identify protected routes/operations | discovery |
| T004 | Define role and permission model | design |
| T005 | Define authorization interfaces | design |
| T006 | Add/modify role persistence | implementation |
| T007 | Implement permission resolution | implementation |
| T008 | Add authorization middleware | implementation |
| T009 | Apply authz to route group A | implementation |
| T010 | Apply authz to route group B | implementation |
| T011 | Unit tests for permission resolution | test |
| T012 | Middleware tests | test |
| T013 | Endpoint authorization tests | test |
| T014 | Privilege-escalation review | review |
| T015 | Update authorization docs | documentation |
| T016 | Integration and regression validation | validation |

T009/T010 parallel only with non-overlapping file ownership. T014 uses a different agent than T006–T010.
