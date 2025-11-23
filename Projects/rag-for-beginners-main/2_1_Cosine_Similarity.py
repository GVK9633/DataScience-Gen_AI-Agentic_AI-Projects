import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Example 1: Simple vectors
print("=== Example 1: Simple Vectors ===")
vector_a = np.array([2, 1])
vector_b = np.array([1, 2])

# Manual calculation
dot_product = np.dot(vector_a, vector_b)
magnitude_a = np.linalg.norm(vector_a)
magnitude_b = np.linalg.norm(vector_b)
cosine_sim = dot_product / (magnitude_a * magnitude_b)

print(f"Vector A: {vector_a}")
print(f"Vector B: {vector_b}")
print(f"Cosine Similarity: {cosine_sim:.4f}\n")

# Example 2: Text documents
print("=== Example 2: Text Documents ===")
from sklearn.feature_extraction.text import CountVectorizer

documents = [
    "cat cat dog",
    "cat dog dog",
    "bird bird bird"
]

# Convert text to vectors
vectorizer = CountVectorizer()
doc_vectors = vectorizer.fit_transform(documents)

print("Vocabulary:", vectorizer.get_feature_names_out())
print("Document vectors:")
print(doc_vectors.toarray())
print()

# Calculate cosine similarity between all documents
similarities = cosine_similarity(doc_vectors)

print("Cosine Similarity Matrix:")
print(similarities)
print()

# Interpret results
print("Interpretations:")
print(f"Doc 0 vs Doc 1: {similarities[0][1]:.4f} (similar topic, different emphasis)")
print(f"Doc 0 vs Doc 2: {similarities[0][2]:.4f} (completely different topics)")
print(f"Doc 1 vs Doc 2: {similarities[1][2]:.4f} (completely different topics)")

# Example 3: Real-world use case - Finding similar sentences
print("\n=== Example 3: Sentence Similarity ===")
sentences = [
    "The cat sleeps on the mat",
    "A dog rests on the carpet",
    "Python is a programming language",
]

vectorizer2 = CountVectorizer()
sentence_vectors = vectorizer2.fit_transform(sentences)
sentence_similarities = cosine_similarity(sentence_vectors)

print("Sentences:")
for i, sent in enumerate(sentences):
    print(f"  {i}: {sent}")

print("\nSimilarity scores:")
print(f"Sentence 0 vs 1: {sentence_similarities[0][1]:.4f} (both about animals resting)")
print(f"Sentence 0 vs 2: {sentence_similarities[0][2]:.4f} (completely different)")
print(f"Sentence 1 vs 2: {sentence_similarities[1][2]:.4f} (completely different)")

# Example 4: User preference similarity (recommendation systems)
print("\n=== Example 4: User Preferences (Recommendation) ===")
# User ratings for [Action, Comedy, Drama, Horror, Sci-Fi]
user1 = np.array([5, 2, 4, 1, 5])  # Likes action and sci-fi
user2 = np.array([4, 1, 3, 2, 5])  # Also likes action and sci-fi
user3 = np.array([1, 5, 2, 5, 1])  # Likes comedy and horror

users = np.array([user1, user2, user3])
user_similarities = cosine_similarity(users)

print("User preference vectors:")
print("        [Action, Comedy, Drama, Horror, Sci-Fi]")
print(f"User 1: {user1}")
print(f"User 2: {user2}")
print(f"User 3: {user3}")
print()

print("User similarity scores:")
print(f"User 1 vs User 2: {user_similarities[0][1]:.4f} (very similar tastes)")
print(f"User 1 vs User 3: {user_similarities[0][2]:.4f} (opposite tastes)")
print(f"User 2 vs User 3: {user_similarities[1][2]:.4f} (opposite tastes)")