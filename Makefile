update-git-metadata:
	python -m dbt_metadata_utils.git_metadata

update-index:
	python -m dbt_metadata_utils.algolia

run:
	cd dbt-search-app && npm start
