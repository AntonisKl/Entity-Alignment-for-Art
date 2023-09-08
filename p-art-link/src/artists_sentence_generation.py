import csv
from time import time
import pandas as pd
from gpt4all import GPT4All
import os

HERE = os.path.dirname(os.path.realpath(__file__))

INPUT_FILE_PATH = os.path.join(HERE, "../data/input_artists_with_artworks.csv")
OUTPUT_FILE_PATH = os.path.join(HERE, "../data/artist_artwork_sentence.csv")

prompt = """[INST] <<SYS>>
You are a helpful AI assistant for finding information about artists.
Your answer must contain only one line. Your answer must follow this template: "artist_name: info_about_artist".
Your answer must not include any other text than the answer itself.
<</SYS>>

Write a short sentence about the artist {artist} who created "{artwork}" [/INST]
"""


def generate_sentence(chat_model, artist, artwork):
    return chat_model.generate(prompt.format(artist=artist, artwork=artwork))


if __name__ == "__main__":
    artist_artwork_df = pd.read_csv(INPUT_FILE_PATH)

    artists_to_link = list(artist_artwork_df["artist"].values)
    artworks_of_artists_to_link = list(artist_artwork_df["artwork"].values)

    chat_model = GPT4All("llama-2-7b-chat.ggmlv3.q4_0.bin")

    sentences = []
    for artist, artwork in zip(artists_to_link, artworks_of_artists_to_link):
        sentence = generate_sentence(chat_model, artist, artwork)
        sentences.append(sentence)

    pd.DataFrame(
        {
            "artist": artists_to_link,
            "artwork": artworks_of_artists_to_link,
            "sentence": sentences,
        }
    ).to_csv(
        OUTPUT_FILE_PATH,
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        doublequote=False,
        index=False,
    )
