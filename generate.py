import os
import subprocess
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
from huggingface_hub import login

class GitCommitGenerator:
    def __init__(self):
        """
        Initialize the Git Commit Generator using a reliable Hugging Face model.
        """
        # Load environment variables
        load_dotenv()
        
        # Retrieve Hugging Face token from environment variable
        hf_token = os.getenv('HUGGINGFACE_TOKEN')
        
        # Authenticate with Hugging Face
        try:
            if hf_token:
                login(token=hf_token)
                print("Successfully authenticated with Hugging Face")
            else:
                print("No Hugging Face token found. Using public models.")
        except Exception as e:
            print(f"Authentication error: {e}")
        
        # Load pre-trained model for text generation
        try:
            # Use a reliable, lightweight model
            model_name = "microsoft/DialoGPT-small"
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
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
            prompt = f"Generate a git commit message for these code changes:\n{truncated_diff}"
            
            # Encode the input
            input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
            
            # Generate response
            output = self.model.generate(
                input_ids, 
                max_length=100, 
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Extract commit message (try to clean it up)
            commit_message = generated_text.split('\n')[-1].strip()
            
            # Fallback and sanitization
            if not commit_message or len(commit_message) < 10:
                return "chore: update code changes"
            
            # Ensure it follows conventional commit format
            if not commit_message.split(':')[0] in ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']:
                commit_message = f"chore: {commit_message}"
            
            return commit_message
        
        except Exception as e:
            print(f"Commit message generation error: {e}")
            return "chore: update code changes"
    
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