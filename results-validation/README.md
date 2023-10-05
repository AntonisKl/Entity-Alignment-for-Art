This folder contains three files:
1. Fleiss Kappa is a notebook containing the validation of agreement between the 5 reviewers.
Three scores were used for the evaluation: Fleiss Kappa, Percentage of agreement and, Rodolph Kappa. For more information, refer to the article in this repository.
2. The other two Python files: Artist and Artwork validation, use the WIKIDATA API. Both scripts can reduce the manual work of proofs, e.g., to validate if an artwork was correctly associated with its Wikidata ID. 
Each file follows the criteria agreed upon by the reviewers. For example, an artwork was correctly associated if, on the Wikidata page, the name of the artwork and the name of its respective artist were found, regardless of language, or special characters.
For the artist, the criteria were: Name, nationality, and occupation.