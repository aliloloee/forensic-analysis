from app.main_window import App


if __name__ == "__main__":
    app = App()
    app.mainloop()




########## Bulk Ingestion ##########
# from core import settings
# from prepration.embedding import read_embeddings
# from prepration.preprocessing import apply_chunking_and_normalization
# from core.settings import EMBEDDINGS_DIR
# from core.weaviate_client import get_client
# from chunks.ingest import ingest_chunks, ingest_emails
# from chunks.collection import create_chunk_collection, create_email_collection


# def bulk_ingestion():
#     emails_df, chunk_df = apply_chunking_and_normalization()

#     # if settings.INGESTION: ## Needs to be updated
#     #     chunk_df.to_csv(
#     #         settings.BASE_DIR / "whole_chunks.csv",
#     #         index=False,
#     #         encoding="utf-8",
#     #     )

#     #### This part need to be updated to compute embeddings instead of reading from file
#     embeddings = read_embeddings(EMBEDDINGS_DIR)

#     if len(chunk_df) != len(embeddings):
#         raise ValueError(f"Length mismatch: chunk_df has {len(chunk_df)} rows, but embeddings has {len(embeddings)} vectors.")
    
#     client = get_client()

#     create_email_collection(client)
#     ingest_emails(client, emails_df)

#     create_chunk_collection(client)
#     ingest_chunks(client, chunk_df, embeddings)

#     client.close()


# bulk_ingestion()
####################################