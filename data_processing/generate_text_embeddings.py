#burayı sadece herhangi bir chunk verdiğimizde embedding üretilebiliyor mu diye
#test etmek için yazdım, sistem içerisinde herhangi bir görevi yok

from sentence_transformers import SentenceTransformer
model = SentenceTransformer("emrecan/bert-base-turkish-cased-mean-nli-stsb-tr")

chunks = ["Bu bir test cümlesidir.", "Millî Eğitim Bakanlığı belgeleri analiz ediliyor."]
embs = model.encode(chunks, show_progress_bar=True)
print(embs.shape)  # (2, 768)

from sklearn.metrics.pairwise import cosine_similarity
print(cosine_similarity([embs[0]], embs[1:]))
