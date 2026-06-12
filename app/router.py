from semantic_router import Route, SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.index import LocalIndex

encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)
faq = Route(
    name = 'faq',
    utterances= [
        "What is the return policy of the product?",
        "Do i get discount with HDFC bank Credit card?",
        "How can i track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?"
    ]
)

sql = Route(
    name = 'sql',
    utterances= [
        "I want to buy nike shoes that have 50 percent discount",
        "Are there any shoes under Rs. 4000?",
        "Are there any puma shoes on sale?",
        "What is the proce of puma running shoes?"
    ]
)
index = LocalIndex()
router =  SemanticRouter(routes=[faq,sql], encoder=encoder, auto_sync="local", index= index)

if __name__ == "__main__":
    print(router("How can i track my order?").name)
    print(router("Pink Puma shoes in price range 5000 to 1000").name)