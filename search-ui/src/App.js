import React from "react";
import {
  SearchProvider,
  SearchBox,
  Results,
  ResultsPerPage,
  Paging,
  WithSearch
} from "@elastic/react-search-ui";
import "@elastic/react-search-ui-views/lib/styles/styles.css";
import "./App.css";
import config from "./searchConfig";

function App() {
  return (
    <SearchProvider config={config}>
      <WithSearch mapContextToProps={({ wasSearched, isLoading, resultSearchTerm, totalResults }) => ({ 
        wasSearched, 
        isLoading,
        resultSearchTerm,
        totalResults 
      })}>
        {({ wasSearched, isLoading, resultSearchTerm, totalResults }) => (
          <div className="app-container">
            {/* Header Section */}
            <div className="search-header">
              <div className="header-content">
                <h1 className="app-title">
                  <span className="title-icon">🔍</span>
                  CV Transcription Search
                </h1>
                <p className="app-subtitle">Search through your transcriptions instantly</p>
              </div>
            </div>

            {/* Search Box Section */}
            <div className="search-section">
              <div className="search-container">
                <SearchBox
                  searchAsYouType={true}
                  inputView={({ getAutocomplete, getInputProps, getButtonProps }) => (
                    <div className="custom-search-box">
                      <div className="search-input-wrapper">
                        <span className="search-icon">🔎</span>
                        <input
                          {...getInputProps({
                            placeholder: "What are you looking for?",
                            className: "search-input"
                          })}
                        />
                        {isLoading && <div className="loading-spinner"></div>}
                      </div>
                      <button {...getButtonProps()} className="search-button">
                        Search
                      </button>
                    </div>
                  )}
                />
              </div>
            </div>

            {/* Results Section */}
            <div className="results-section">
              <div className="results-container">
                {wasSearched && (
                  <div className="results-header">
                    <div className="results-info">
                      <h2 className="results-title">
                        {totalResults > 0 ? (
                          <>
                            Found <span className="highlight">{totalResults}</span> results
                            {resultSearchTerm && (
                              <> for "<span className="search-term">{resultSearchTerm}</span>"</>
                            )}
                          </>
                        ) : (
                          <>No results found</>
                        )}
                      </h2>
                    </div>
                    <div className="results-controls">
                      <ResultsPerPage options={[10, 20, 50]} />
                    </div>
                  </div>
                )}

                {isLoading ? (
                  <div className="loading-container">
                    <div className="loading-animation">
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                    </div>
                    <p>Searching...</p>
                  </div>
                ) : (
                  <Results
                    titleField="filename"
                    textField="text"
                    shouldTrackClickThrough={true}
                    resultView={({ result }) => (
                      <div className="result-card">
                        <div className="result-header">
                          <h3 className="result-title">
                            {result.filename?.raw || result.filename?.snippet || "Untitled"}
                          </h3>  
                        </div>
                      <div className="result-demographics">
                        {result.age?.raw && (
                          <span className="demographic-badge age">
                            👤 Age: {result.age.raw}
                          </span>
                        )}
                        {result.gender?.raw && (
                          <span className="demographic-badge gender">
                            ⚧ Gender: {result.gender.raw}
                          </span>
                        )}
                        {result.accent?.raw && (
                          <span className="demographic-badge accent">
                            🗣️ Accent: {result.accent.raw}
                          </span>
                        )}
                        </div>
                        <div className="result-body">
                          {result.text?.snippet ? (
                            <p 
                              className="result-text"
                              dangerouslySetInnerHTML={{ 
                                __html: result.text.snippet 
                              }}
                            />
                          ) : result.text?.raw ? (
                            <p className="result-text">
                              {result.text.raw.substring(0, 200)}...
                            </p>
                          ) : (
                            <p className="result-text no-text">
                              No text available
                            </p>
                          )}
                        </div>

                        <div className="result-footer">
                          {result._meta?.id && (
                            <span className="result-meta">ID: {result._meta.id}</span>
                          )}
                          {result._meta?.score && (
                            <span className="result-meta">
                              Score: {result._meta.score.toFixed(2)}
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  />
                )}

                {wasSearched && totalResults > 0 && (
                  <div className="pagination-container">
                    <Paging />
                  </div>
                )}
              </div>
            </div>

            {/* Empty State */}
            {!wasSearched && (
              <div className="empty-state">
                <div className="empty-state-icon">📄</div>
                <h3>Start Your Search</h3>
                <p>Enter keywords to search through your CV transcriptions</p>
              </div>
            )}
          </div>
        )}
      </WithSearch>
    </SearchProvider>
  );
}

export default App;