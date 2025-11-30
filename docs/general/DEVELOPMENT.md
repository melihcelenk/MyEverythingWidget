# Development Guidelines

## UI Testing System

### Humanized Test DSL

All UI tests for drag-and-drop operations MUST be written using the Humanized Test DSL format. This format provides a
human-readable way to define grid states and test actions.

#### Test File Format

Test files are located in `tests/humanized/drag/` directory. Each test file follows this format:

```
Rows: 5
Columns: 5

Initial:
.  .  .  .  .
N1 N1 .  .  A1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action:
Drag(N1,R1C3)

Expected:
.  .  .  .  .
A1 .  .  N1 N1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
```

#### Notation

- **Apps**: `A1`, `A2`, `A3`, etc.
- **Notes**: `N1`, `N2`, `N3`, etc.
- **Images**: `I1`, `I2`, `I3`, etc.
- **Empty cells**: `.` (dot)
- **Multi-span items**: Show all cells they occupy (e.g., `N1 N1` for a 2x1 note)

#### Actions

**Drag Action:**

```
Drag(ItemID,TargetPosition)
```

Example: `Drag(N1,R2C3)` - Drags item N1 to row 2, column 3 (0-indexed: second row, third column)

**Create Action:**

```
Create(NOTE, "note content", N1)
Create(APP, "app name", A1)
```

Creates a new item and assigns it the specified ID.

#### Running Tests

**Run all tests:**

```bash
.\tests\test_humanized_ui.bat
```

**Run specific test:**

```bash
.\tests\test_humanized_ui.bat swap_note_and_app
# or
.\tests\test_humanized_ui.bat swap_note_and_app.dsl
```

### Test State Management

#### JSON State Files

All test state files are located in `tests/state/` and `tests/tmp/` directories:

- `tests/state/initial_test_state.json` - Template state file (read-only, git committed)
- `tests/tmp/app_state.json` - Working test state file (created during tests, gitignored)

#### State Isolation

- UI tests use `tests/tmp/app_state.json` to avoid affecting user's actual state
- Each test starts by copying `tests/state/initial_test_state.json` to `tests/tmp/app_state.json`
- Tests automatically clean up state after completion
- `tests/tmp/` directory is gitignored

#### State File Structure

```json
{
  "categories": [],
  "apps": [],
  "notes": []
}
```

### Testing Workflow

**IMPORTANT:** When testing UI functionality, especially drag-and-drop operations:

1. **DO NOT** ask the user to manually test
2. **DO** write a humanized test file in `tests/humanized/drag/`
3. **DO** run the test using `scripts\test_humanized_ui.bat`
4. **DO** verify the test passes or correctly identifies the bug
5. **DO** fix the bug and ensure the test passes

#### Example Workflow

1. User reports: "2x1 note becomes 1x1 when dragged"
2. Create test file: `tests/humanized/drag/2x1_note_right_edge.dsl`
3. Write test with `Create(NOTE, "content", N1)` and `Drag(N1, R2C3)`
4. Run: `.\tests\test_humanized_ui.bat 2x1_note_right_edge`
5. Test fails, confirming the bug
6. Fix the bug in code
7. Re-run test to verify fix

### Test Runner Features

The `humanized_ui_runner.py`:

- Automatically creates test category and items
- Opens the application window
- Performs drag-drop operations using PyAutoGUI
- Compares actual vs expected results
- Shows detailed differences if test fails
- Cleans up state after test

### Best Practices

1. **Always write tests first** (TDD approach)
2. **Use descriptive test names** that explain what is being tested
3. **Include comments** in test files for complex scenarios
4. **Test edge cases**: right edge, bottom edge, multi-span items
5. **Verify span information**: Tests check both position AND span (row_span, col_span)

### Test File Naming

- **Format**: `snake_case.dsl`
- **Extension**: `.dsl` (required - Domain Specific Language)
- **Examples**:
    - `swap_note_and_app.dsl`
    - `2x1_note_right_edge.dsl`
    - `switch_between_tabs.dsl`
    - `open_add_dialog.dsl`
- **Rules**:
    - Always use `snake_case` (lowercase with underscores)
    - Always include `.dsl` extension
    - Use descriptive names that explain what is being tested
    - No "or" or other conjunctions - each file tests one scenario
- **Organization**:
    - `tests/humanized/drag/` - Drag-and-drop tests
    - `tests/humanized/tabs/` - Tab switching tests
    - `tests/humanized/dialogs/` - Dialog tests
    - `tests/humanized/` - Other general tests

