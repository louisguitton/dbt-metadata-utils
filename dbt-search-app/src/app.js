require('dotenv').config()

const searchClient = algoliasearch(
    process.env.ALGOLIA_APP_ID,
    process.env.ALGOLIA_SEARCH_ONLY_API_KEY
);

const search = instantsearch({
    indexName: process.env.ALGOLIA_INDEX_NAME || 'dbt_nodes',
    searchClient,
});

// https://www.algolia.com/doc/guides/building-search-ui/widgets/showcase/js/
search.addWidgets([
    instantsearch.widgets.searchBox({
        container: '#searchbox',
        placeholder: 'Search for a dataset',
    }),
    instantsearch.widgets.stats({
        container: '#stats',
    }),
    instantsearch.widgets.hits({
        container: '#hits',
        templates: {
            item: document.getElementById('hit-template').innerHTML,
            empty: `We didn't find any results for the search <em>"{{query}}"</em>`,
        },
    }),
    instantsearch.widgets.pagination({
        container: '#pagination',
    }),
    instantsearch.widgets.clearRefinements({
        container: '#clear-refinements',
    }),
    // https://www.algolia.com/doc/api-reference/widgets/refinement-list/js/
    instantsearch.widgets.refinementList({
        container: '#sources-list',
        attribute: 'sources',
        searchable: true,
    }),
    instantsearch.widgets.refinementList({
        container: '#folder-list',
        attribute: 'folder',
        searchable: true,
    }),
    instantsearch.widgets.refinementList({
        container: '#materialized-list',
        attribute: 'materialized',
    }),
    instantsearch.widgets.refinementList({
        container: '#resource_type-list',
        attribute: 'resource_type',
    }),
    instantsearch.widgets.configure({
        hitsPerPage: 10,
    })
]);

search.start();
