from core import settings
from generation.hypothesis_expansion import generate_queries as generate_queries_core 



def generate_queries(hypothesis: str):
    queries = generate_queries_core(
        hypothesis,
        num_queries=settings.HE_QUERIES,
        max_query_length=settings.HE_MAX_LENGTH,
        model=settings.HE_MODEL
        )
    return queries