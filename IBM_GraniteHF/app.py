import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from functools import lru_cache
import re

# Load the Granite model
model_path = "ibm-granite/granite-3.2-2b-instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

@lru_cache(maxsize=1)
def load_model():
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    return model, tokenizer

model, tokenizer = load_model()

def audio_friendly_formatting(text):
    """Format text to be more audio-friendly for TTS conversion"""
    # Remove excessive punctuation
    text = re.sub(r'[.]{2,}', '...', text)
    
    # Ensure proper spacing after punctuation
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    # Convert numbers to words for better TTS pronunciation
    numbers = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', 
              '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '0': 'zero'}
    for num, word in numbers.items():
        text = text.replace(num, word)
    
    # Add pauses for better audio pacing
    text = re.sub(r'([,;:])', r'\1 ', text)
    
    # Ensure sentences end with proper punctuation
    sentences = text.split('. ')
    formatted_sentences = []
    for sentence in sentences:
        if sentence and not sentence.endswith(('.', '!', '?')):
            sentence += '.'
        formatted_sentences.append(sentence)
    
    return '. '.join(formatted_sentences)

def rewrite_tone(text, tone, max_tokens=1000):
    """Rewrite text in specified tone optimized for audio"""
    
    tone_prompts = {
        "neutral": """You are an expert text rewriter. Rewrite the following text in a clear, neutral, and professional tone. 
        Make it suitable for audio narration by using simple sentence structures, avoiding complex punctuation, 
        and ensuring smooth flow. Keep the same meaning but make it sound natural when spoken aloud.""",
        
        "suspenseful": """You are an expert text rewriter. Rewrite the following text in a suspenseful, mysterious tone 
        that builds tension and intrigue. Use shorter sentences for dramatic effect, create anticipation, 
        and add elements that will sound engaging when narrated as audio. Make listeners want to know what happens next.""",
        
        "inspiring": """You are an expert text rewriter. Rewrite the following text in an inspiring, motivational tone 
        that uplifts and energizes the reader. Use positive language, powerful imagery, and rhythmic phrases 
        that will sound compelling when spoken aloud. Make it emotionally resonant and encouraging."""
    }
    
    system_prompt = tone_prompts.get(tone, tone_prompts["neutral"])
    
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please rewrite this text: {text}"}
    ]
    
    # Apply chat template
    input_ids = tokenizer.apply_chat_template(
        conversation, 
        return_tensors="pt", 
        add_generation_prompt=True,
        return_dict=True
    ).to(device)
    
    # Generate response
    with torch.no_grad():
        output = model.generate(
            **input_ids,
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode response
    response = tokenizer.decode(
        output[0, input_ids["input_ids"].shape[1]:], 
        skip_special_tokens=True
    )
    
    # Apply audio-friendly formatting
    formatted_response = audio_friendly_formatting(response)
    
    return formatted_response

def process_text(input_text, selected_tone):
    """Main processing function"""
    if not input_text.strip():
        return "Please enter some text to rewrite."
    
    try:
        rewritten_text = rewrite_tone(input_text, selected_tone)
        return rewritten_text
    except Exception as e:
        return f"Error processing text: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Tone Rewriter for Audio") as iface:
    gr.Markdown("# 🎯 Tone Rewriter for Audio Conversion")
    gr.Markdown("Transform your text into different tones optimized for text-to-speech conversion using IBM Granite 3.2-2B-Instruct")
    
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Input Text",
                placeholder="Enter the text you want to rewrite...",
                lines=6,
                max_lines=10
            )
            
            tone_selector = gr.Radio(
                choices=["neutral", "suspenseful", "inspiring"],
                label="Select Tone",
                value="neutral",
                info="Choose the tone for rewriting"
            )
            
            rewrite_btn = gr.Button("Rewrite Text", variant="primary")
        
        with gr.Column():
            output_text = gr.Textbox(
                label="Rewritten Text (Audio-Optimized)",
                lines=8,
                max_lines=15,
                interactive=False
            )
    
    # Examples
    gr.Examples(
        examples=[
            ["The company announced its quarterly results yesterday. Sales increased by fifteen percent compared to last year.", "neutral"],
            ["The old house stood at the end of the street. Nobody had lived there for years.", "suspenseful"],
            ["Every challenge is an opportunity to grow. You have the strength to overcome any obstacle.", "inspiring"]
        ],
        inputs=[input_text, tone_selector],
        outputs=output_text,
        fn=process_text
    )
    
    rewrite_btn.click(
        fn=process_text,
        inputs=[input_text, tone_selector],
        outputs=output_text
    )

if __name__ == "__main__":
    iface.launch()
