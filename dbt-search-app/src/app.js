import algoliasearch from 'algoliasearch/lite';
import instantsearch from 'instantsearch.js';
import {
  searchBox,
  hits,
  stats,
  configure,
  pagination,
  refinementList,
  clearRefinements,
} from 'instantsearch.js/es/widgets';

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
  searchBox({
    container: '#searchbox',
    placeholder: 'Search for a dataset',
  }),
  stats({
    container: '#stats',
  }),
  hits({
    container: '#hits',
    templates: {
      // https://www.algolia.com/doc/api-reference/widgets/hits/js/#widget-param-item
      // https://www.algolia.com/doc/guides/building-search-ui/widgets/customize-an-existing-widget/js/#example-using-a-function
      // https://www.algolia.com/doc/guides/building-search-ui/ui-and-ux-patterns/highlighting-snippeting/js/#response-information
      item(hit) {
        return `<article>
                <h2 class="hit-name">${hit._highlightResult.name.value}</h2>
                <p class="hit-description">${
                  hit._highlightResult.description.value
                }</p>
                <dl class="hit-metadata">
                    <dt>folder:</dt>
                    <dd>${hit._highlightResult.folder.value}</dd>
                    <dt>sources:</dt>
                    <dd><ul>${(hit._highlightResult.sources || [])
                      .map(({ value }) => `<li>${value}</li>`)
                      .join('')}</ul></dd>
                    <dt>type:</dt>
                    <dd>${hit.resource_type}<dd>
                    <dt>materialization:</dt>
                    <dd>${hit.materialized}</dd>
                    <dt>loaders:</dt>
                    <dd><ul>${hit.loaders
                      .map(loader => `<li>${loader}</li>`)
                      .join('')}</ul></dd>
                    <dt>centrality:</dt>
                    <dd>${hit.degree_centrality}</dd>
                    <dt>owner:</dt>
                    <dd>${hit.owner}</dd>
                    <dt>created_at:</dt>
                    <dd>${new Date(hit.created_at * 1000).toDateString()}</dd>
                    <dt>last_modified_at:</dt>
                    <dd>${new Date(
                      hit.last_modified_at * 1000
                    ).toDateString()}</dd>
                </dl>
                </article>`;
      },
    },
  }),
  pagination({
    container: '#pagination',
  }),
  clearRefinements({
    container: '#clear-refinements',
  }),
  // https://www.algolia.com/doc/api-reference/widgets/refinement-list/js/
  refinementList({
    container: '#sources-list',
    attribute: 'sources',
    searchable: true,
  }),
  refinementList({
    container: '#folder-list',
    attribute: 'folder',
    searchable: true,
  }),
  refinementList({
    container: '#materialized-list',
    attribute: 'materialized',
  }),
  refinementList({
    container: '#resource_type-list',
    attribute: 'resource_type',
  }),
  refinementList({
    container: '#loaders-list',
    attribute: 'loaders',
  }),
  configure({
    hitsPerPage: 5,
  }),
]);

search.start();
