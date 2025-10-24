# Lint Fix Command

This command automatically fixes linting issues across the Commerce Clarity monorepo using ESLint, Prettier, and TypeScript.

## What it does

1. **ESLint Auto-fix**: Automatically fixes fixable ESLint issues
2. **Prettier Formatting**: Formats code according to project style guidelines
3. **TypeScript Check**: Validates TypeScript types and fixes import issues
4. **Import Organization**: Sorts and organizes imports according to project rules
5. **Unused Import Removal**: Removes unused imports and variables

## Usage

Run this command when you want to:

- Fix linting errors automatically
- Format code consistently
- Clean up imports and unused code
- Ensure code follows project standards

## Commands executed

```bash
# Fix ESLint issues across all packages
yarn lint --fix

# Format code with Prettier
yarn format

# Type check all packages
yarn typecheck

# Fix specific common issues
npx eslint . --fix --ext .ts,.tsx,.js,.jsx
npx prettier . --write
```

## Scope

This command works on:

- **apps/web**: Main web application
- **apps/storybook**: Storybook documentation
- **packages/ui**: UI component library
- **packages/theme**: Design system theme

## What gets fixed

- **Code Style**: Indentation, spacing, quotes, semicolons
- **Import Organization**: Alphabetical sorting, grouping (external → internal → relative)
- **TypeScript Issues**: Type errors, unused variables, missing types
- **React Issues**: Hook dependencies, JSX formatting, component patterns
- **Unused Code**: Unused imports, variables, and functions

## Manual fixes required

Some issues require manual attention:

- Complex TypeScript type errors
- Logic errors or bugs
- Architecture decisions
- Custom ESLint rules that can't be auto-fixed

## Project-specific rules

The command respects these project conventions:

- **Import Order**: External → Internal → Relative imports
- **TypeScript**: Strict mode with no `any` types
- **React**: Functional components with hooks
- **Styling**: Tailwind CSS with CVA patterns
- **Architecture**: Tanstack Router, Zustand, Tanstack Query

## Output

After running, you'll see:

- ✅ Fixed issues count
- ⚠️ Remaining issues that need manual attention
- 📝 Suggestions for complex fixes
- 🎯 Files that were modified

## Best practices

1. **Run before commits**: Always lint-fix before committing code
2. **Review changes**: Check auto-fixes don't change logic
3. **Manual fixes**: Address remaining issues manually
4. **Test after**: Run tests to ensure fixes don't break functionality
