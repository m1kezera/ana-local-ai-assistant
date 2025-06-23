import logging
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import random
from modules.system_control import executar_comando, abrir_programa, MASTER_OVERRIDE

class AnaBrain:
    def __init__(self):
        self.knowledge_base = {}
        self.concepts = []
        self.texts = []
        self.nlp = spacy.load("pt_core_news_sm")
        self.vectorizer = TfidfVectorizer()
        self.graph = nx.DiGraph()
        self.tfidf_matrix = None
        logging.info("ANA Brain avançada inicializada.")

    def learn(self, concept, text):
        self.knowledge_base[concept] = text
        self.concepts.append(concept)
        self.texts.append(text)
        self.graph.add_node(concept)
        logging.info(f"Aprendido conceito: {concept}")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.texts)

    def query(self, question):
        logging.info(f"Pergunta recebida: {question}")
        if not self.texts:
            return "Ainda não aprendi nada para responder."
        question_vec = self.vectorizer.transform([question])
        similarities = cosine_similarity(question_vec, self.tfidf_matrix).flatten()
        best_idx = similarities.argmax()
        best_concept = self.concepts[best_idx]
        best_text = self.knowledge_base[best_concept]
        resposta = f"Baseado no conceito '{best_concept}': {best_text}"
        return resposta

    def summarize(self):
        num_concepts = len(self.concepts)
        num_edges = self.graph.number_of_edges()
        return f"Conhecimento: {num_concepts} conceitos; Relações: {num_edges} conexões."

    def agir(self):
        if not MASTER_OVERRIDE:
            return "🔒 Ação bloqueada pelo failsafe."

        if not self.concepts:
            return "Não há conhecimento suficiente para agir."

        escolhas = [
            ("abrir", "code"),
            ("abrir", "explorer"),
            ("cmd", "dir"),
            ("cmd", "echo ANA presente")
        ]
        acao, parametro = random.choice(escolhas)

        if acao == "abrir":
            resultado = abrir_programa(parametro)
            return f"🧠 Decisão autônoma: Abrindo {parametro}\n{resultado}"
        elif acao == "cmd":
            saida = executar_comando(parametro)
            return f"🧠 Decisão autônoma: Executando comando '{parametro}'\n{saida}"
        else:
            return "(ação desconhecida)"
