import csv
import wikipediaapi
import pywikibot
import spacy
import pandas as pd

# Initialize Wikipedia, Pywikibot, and Spacy with OpenTapioca
wiki_wiki = wikipediaapi.Wikipedia('en')
site = pywikibot.Site("en", "wikipedia")
nlp = spacy.blank('en')
nlp.add_pipe('opentapioca')

# Read the artist names from a CSV file
artist_names_df = pd.read_csv('titles_names.csv')

# Read the Wikipedia URLs from the CSV file
with open('wikipedia_urls.csv', 'r', encoding="utf-8") as f:
    reader = csv.reader(f)
    wikipedia_urls = list(reader)

# Open a CSV file for writing
with open('artists2.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # For each URL, get the page title, then use Pywikibot to get the Wikidata item
    for url in wikipedia_urls:
        try:
            # Extract the page title from the URL
            title = url[0].split('/')[-1]

            # Get the Wikipedia page
            page = wiki_wiki.page(title)

            # Use Pywikibot to get the Wikidata item
            page_pywikibot = pywikibot.Page(site, page.title)
            item = pywikibot.ItemPage.fromPage(page_pywikibot)

            # Write the title and Wikidata entity ID to the CSV file
            writer.writerow([title, item.id])
        except (pywikibot.exceptions.NoPageError, pywikibot.exceptions.InvalidTitleError):
            print(f"Unable to find page or invalid title: {title}")
            # Check if the title matches an artist's name in the CSV file
            artist_name = artist_names_df.loc[artist_names_df['Name'] == title]
            if not artist_name.empty:
                # Use Spacy and OpenTapioca on the 'Name' column
                name_to_process = artist_name['Name'].iloc[0]
                doc = nlp(name_to_process)
                for span in doc.ents:
                    # Write the name and Wikidata entity ID to the CSV file
                    writer.writerow([name_to_process, span.kb_id_])
