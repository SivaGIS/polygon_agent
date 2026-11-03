"""Step 1: what embeddings are. No API key needed.

Run it and look at the scores: phrases with similar MEANING score high even when they
share no words ("flash flood" vs "high water on roadways").
"""
from embeddings import embed, cosine

phrases = [
    "flash flood warning",
    "high water on roadways",
    "wildfire smoke",
    "brush fire spreading",
    "I-10 Katy Freeway",
    "interstate highway",
    "shopping mall",
]

vectors = embed(phrases)
print(f"Each phrase became a vector of {vectors.shape[1]} numbers.\n")

print("Similarity (1.0 = same meaning, near 0 = unrelated)\n")
print(" " * 24 + "".join(f"{i:>6}" for i in range(len(phrases))))
for i, p in enumerate(phrases):
    row = "".join(f"{cosine(vectors[i], vectors[j]):6.2f}" for j in range(len(phrases)))
    print(f"{i} {p[:21]:<22}{row}")

print("\nTry it: add your own phrases, e.g. 'pipeline rupture' and 'natural gas leak'.")
