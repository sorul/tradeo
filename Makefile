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
	base_commit=$$(git merge-base HEAD origin/master); \
	merge_output=$$(mktemp); \
	git merge-tree "$$base_commit" HEAD origin/master > "$$merge_output"; \
	conflict_files=$$(awk '/^changed in both$$/{getline; if ($$1 == "base") print $$NF}' "$$merge_output"); \
	if [ -z "$$conflict_files" ]; then \
		rm -f "$$merge_output"; \
		echo "OK: No merge conflicts detected with origin/master."; \
		exit 0; \
	fi; \
	conflict_count=$$(printf "%s\n" "$$conflict_files" | wc -l | tr -d ' '); \
	if [ "$$conflict_count" -eq 1 ] && [ "$$conflict_files" = "pyproject.toml" ] && \
		awk ' \
			BEGIN { in_conflict = 0; seen_start = 0; seen_sep = 0; seen_end = 0; ours_count = 0; theirs_count = 0; valid = 1 } \
			/^[+]?<<<<<<< / { \
				if (in_conflict != 0) valid = 0; \
				in_conflict = 1; \
				seen_start++; \
				next; \
			} \
			/^[+]?=======$$/ { \
				if (in_conflict != 1) valid = 0; \
				in_conflict = 2; \
				seen_sep++; \
				next; \
			} \
			/^[+]?>>>>>>> / { \
				if (in_conflict != 2) valid = 0; \
				in_conflict = 0; \
				seen_end++; \
				next; \
			} \
			in_conflict == 1 { \
				ours_count++; \
				line = $$0; \
				sub(/^[+]/, "", line); \
				sub(/^[[:space:]]+/, "", line); \
				if (index(line, "version = \"") != 1) valid = 0; \
				next; \
			} \
			in_conflict == 2 { \
				theirs_count++; \
				line = $$0; \
				sub(/^[+]/, "", line); \
				sub(/^[[:space:]]+/, "", line); \
				if (index(line, "version = \"") != 1) valid = 0; \
				next; \
			} \
			END { \
				if (valid && seen_start == 1 && seen_sep == 1 && seen_end == 1 && ours_count == 1 && theirs_count == 1) exit 0; \
				exit 1; \
			} \
		' "$$merge_output"; then \
		rm -f "$$merge_output"; \
		echo "OK: Only the expected version conflict in pyproject.toml was detected."; \
		exit 0; \
	fi; \
	echo "ERROR: Potential merge conflicts detected with origin/master. Resolve before make tag."; \
	echo "$$conflict_files"; \
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
		echo "ERROR: Tag v$$(poetry version -s) already exists."; \
		exit 1; \
	fi
	@git tag v$$(poetry version -s)
	@git push
	@git push --tags
	@poetry version
	@echo "Tagging complete. Make a pull request to merge develop into master ->https://github.com/sorul/tradeo/compare/develop?expand=1"

