flake8:
	@poetry run flake8 --config config/tox.ini

test:
	@poetry run pytest --cov=tradeo

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
	@git fetch origin
	@echo "Checking merge conflicts between develop and origin/master..."
	@set -e; \
	git merge --no-commit --no-ff origin/master >/dev/null 2>&1 || { \
		echo "ERROR: Potential merge conflicts detected with origin/master. Resolve before make tag."; \
		git rev-parse -q --verify MERGE_HEAD >/dev/null && git merge --abort || true; \
		exit 1; \
	}; \
	git rev-parse -q --verify MERGE_HEAD >/dev/null && git merge --abort || true; \
	echo "OK: No merge conflicts detected with origin/master."

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
	@git add .
	@git commit -am "v$$(poetry version -s)"
	@git push
	@git tag v$$(poetry version -s)
	@git push --tags
	@poetry version
	@echo "Tagging complete. Make a pull request to merge develop into master -> https://github.com/sorul/tradeo/compare/develop?expand=1"
