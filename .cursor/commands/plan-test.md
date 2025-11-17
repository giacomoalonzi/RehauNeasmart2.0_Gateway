# Plan Test Command

The user will provide a feature plan file (e.g., `0002_zone_management_plan.md`). Your job is to:

1. **Analyze the feature plan** to understand the core functionality
2. **Create a focused test plan** that covers only the essential aspects
3. **Generate simple test scenarios** for critical user flows only
4. **Structure the test plan** to be actionable for the `@test-maker.md` command
5. **Focus on what really matters** - avoid over-testing

## Test Types

**IMPORTANT**: This command generates plans for **Unit Tests** and **Integration Tests** only, **NOT E2E tests**.

- **Unit Tests**: Test individual modules, functions, and utilities in isolation
- **Integration Tests**: Test API endpoints, database operations, and Modbus communication
- **NOT E2E**: No full system testing or complete user journey testing

## Test Plan Structure

The generated test plan should include:

### 1. **Feature Overview**

- Brief description of what the feature does
- **Main user flow** (the primary path users will take)
- **Critical success criteria** (what must work for the feature to be useful)

### 2. **Essential Tests Only**

Focus on these **3 core areas**:

- **Happy Path**: The main user flow works (unit + integration tests, NOT E2E)
- **Critical Error**: The most important error scenario (e.g., database failure, Modbus timeout)
- **Key Components**: Only the most important modules that users interact with

**Test Scope Clarification**:

- **Unit Tests**: Test individual functions, data encoding/decoding, database operations
- **Integration Tests**: Test API endpoints, Modbus communication, database persistence
- **NOT E2E**: No full system testing, no complete user journeys, no real hardware

### 3. **Test Coverage by Phase**

For each phase, focus on **only the essential items**:

- **Core Modules**: Only test modules that have complex logic or are critical to the user flow
- **API endpoints**: Only test the main API calls, not every endpoint
- **Database operations**: Only test critical data persistence scenarios

### 4. **Critical Test Scenarios**

- **Main Flow**: Complete the primary user journey
- **One Key Error**: Test the most likely failure scenario
- **Data Validation**: Test only the most important validation rules

### 5. **Simple Test Checklist**

- **Unit Tests**: Does the function work? Does it handle edge cases?
- **Integration Tests**: Does the API endpoint work? Does database persistence work?
- **Modbus Tests**: Does communication work? Does error handling work?

## Test Plan Generation Rules

1. **Focus on the main user flow** - ignore edge cases unless they're critical
2. **Test only the most important modules** - skip simple utility functions
3. **Include only essential API endpoints** - not every endpoint mentioned
4. **Test one main error scenario** - not every possible error
5. **Keep it simple** - avoid complex test scenarios

## Output Format

Generate the test plan as `docs/tests/000N_feature_name_test_plan.md` where:

- `N` is the next available test plan number (starting with 0001)
- `feature_name` matches the feature being tested
- The file is **concise and focused** on essentials only

## Integration with test-maker.md

The generated test plan should be structured so that the `@test-maker.md` command can:

- **Generate only essential tests** - no over-engineering
- **Create minimal mocks** - only what's needed for the main flow
- **Focus on critical functionality** - skip nice-to-have tests

## Example Test Plan Sections

```markdown
# Test Plan 0001: Zone Setpoint Management Testing

## Feature Overview

Users can set and read zone setpoints via API. Main flow: POST setpoint → Modbus write → database persistence → GET verification.

## Essential Tests Only

### Main Flow Test (Unit + Integration)

- [ ] DPT 9001 encoding/decoding works correctly
- [ ] Modbus register write/read operations work
- [ ] Database persistence works
- [ ] API endpoint returns correct response

### Critical Error Test

- [ ] Database failure triggers fallback mechanism
- [ ] Modbus timeout is handled gracefully
- [ ] Invalid setpoint values are rejected

### Key Components

- [ ] DPT 9001 encoding preserves temperature precision
- [ ] Database manager handles connection failures
- [ ] Modbus manager writes to correct registers
- [ ] API validates input parameters

## Simple Test Checklist

- [ ] Main setpoint flow works
- [ ] Error handling works
- [ ] Data encoding/decoding works
- [ ] Database persistence works
```

The test plan should be **simple and focused** - only test what's essential for the feature to work properly.

## Important Reminders

- **Unit Tests**: Test individual functions, data encoding, database operations
- **Integration Tests**: Test API endpoints, Modbus communication, database persistence
- **NOT E2E**: No full system testing, no complete user journeys, no real hardware
- **Focus on**: Function behavior, data transformations, API responses, error handling
- **Avoid**: Full system flows, hardware testing, complex user scenarios
