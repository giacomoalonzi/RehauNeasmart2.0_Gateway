We have identified a bug or issue that needs to be fixed.

Your job is to:

1. Create a technical bug fix plan that concisely describes the bug and how to fix it.
2. Research the files and functions that need to be changed to implement the fix
3. Avoid any product manager style sections (no success criteria, timeline, migration, etc)
4. Avoid writing any actual code in the plan.
5. Include specific and verbatim details from the user's bug report to ensure the plan is accurate.
6. **Data Naming Conventions**: Always specify data transformation requirements between backend (snake_case) and frontend (camelCase) formats.

This is strictly a technical requirements document that should:

1. Include a brief description to set context at the top
2. Point to all the relevant files and functions that need to be changed or created
3. Explain any algorithms that are used step-by-step
4. If necessary, breaks up the work into logical phases. Ideally this should be done in a way that has an initial "investigation" phase that defines the root cause and scope, followed by N phases that can be done in parallel (e.g. Phase 2A - Core Fix, Phase 2B - Testing, Phase 2C - Documentation). Only include phases if it's a REALLY complex bug.
5. **Data Transformation Requirements**: Specify how backend data (snake_case) will be transformed to frontend format (camelCase) in API responses.

If the user's bug description is unclear, especially after researching the relevant files, you may ask up to 5 clarifying questions before writing the plan. If you do so, incorporate the user's answers into the plan.

Prioritize being concise and precise. Make the plan as tight as possible without losing any of the critical details from the user's bug report.

Write the plan into a `docs/bugfixes/<N>_BUG_DESCRIPTION.md` file with the next available bug number (starting with 0001)

## TODO Checklist — Auto-generation

After writing the plan, automatically generate or update a `## TODO Checklist` section in the SAME plan file. Do NOT open or use a separate command doc.

Steps:

1. Read the plan you just wrote.
2. Extract phases and concrete files/components/hooks/routes/stores mentioned in the plan.
3. Create an actionable TODO checklist grouped by phases, with atomic, verb-led items.
4. Insert or replace the `## TODO Checklist` section inside the same plan file.

Rules:

1. Follow project architecture conventions: Flask blueprints, SQLite database, Modbus communication, circuit breaker pattern, structured logging, Docker deployment, OpenAPI documentation.
2. Data transformations: backend `snake_case` ↔ frontend `camelCase` in API responses. If the plan references API work, include tasks to transform requests and responses accordingly.
3. Type safety: reference or add tasks for proper type hints and avoid `Any`.
4. Tasks MUST be:
   - Atomic (≤ 14 words), verb-led, clear outcome
   - Grouped under their Phase heading
   - File-oriented when possible (reference exact paths from the plan)
   - Free of operational steps (no "run tests", "search codebase", etc.)
5. If a `## TODO Checklist` already exists, replace it entirely with the new list (idempotent update).

Output:

- Update the SAME plan file in-place, appending or replacing the `## TODO Checklist` section.
- Checklist format must use GitHub-style checkboxes `- [ ]` and nested sub-items.
- Keep paths relative to `src/` where applicable.

Checklist Content Guidance (map these to the plan's phases):

- Phase — Investigation & Analysis
  - Trace bug through codebase flow
  - Identify root cause and affected files
  - Check for similar patterns and edge cases
  - Assess data transformation issues (snake_case vs camelCase)

- Phase — Core Fix Implementation
  - Fix the root cause in identified files
  - Update related components and functions
  - Apply data transformations if needed
  - Add proper error handling and logging

- Phase — Testing & Validation
  - Write unit tests for the fix
  - Add integration tests if needed
  - Test edge cases and error scenarios
  - Validate data transformations

- Phase — Documentation & Prevention
  - Update API documentation
  - Add comments explaining the fix
  - Document prevention strategies
  - Update configuration examples if needed

Example (insert into the plan file):

## TODO Checklist

- [ ] Phase 1 — Investigation & Analysis
  - [ ] Trace bug through `api/zones.py`
  - [ ] Identify root cause in `modbus_manager.py`
  - [ ] Check similar patterns in `api/*`
  - [ ] Verify data transformation in API responses
- [ ] Phase 2 — Core Fix Implementation
  - [ ] Fix validation logic in `api/zones.py`
  - [ ] Update Modbus communication in `modbus_manager.py`
  - [ ] Apply snake_case ↔ camelCase transforms
  - [ ] Add proper error handling and logging
- [ ] Phase 3 — Testing & Validation
  - [ ] Write unit tests for `tests/unit/test_zones.py`
  - [ ] Add integration tests for zone operations
  - [ ] Test edge cases and error scenarios
  - [ ] Validate data transformation functions
- [ ] Phase 4 — Documentation & Prevention
  - [ ] Update API documentation
  - [ ] Add inline comments explaining fix
  - [ ] Document prevention strategies
  - [ ] Update configuration examples if needed
