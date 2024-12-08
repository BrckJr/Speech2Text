import os
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
os.environ["TOKENIZERS_PARALLELISM"] = "false" # Avoid an error message for huggingface/tokenizer because of deadlock warning

# Load the GPT-J Model and Tokenizer
model_name = "EleutherAI/gpt-neo-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Load the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis")

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

def improve_text(filepath: str) -> str:
    """
    Sends the input text to GPT-J to improve grammar, clarity, and readability.

    Args:
        filepath (str): Text file which should be improved

    Returns:
        str: Improved text

    """
    # Load textfile to for which he summary is requested
    with open(filepath, 'r') as file:
        text = file.read()

    # Prompt construction to improve grammar, clarity, and readability
    prompt_text = "Improve the following text for grammar, clarity, and coherence:\n\n" + text

    # Tokenize input
    input_ids = tokenizer(prompt_text, return_tensors="pt").input_ids

    # Generate output from GPT-J
    output = model.generate(
        input_ids,
        max_length=len(input_ids[0]) + 200,  # Generate additional context
        do_sample=True,  # Random sampling for variation
        temperature=0.7,  # Adjust temperature for creativity
    )

    # Decode the output text
    improved_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return improved_text