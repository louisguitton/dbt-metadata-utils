update-index:
	python -m dbt_metadata_utils.algolia

run:
	cd dbt-search-app && npm start
