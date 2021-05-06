# dbt-metadata-utils

> Parse dbt artifacts, enrich them, and search them with Algolia.

Check the online demo at <https://dbt-metadata-utils.guitton.co/>

![](docs/dbt-search-app.png)
![](docs/architecture.png)

## Prerequisites

All you will need is:

- your already existing dbt project in a git repository locally
- clone dbt-metadata-utils on the same machine than your dbt project
- create one Algolia account (and API key)
- create one Algolia app inside that account
- create `.env` file following `.env.example` and fill in your config values from the Algolia dashboard

For the dbt project, we will use one of the [example projects](https://docs.getdbt.com/faqs/example-projects/) listed on the dbt docs: the [jaffle_shop](https://github.com/fishtown-analytics/jaffle_shop) codebase.

## Local Usage

For testing things out with this project, one option is to work in your local environment.

Install the dependencies (in a virtual environment) with the following command:

```sh
make install
```

Then index records into your Algolia search index:

```sh
make update-git-metadata
make update-index
```

Finally, start the search webapp:

```sh
make run
```

## Docker-compose Usage

Whether you want a way to deploy dbt-metadata-utils in production or if simply you're running into issues, you can start the project using `docker-compose`:

```sh
docker-compose up
open http://localhost:8080
```

## Development

```sh
make develop
```
