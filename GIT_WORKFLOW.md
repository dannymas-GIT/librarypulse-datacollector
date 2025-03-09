# LibraryPulse Git Workflow

This document outlines the Git workflow for the LibraryPulse project.

## Branch Structure

- **main**: The stable production branch. All code in this branch should be fully tested and ready for deployment.
- **development**: The primary development branch where features and bug fixes are integrated.
- **feature/xxx**: Feature branches for developing new functionality.
- **bugfix/xxx**: Branches for fixing specific bugs.
- **release/x.x.x**: Release branches for preparing specific versions.

## Workflow

### Starting New Work

1. Always create new branches from the `development` branch:
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, commit often with meaningful commit messages:
   ```bash
   git add .
   git commit -m "Descriptive message about the changes"
   ```

### Completing Work

1. Ensure your branch is up to date with the development branch:
   ```bash
   git checkout development
   git pull origin development
   git checkout feature/your-feature-name
   git merge development
   ```

2. Resolve any conflicts if they arise.

3. Push your branch to GitHub (once repository is set up on GitHub):
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request from your feature branch to the development branch.

### Releasing

1. When ready for a release, create a release branch from development:
   ```bash
   git checkout development
   git pull origin development
   git checkout -b release/x.x.x
   ```

2. Make any final adjustments, version bumps, etc.

3. Merge to main:
   ```bash
   git checkout main
   git merge release/x.x.x
   git push origin main
   ```

4. Tag the release:
   ```bash
   git tag -a vx.x.x -m "Version x.x.x"
   git push origin vx.x.x
   ```

5. Merge back to development:
   ```bash
   git checkout development
   git merge release/x.x.x
   git push origin development
   ```

## Commit Message Guidelines

Write clear, concise commit messages that explain the "what" and "why" of your changes, not just the "how".

Format:
```
Short summary (50 chars or less)

More detailed explanation, if necessary. Keep line length to about 72 
characters. Explain the problem that this commit is solving and why
you chose the approach you did.

- Bullet points are fine
- Use a hyphen or asterisk followed by a space

If applicable, reference issues and pull requests:
- Fixes #123
- Relates to #456
```

## Git Commands Quick Reference

- Check status: `git status`
- View branches: `git branch`
- Create branch: `git checkout -b branch-name`
- Switch branch: `git checkout branch-name`
- Pull changes: `git pull origin branch-name`
- Add files: `git add file-name` or `git add .`
- Commit changes: `git commit -m "message"`
- Push changes: `git push origin branch-name`
- View commit history: `git log`
- View differences: `git diff` 