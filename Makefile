install:
	pip install --upgrade pip
	pip install -r requirements.txt

update-git-metadata:
	python -m dbt_metadata_utils.git_metadata

update-index:
	python -m dbt_metadata_utils.algolia

run:
	cd dbt-search-app && npm start

develop: install
	pip install 'black>=19.3b0' 'flake8>=3.6.0' 'flake8-annotations==2.1.0' \
		'pre-commit>=2.2.0'
	pre-commit install

lint:
	pre-commit run -a

deploy:
	cd dbt-search-app && npm run build
	cd dbt-search-app && npm run push-gh-pages
