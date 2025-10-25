from ollama import Client
from typing import List

client = Client(host="http://localhost:11434")  # Ollama default host

def call_llm(prompt: str, model: str = "mistral:7b-instruct") -> str:
    """LLM çağrısını yapan temel fonksiyon."""
    response = client.generate(model=model, prompt=prompt)
    return response["response"].strip()

def is_rel(question: str, document: str) -> str:
    """Belge ile soru alakalı mı?"""
    prompt = f"""
    Aşağıdaki soru ile belgeyi karşılaştır.

    Eğer belge, sorunun cevabını **doğrudan içeriyor** ya da **sorunun konusu ve içeriğiyle anlamlı biçimde ilgiliyse**, sadece 'evet' yaz.

    Belgede soruyla ilgisiz başka bir konu işleniyorsa ya da belge soruyu cevaplamıyorsa, sadece 'hayır' yaz.

    **Hiçbir açıklama yapma. Sadece 'evet' ya da 'hayır' cevabı ver.**

    Soru:
    {question}

    Belge:
    {document}
    """

    return call_llm(prompt).strip().lower()

def is_sup(question: str, answer: str, document: str) -> str:
    """Belge cevabı destekliyor mu?"""
    prompt = f"""
    Aşağıda bir soru, bu soruya verilmiş bir cevap ve bir belge bulunmaktadır.

    Eğer belge bu cevabı açıkça ya da mantıksal olarak destekliyorsa **sadece** 'evet' yaz. Aksi halde **sadece** 'hayır' yaz. **Hiçbir açıklama yapma.**

    Soru:
    {question}

    Cevap:
    {answer}

    Belge:
    {document}
    """
    return call_llm(prompt).strip().lower()

def is_useful(question: str, answer: str) -> str:
    """Cevap soruyu gerçekten net bir şekilde yanıtladı mı?"""
    prompt = f"""
    Aşağıdaki soruya verilen cevabın soruyu ne kadar iyi karşıladığını değerlendir.

    Eğer cevap soruya net bir şekilde yanıt veriyorsa, yalnızca 'evet' yaz. Eğer cevap belirsiz, yetersiz veya alakasızsa yalnızca 'hayır' yaz. Açıklama yapma.
    
    Soru:
    {question}

    Cevap:
    {answer}
    """
    return call_llm(prompt).strip().lower()


def generate_answer(question: str, docs: List[dict]) -> str:
    """Soru ve belgelerle cevap üreten fonksiyon."""

    doc_texts = [f"{i+1}. {doc['text']}" for i, doc in enumerate(docs)]
    context = "\n".join(doc_texts)

    prompt = f"""
    Aşağıda sana bir soru ve bu soruyla ilgili bazı belgeler verilmiştir. Belgeleri dikkatle inceleyerek soruyu yanıtla.

    Üreteceğin yanıt YALNIZCA TÜRKÇE bir yanıt olsun. Başka bir dilde yanıt üretme.

    Soru:
    {question}

    Belgeler:
    {context}

    Lütfen sadece soruyu yanıtlayan, açık ve doğru bir cevap ver.
    """.strip()

    return call_llm(prompt).strip()

def rewrite_question(question: str) -> str:
    prompt = f"""
    Aşağıda sana bir soru verilmiştir. Lütfen bu sorunun temel anlamını koruyarak, daha açık ve belge aramasına uygun hale getir.

    Yeni soru yalnızca net bir soru cümlesi olmalı. Açıklama yapma, sadece yeni soruyu yaz.

    Yalnızca TÜRKÇE bir soru üret.

    Soru:
    {question}
    """
    return call_llm(prompt).strip()







if __name__ == "__main__":
    # is_rel test
    question = "Yerçekimi kuvveti nedir?"
    document = "Yerçekimi, kütleli cisimlerin birbirini çekmesine neden olan temel bir kuvvettir."
    print("is_rel sonucu:", is_rel(question, document))

    # is_sup test
    answer = "Yerçekimi, cisimlerin birbirini çekmesini sağlar."
    print("is_sup sonucu:", is_sup(question, answer, document))

    # is_useful test
    print("is_useful sonucu:", is_useful(question, answer))

    print("-" * 50)

    # Test 2: Alakasız belge
    question = "Türkiye'nin başkenti neresidir?"
    document = "Türkiye'nin en kalabalık şehri İstanbul'dur."
    print("is_rel sonucu:", is_rel(question, document))

    # Test 3: Doğru ama genel cevap
    answer = "Türkiye büyük bir ülkedir."
    print("is_sup sonucu:", is_sup(question, answer, document))
    print("is_useful sonucu:", is_useful(question, answer))

    print("-" * 50)

    # Test 4: Cevap belirsiz
    question = "Ayasofya ne zaman camiye çevrilmiştir?"
    answer = "Bu olay son yıllarda gerçekleşmiştir."
    document = "Ayasofya 2020 yılında tekrar cami olarak kullanılmaya başlanmıştır."
    print("is_rel sonucu:", is_rel(question, document))
    print("is_sup sonucu:", is_sup(question, answer, document))
    print("is_useful sonucu:", is_useful(question, answer))

    print("-" * 50)

    # Test 5: Doğru cevaplı teknik soru
    question = "Su kaç derecede kaynar?"
    document = "Deniz seviyesinde su 100°C'de kaynar."
    answer = "Evet, su deniz seviyesinde 100 derecede kaynar."
    print("is_rel sonucu:", is_rel(question, document))
    print("is_sup sonucu:", is_sup(question, answer, document))
    print("is_useful sonucu:", is_useful(question, answer))


    question = "Ayasofya ne zaman camiye çevrilmiştir?"
    document = "Deniz seviyesinde su 100°C'de kaynar."
    print("rewrite_question sonucu:", rewrite_question(question))