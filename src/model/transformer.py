import os
from transformers import pipeline

os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid deadlock warnings

# Comparison of models for sustainability-demo text:
# Model         | Headline Quality | Summary Quality | Text Improvement Quality | Time for Analysis
# --------------|------------------|-----------------|--------------------------|-------------------
# T5            |          -       |        o        |             --           |   227.05 seconds
# BART          |          -       |        o        |             -            |    91.44 seconds


models = {
    'T5': 'google-t5/t5-large',
    'BART': 'facebook/bart-large-cnn',
}

# Use one of the above-mentioned pretrained models as the pipeline
summarizer = pipeline("summarization", model=models['BART'])

def generate_summary(filepath, min_length, max_length):
    """
    Generates a summary of the given text file between min_length and max_length.
    Args:
        filepath (str): Path to the file to summarize.
        min_length (int): Minimum number of words in the summary.
        max_length (int): Maximum number of words in the summary.

    Returns:
        str: Generated summary text.
    """
    # Load text from the file
    with open(filepath, 'r') as file:
        text = file.read()

    # Generate a summary (use the pipeline with defined min and max lengths)
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)

    # Return the summary text
    return summary[0]['summary_text'].strip()

def improve_text(filepath: str) -> str:
    """
    Improves grammar, clarity, and coherence of the entire file text using BART.

    It basically just takes the transcription, feeds it one time through the BART model and takes the
    output as the improved text.
    It uses the same model as the summary tool to be sure the text stays approximately the same.

    Args:
        filepath (str): Path to the file to process and improve.

    Returns:
        str: Improved full text as a single string.
    """
    # Load text from the file
    with open(filepath, 'r') as file:
        text = file.read()

    # Use the summarization pipeline to rewrite the full text to improve clarity and grammar
    improved_text = summarizer(
        text,
        max_length=len(text.split()) + 50,  # Allow the output to grow longer to capture rewritten improvements
        min_length=len(text.split()) - 50,
        do_sample=False
    )

    # Return the improved, rewritten text
    return improved_text[0]['summary_text'].strip()