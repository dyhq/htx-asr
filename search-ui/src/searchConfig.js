import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

// Configuration for Elasticsearch connection
const connector = new ElasticsearchAPIConnector({
  // Elasticsearch server URL
  host: "http://localhost:9200",
  
  // Elasticsearch index
  index: "cv-transcriptions"
});

// Search UI configuration
const config = {
  apiConnector: connector,
  
  // Fields to search in
  searchQuery: {
    search_fields: {
      text: {},
      generated_text: {}
    },
    // Fields to return in results
    result_fields: {
      filename: {
        snippet: {}
      },
      text: {
        snippet: {
          size: 300,
          fallback: true
        }
      },
      age: {
        raw: {}
      },
      gender: {
        raw: {}
      },
      accent: {
        raw: {}
      }
    }
  }
};

export default config;