"""
app.options.py
--------------
Static UI constants used for dropdowns and light validation.

Quick test:
>>> from app.options import VALID_GENRES

Author: **Suganya P**
"""

VALID_LANGUAGES = ["en", "ta", "hi", "es"]
VALID_GENRES = ["fantasy", "fiction", "non-fiction", "education", "picture book"]
VALID_AGES = ["0-2", "3-5", "6-8", "9-12", "13+"]


# Mapping from dataset genres (raw or varied terms) to standardized VALID_GENRES
GENRE_MAP = {
    # Direct or close matches
    "Nature": "Nature",
    "Mythology": "Fantasy",           # Mythology conceptually fits Fantasy
    "Values": "Educational",          # Values themed books are Educational
    "Education": "Educational",
    "Educational": "Educational",     # Already standardized

    "Adventure": "Adventure",
    "Adventures": "Adventure",        # Handling plural variant

    "Mystery": "Mystery",

    # Other mapped or variant terms
    "Myths": "Fantasy",
    "Fairy Tale": "Fairy Tale",
    "Science Fiction": "Science Fiction",
    "Biography": "Biography",
    "Historical": "Historical",
    "Poetry": "Poetry",

    # Placeholder for future mappings, e.g.:
    # "Myth": "Fantasy",
    # "Fairy Tales": "Fairy Tale",
}

# Validation block to make sure all mapped genres exist in VALID_GENRES
for mapped_genre in set(GENRE_MAP.values()):
    if mapped_genre not in VALID_GENRES:
        raise ValueError(f"Mapped genre '{mapped_genre}' is not in VALID_GENRES")
