from core import settings
from generation.hypothesis_expansion import generate_queries as generate_queries_core 



def generate_queries(hypothesis: str, num_queries: str, model: str, template_path: str):
    queries = generate_queries_core(
        hypothesis,
        num_queries=num_queries,
        model=model,
        template_path=template_path
        )
    return queries