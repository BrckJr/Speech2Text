import os
from transformers import pipeline, MBartForConditionalGeneration, MBart50TokenizerFast, T5ForConditionalGeneration, T5Tokenizer, BartForConditionalGeneration, BartTokenizer, GPTNeoForCausalLM, GPT2Tokenizer

os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid deadlock warnings

# Models dictionary
models = {
    'T5': 'google-t5/t5-large',
    'BART': 'facebook/bart-large-cnn',
    'GPT-Neo': 'EleutherAI/gpt-neo-1.3B', # Does not work for long sequences!!
}


model_name='BART'

# Function to load model and tokenizer based on the selected model
def load_model_and_tokenizer():
    if model_name == 'T5':
        model = T5ForConditionalGeneration.from_pretrained(models['T5'])
        tokenizer = T5Tokenizer.from_pretrained(models['T5'])
    elif model_name == 'BART':
        model = BartForConditionalGeneration.from_pretrained(models['BART'])
        tokenizer = BartTokenizer.from_pretrained(models['BART'])
    elif model_name == 'GPT-Neo':
        model = GPTNeoForCausalLM.from_pretrained(models['GPT-Neo'])
        tokenizer = GPT2Tokenizer.from_pretrained(models['GPT-Neo'])  # GPT-Neo uses GPT2 tokenizer
    else:
        raise ValueError(f"Model {model_name} is not supported.")
    return model, tokenizer

# Function to generate summary using the selected model
def generate_summary(filepath, min_length, max_length, ):
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

    # Generate summary (set the source and target languages as needed)
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

# Function to improve text using the selected model
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

    # Generate improved text (set the source and target languages as needed)
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
