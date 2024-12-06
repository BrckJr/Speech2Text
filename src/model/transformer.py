from transformers import pipeline

# Load the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(filepath, min_length, max_length):
    """
    This method provides a summary of the file with the provided filepath.

    To make the summary, the transformer library from Hugging Face is used. The length of the summary will be in
    between the min_length and max_length respectively to be able to generate headings as well as actual summaries
    of individual length.

    Args:
        filepath: Text file which should be summarized
        min_length: Minimum number of the length the summary should have
        max_length: Maximum number of the length the summary should have

    Returns:
        str: The summary of the file with the requested length
    """

    # Load textfile to for which he summary is requested
    with open(filepath, 'r') as file:
        text = file.read()

    # Generate a short summary which will act as the heading
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)

    # Return the summary text (heading)
    return summary[0]['summary_text'].strip()
