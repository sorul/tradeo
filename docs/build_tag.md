Source: [Tutorial]( https://dev.to/luscasleo/creating-and-publishing-a-python-lib-with-poetry-and-git-11bp#:~:text=Creating%20and%20publishing%20a%20python%20lib%20with%20poetry,...%206%20Bonus%20-%20Using%20private%20repositories%20)

### 1. Merge all the changes into develop branch

### 2. Being in develop branch, update the [CHANGELOG](../CHANGELOG.md) file. 
The changes are cataloged in:
- fix: A bug fix. Correlates with PATCH
- feat: A new feature. Correlates with MINOR
- docs: Documentation only changes
- style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- refactor: A code change that neither fixes a bug nor adds a feature. Correlates with PATCH
- perf: A code change that improves performance
- test: Adding missing or correcting existing tests
- build: Changes that affect the build system or external dependencies (example - scopes: pip, docker, npm)
- ci: Changes to our CI configuration files and scripts (example scopes: GitLabCI)

<br/>

### 3. Upload the version according to the change made:
```python
poetry version <option>
```
The \<option> should be ([Poetry Doc](https://python-poetry.org/docs/cli/#version)):
- patch (X.X.1)
- minor (X.1.X)
- major (1.X.X)
- prepatch
- preminor
- premajor
- prerelease

<br/>

### 4. Make the build package and push it to Github:
```
make version
```