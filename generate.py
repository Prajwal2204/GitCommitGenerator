import os
import subprocess
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv

class GitCommitGenerator:
    def __init__(self):
        """
        Initialize the Git Commit Generator using a reliable Hugging Face model.
        """
        # Load environment variables
        load_dotenv()
        
        # Load pre-trained model for text generation
        try:
            # Use a reliable model
            model_name = "gpt2"
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Set pad token if not already set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            print(f"Loaded model: {model_name}")
        except Exception as e:
            print(f"Model loading error: {e}")
            self.tokenizer = None
            self.model = None
    
    def get_git_diff(self):
        """
        Retrieve git diff of staged changes.
        """
        try:
            return subprocess.check_output(
                ['git', 'diff', '--cached'], 
                universal_newlines=True
            )
        except subprocess.CalledProcessError:
            print("Error retrieving git diff")
            return ""
    
    def generate_commit_message(self, diff):
        """
        Generate commit message using the loaded model.
        """
        if not diff or not self.model or not self.tokenizer:
            return "chore: update code changes"
        
        # Truncate diff to prevent excessive token usage
        max_diff_length = 1000
        truncated_diff = diff[:max_diff_length]
        
        try:
            # Prepare the prompt
            prompt = f"""You are an expert at generating concise and meaningful git commit messages.
Given the following code changes, generate a precise commit message that follows conventional commit guidelines:

Code Changes:
{truncated_diff}

Generate a commit message that:
1. Starts with a conventional commit prefix (feat, fix, docs, style, refactor, test, chore)
2. Is under 50 characters
3. Clearly describes the changes made

Commit Message:"""
            
            # Encode the input with explicit padding and attention mask
            inputs = self.tokenizer(
                prompt, 
                return_tensors='pt', 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            # Generate response with sampling enabled
            generation_params = {
                'max_length': inputs['input_ids'].shape[1] + 50,  # Extend beyond input length
                'num_return_sequences': 1,
                'do_sample': True,  # Enable sampling
                'temperature': 0.7,  # Creative temperature
                'top_k': 50,  # Top-k sampling
                'top_p': 0.95,  # Nucleus sampling
                'no_repeat_ngram_size': 2,  # Prevent repetition
            }
            
            # Generate output
            output = self.model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                **generation_params
            )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Extract and clean commit message
            commit_message = self._clean_commit_message(generated_text, prompt)
            
            return commit_message
        
        except Exception as e:
            print(f"Commit message generation error: {e}")
            return "chore: update code changes"
    
    def _clean_commit_message(self, generated_text, prompt):
        """
        Clean and format the generated commit message.
        
        :param generated_text: Full generated text
        :param prompt: Original prompt
        :return: Cleaned commit message
        """
        # Remove the prompt from the generated text
        cleaned_text = generated_text.replace(prompt, '').strip()
        
        # Split into lines and take the first meaningful line
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        commit_message = lines[0] if lines else "chore: update code changes"
        
        # Ensure conventional commit format
        conventional_prefixes = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
        if not any(commit_message.startswith(prefix) for prefix in conventional_prefixes):
            commit_message = f"chore: {commit_message}"
        
        # Limit message length
        return commit_message[:72]
    
    def auto_commit(self):
        """
        Automatically generate and commit changes.
        """
        diff = self.get_git_diff()
        
        if not diff:
            print("No changes to commit.")
            return
        
        commit_message = self.generate_commit_message(diff)
        
        try:
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print(f"Committed with message: {commit_message}")
        except subprocess.CalledProcessError:
            print("Commit failed.")

def main():
    generator = GitCommitGenerator()
    generator.auto_commit()

if __name__ == "__main__":
    main()