---
name: spec-writing
description: 기획. Interview the user, then write a self-contained spec to docs/spec-<topic>.md with goal, scope, screens and checkable acceptance criteria. Use before design or implementation of a new feature.
---

Run this in the main conversation (the user must answer questions; subagents cannot ask). Use plan mode while interviewing.

1. Restate the request in two lines. Ask only what the code and the request do not answer: target user, goal, what is out of scope, the hard constraints. Two to four questions at a time, with a recommended default for each.
2. Write the spec to `docs/spec-<topic>.md` (or the path the user names). Sections:
   - Goal and Users.
   - In scope and Out of scope.
   - Screens or flows, one line each, and the data each one needs.
   - API needs (what the client must get from the server), if any.
   - Acceptance criteria. Each one must be checkable by a command, a request or a file read. Rewrite any that is not.
   - Open questions.
3. Mark every assumption "Assumption:". Do not invent requirements the user did not give.
4. The file must stand alone: designer, publisher, frontend, backend and qa read it without this conversation. Name the files and interfaces involved.
