generate-docs:
	pdoc3 --html --force api
test:
	pytest .
fmt:
	black .
	isort -rc .
	autoflake --in-place -r api