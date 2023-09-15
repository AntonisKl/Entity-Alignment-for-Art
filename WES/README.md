## WES Method Files

This method is aimed at entity alignment from a pre-existing Knowledge Art (ArtGraph) based on Wikiart. Below, data and code functions are described.

## Data

### Input

[Artist names and artwork titles](https://drive.google.com/file/d/1DDfIz-15SNe8T7vysWKNBX0P-xe-2q8F/view?usp=drive_link)  
Formatted in CSV with the following columns:

| artist   | artwork  |
|----------|----------|

**Explanation:**

- `artist`: Denotes the artist's name.
- `artwork`: Represents the title of an artwork created by the respective artist.

### 1. Entity Search Script: `entitysearch.py`

**Description:**  
The `entitysearch.py` script is designed to search and retrieve entities, primarily from the Wikidata repository or another SPARQL-based data source.

**Main Components and Functions:**

- **Imports and Dependencies:**  
  - `csv`: Handles CSV files.
  - `time`: Manages time-related tasks.
  - `SPARQLWrapper`: Executes SPARQL queries.
  - `BeautifulSoup`: Parses HTML and XML documents.
  - `unicodedata`: Manages Unicode character properties.

- **Function - `replace_symbols(text)`:**  
  Normalizes the input text by decoding special symbols and characters.

- **Function - `execute_query(sparql, query)`:**  
  Executes the provided SPARQL query and returns the results.

**SPARQL Query:**  

The query searches Wikidata for entities that match a given text, which corresponds to the title of the artwork ({input_text}). From these results, it identifies items that have a specified creator and further filters them based on whether the creator's name contains another given text, corresponding to the artist ({input_text2}). The final output is the topmost item from this refined list.


```
    SELECT * WHERE {{
        SERVICE wikibase:mwapi {{
            bd:serviceParam wikibase:endpoint "www.wikidata.org";
                            wikibase:api "EntitySearch";
                            mwapi:search "{input_text}";
                            mwapi:language "en".
            ?item wikibase:apiOutputItem mwapi:item.
            ?num wikibase:apiOrdinal true.
        }}
        ?item wdt:P170 ?creator.
        ?creator rdfs:label ?creatorLabel.
        FILTER (CONTAINS(LCASE(?creatorLabel), "{input_text2}"))
    }}
    ORDER BY ASC(?num)
    LIMIT 1
```

### 2. Entity Search Script for Artists: `artists-entitysearch.py`

**Description:**  
This script is designed to map Wikipedia page titles and artist names to their corresponding Wikidata entity IDs. It reads artist names and Wikipedia URLs from two separate CSV files, processes each entry, and writes the results to a new CSV file. The processing involves extracting Wikipedia page titles, fetching their corresponding Wikidata items, and handling exceptions for non-existent pages or invalid titles. If an exception arises, the script checks for a match in the list of artist names and uses Spacy with OpenTapioca to identify the Wikidata entity ID.

**Main Components and Functions:**

- **Imports and Dependencies:**  
  - `csv`: Handles reading and writing CSV files.
  - `wikipediaapi`: Fetches Wikipedia page data.
  - `pywikibot`: Interacts with Wikipedia and Wikidata.
  - `spacy`: Conducts natural language processing tasks.
  - `pandas`: Facilitates data manipulation and analysis.

- **Initializations:**  
  Initializes the English version of Wikipedia, the English Wikipedia site for Pywikibot, and a blank English Spacy model with the OpenTapioca pipeline added.

- **Function - `Reading Artist Names`:**  
  Reads the artist names from the `titles_names.csv` file into a pandas DataFrame.

- **Function - `Reading Wikipedia URLs`:**  
  Opens the `wikipedia_urls.csv` file and reads all the Wikipedia URLs into a list.

- **Function - `Processing URLs and Writing Results`:**  
  Opens a new CSV file (`artists2.csv`) for writing. For each Wikipedia URL, it:
  - Extracts the page title.
  - Fetches the corresponding Wikidata item using Pywikibot.
  - Handles exceptions if the page doesn't exist or has an invalid title.
  - If an exception occurs, it checks if the title matches any artist name in the `titles_names.csv` file. If a match is found, it uses Spacy with OpenTapioca to identify the Wikidata entity ID.

### Output

[Results]([https://drive.google.com/file/d/1c7xpb-ddZX-euwzadizrtZfmF5k3M-M7/view?usp=drive_link](https://drive.google.com/file/d/1sW40LYfJD4ahD2Q6u5FQVsgjk9fnrWui/view?usp=sharing))
in CSV format with columns:

| Entity ID | Description | Creator Label | Input Text |
|--------|---------|----------|--------------|

Explanation:

- Tool's output columns:
  -  `Entity ID`: URL produced by the tool
  - `Description`: Note or description
      -  `Creator Label`: Artist's name
  -  `Input Text`: Title of an artwork created by the artist
 
  The evaluation results can be found [here](https://docs.google.com/spreadsheets/d/1rt1IuWP7FzdRNpDkWUliqI-vVwrfhYJLdtQziPxEsos/edit?usp=sharing).

## Results

**13625** artworks linked; **2,452** artists link. This method is complemented by [pArtLink](https://github.com/AntonisKl/Entity-Alignment-for-Art/tree/main/p-art-link).
