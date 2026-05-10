flake8:
	@poetry run flake8 --config config/tox.ini

test:
	@if rg --files -g 'test*.py' -g '*test*.py' -g 'tests/**' | grep -q .; then \
		poetry run pytest --cov=sorul_tradingbot; \
	else \
		echo "No tests found. Skipping pytest."; \
	fi

requirements:
	poetry lock
	poetry export -f requirements.txt --output requirements.txt --without-hashes

dev_requirements:
	poetry lock
	poetry export --with dev -f requirements.txt --output requirements_dev.txt --without-hashes

push_develop:
	@poetry update
	@make requirements
	@make dev_requirements
	git commit --allow-empty -m "updating requirements and pushing to develop"

check_merge_master:
	@current_branch=$$(git branch --show-current); \
	if [ "$$current_branch" != "develop" ]; then \
		echo "ERROR: check_merge_master must run from develop (current: $$current_branch)"; \
		exit 1; \
	fi
	@set -e; \
	git fetch origin; \
	merge_output=$$(mktemp); \
	echo "Checking merge conflicts between develop and origin/master..."; \
	if git merge-tree --write-tree HEAD origin/master > "$$merge_output" 2>&1; then \
		rm -f "$$merge_output"; \
		echo "OK: No merge conflicts detected with origin/master."; \
		exit 0; \
	fi; \
	echo "ERROR: Merge conflicts detected with origin/master. Resolve before make tag."; \
	sed -n 's/^CONFLICT .* in //p' "$$merge_output"; \
	rm -f "$$merge_output"; \
	exit 1

check_untracked:
	@untracked=$$(git ls-files --others --exclude-standard); \
	if [ -n "$$untracked" ]; then \
		echo "ERROR: Untracked files detected:"; \
		echo "$$untracked"; \
		exit 1; \
	fi

check_origin_develop:
	@current_branch=$$(git branch --show-current); \
	if [ "$$current_branch" != "develop" ]; then \
		echo "ERROR: check_origin_develop must run from develop (current: $$current_branch)"; \
		exit 1; \
	fi
	@git fetch origin develop
	@behind_count=$$(git rev-list --count HEAD..origin/develop); \
	if [ "$$behind_count" -ne 0 ]; then \
		echo "ERROR: origin/develop is ahead of local develop by $$behind_count commit(s)."; \
		echo "Run 'git pull --rebase origin develop' before make tag."; \
		exit 1; \
	fi

tag:
	@make check_origin_develop
	@make check_untracked
	@make check_merge_master
	@poetry update
	@make flake8
	@make test
	@make requirements
	@make dev_requirements
	@if git diff --quiet && git diff --cached --quiet; then \
		echo "No tracked changes to commit. Tagging current HEAD."; \
	else \
		git add -u; \
		git commit -m "v$$(poetry version -s)"; \
	fi
	@if git rev-parse -q --verify refs/tags/v$$(poetry version -s) >/dev/null; then \
		echo "ERROR: Tag v$$(poetry version -s) already exists locally."; \
		exit 1; \
	fi
	@if git ls-remote --exit-code --tags origin v$$(poetry version -s) >/dev/null 2>&1; then \
		echo "ERROR: Tag v$$(poetry version -s) already exists in origin."; \
		exit 1; \
	fi
	@git tag v$$(poetry version -s)
	@git push
	@git push --tags
	@poetry version
	@echo "Tagging complete. Make a pull request to merge develop into master -> https://github.com/sorul/tradeo/compare/develop?expand=1"
