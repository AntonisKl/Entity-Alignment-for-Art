import csv
import time
from SPARQLWrapper import SPARQLWrapper, JSON, URLENCODED
from bs4 import BeautifulSoup
import unicodedata

def replace_symbols(text):
    soup = BeautifulSoup(text, 'html.parser')
    decoded_text = soup.get_text()
    normalized_text = unicodedata.normalize('NFKD', decoded_text)
    return normalized_text

def execute_query(sparql, query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setRequestMethod(URLENCODED)
    results = sparql.query().convert()
    return results["results"]["bindings"]

# Read and clean the dataset
cleaned_dataset = []
with open('titles_names.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
            cleaned_row = [replace_symbols(entry) for entry in row]
            cleaned_dataset.append(cleaned_row)


# Define the SPARQL endpoint
endpoint_url = "https://query.wikidata.org/sparql"

# Initialize the SPARQL wrapper with endpoint
sparql = SPARQLWrapper(endpoint_url)

# Define the SPARQL query template
query_template = """
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
"""

# Initial delay (in seconds)
delay = 5

# Define the output CSV file path
output_file = "results.csv"

# Read already processed titles from output file
processed_titles = []
try:
    with open(output_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        processed_titles = [replace_symbols(row["Input Text"]) for row in reader]
except FileNotFoundError:
    pass  # if file doesn't exist yet, we'll create it below

# Write the header to the CSV file if it does not exist
if not processed_titles:
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Entity ID", "Description", "Creator Label", "Input Text"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

# Iterate over the cleaned dataset
for row in cleaned_dataset[1:]:
    input_text = row[0].replace('"', r'\"')  # Escape quotation marks in the search text
    input_text2 = row[1]

    # Skip if title already processed
    if input_text in processed_titles:
        continue

    print(f"Processing: {input_text}")

    # Set the input values in the query
    query = query_template.format(input_text=input_text, input_text2=input_text2)

    # Execute the SPARQL query
    try:
        results = execute_query(sparql, query)

        # If no results and the text starts with "the", retry without "the"
        if not results and input_text.lower().startswith('the '):
            query = query_template.format(input_text=input_text[4:], input_text2=input_text2)
            results = execute_query(sparql, query)

        # Process the results and write them to the CSV file
        for result in results:
            entity_id = result["item"]["value"]
            description = result.get("itemDescription", {}).get("value", "N/A")
            creator_label = result.get("creatorLabel", {}).get("value", "N/A")

            # Write the result to the CSV file
            with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Entity ID", "Description", "Creator Label", "Input Text"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({
                    "Entity ID": entity_id,
                    "Description": description,
                    "Creator Label": creator_label,
                    "Input Text": input_text
                })

    except Exception as e:
        print("Error: ", str(e))
        print(f"Delaying for {delay} seconds.")
        time.sleep(delay)
        delay *= 2

print("Results saved to", output_file)
