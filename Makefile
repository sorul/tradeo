flake8:
	@flake8 --config config/tox.ini

test:
	@poetry run pytest --cov=tradeo

requirements:
	@poetry export -f requirements.txt --output requirements.txt --without-hashes

dev_requirements:
	@poetry export --with dev -f requirements.txt --output requirements_dev.txt --without-hashes

push_develop:
	@make requirements
	@make dev_requirements
	git commit --allow-empty -m "updating requirements and pushing to develop"

tag:
	@make flake8
	@make test
	@make requirements
	@make dev_requirements
	@git add .
	@git commit -am "v$$(poetry version -s)"
	@git push
	@git checkout master
	@git merge --no-edit --log develop
	@git tag v$$(poetry version -s)
	@git push
	@git push --tags
	@git checkout develop
	@poetry version

