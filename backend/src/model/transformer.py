import os
from transformers import BartForConditionalGeneration, BartTokenizer

os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid deadlock warnings

# Models dictionary (for future extension)
models = {
    'BART': 'facebook/bart-large-cnn',
}

model_name = 'BART'

def load_model_and_tokenizer():
    if model_name == 'BART':
        model = BartForConditionalGeneration.from_pretrained(models['BART'])
        tokenizer = BartTokenizer.from_pretrained(models['BART'])
    else:
        raise ValueError(f"Model {model_name} is not supported.")
    return model, tokenizer

def generate_summary(filepath, min_length, max_length):
    """
    Generates a summary of the given text file between min_length and max_length using the selected model.

    Args:
        filepath (str): Path to the file to summarize.
        min_length (int): Minimum number of words in the summary.
        max_length (int): Maximum number of words in the summary.

    Returns:
        str: Generated summary text.
    """
    # Load the model and tokenizer
    model, tokenizer = load_model_and_tokenizer()

    # Load text from the file
    with open(filepath, 'r') as file:
        text = file.read()

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

    # Generate summary
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        num_beams=4,
        early_stopping=True
    )

    # Decode the summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary.strip()

def improve_text(filepath: str) -> str:
    """
    Improves grammar, clarity, and coherence of the entire file text using the selected model.

    Args:
        filepath (str): Path to the file to process and improve.

    Returns:
        str: Improved full text as a single string.
    """
    # Load the model and tokenizer
    model, tokenizer = load_model_and_tokenizer()

    # Load text from the file
    with open(filepath, 'r') as file:
        text = file.read()

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

    # Generate improved text
    improved_ids = model.generate(
        inputs["input_ids"],
        max_length=len(text.split()) + 50,  # Allow the output to grow longer to capture rewritten improvements
        min_length=len(text.split()) - 50,
        num_beams=4,
        early_stopping=True
    )

    # Decode the improved text
    improved_text = tokenizer.decode(improved_ids[0], skip_special_tokens=True)

    return improved_text.strip()
