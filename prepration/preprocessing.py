import pandas as pd
from core import settings

from prepration.preprocessing_patterns import parse_and_clean_email
from prepration.chunking import build_chunk_df
from prepration.normalization import apply_method_normalization


def preprocess_emails(emails_df_address=settings.EMAILS_CSV_PATH) -> pd.DataFrame:

    # Load and reset index to create email_id, drop docID as it's no longer needed
    emails_df = pd.read_csv(emails_df_address)
    emails_df["email_id"] = emails_df.reset_index(drop=True).index
    emails_df = emails_df.drop(columns=["docID"])

    # Apply preprocessing to the message column and expand the resulting dictionaries into separate columns
    parsed_dicts = emails_df["message"].apply(parse_and_clean_email)
    emails_df = pd.concat(
        [emails_df, pd.json_normalize(parsed_dicts)],
        axis=1
    )

    # Messages with insufficient newly authored textual content removed during preprocessing
    emails_df = emails_df[emails_df["len_base"] >= 80].reset_index(drop=True)

    # Drop columns that are no longer needed after preprocessing
    columns_to_drop = ['len_base', 'message']
    emails_df = emails_df.drop(columns=columns_to_drop)

    return emails_df


def apply_chunking_and_normalization():
    cleaned_emails_df = preprocess_emails(settings.EMAILS_CSV_PATH)
    chunk_df = build_chunk_df(
                cleaned_emails_df,
                email_id_col="email_id",
                text_col="body_base",
                min_chars=200,
                max_chars=1200
            )
    chunk_df = apply_method_normalization(chunk_df)

    # chunk_df.to_csv(
    #     settings.BASE_DIR / "whole_chunks.csv",
    #     index=False,
    #     encoding="utf-8",
    # )

    return chunk_df
