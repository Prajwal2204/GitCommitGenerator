import os
import subprocess
from transformers import pipeline
from dotenv import load_dotenv
from huggingface_hub import login, HfApi

class GitCommitGenerator:
    def __init__(self):
        """
        Initialize the Git Commit Generator using Hugging Face model with authentication.
        """
        # Load environment variables
        load_dotenv()
        
        # Retrieve Hugging Face token from environment variable
        hf_token = os.getenv('HUGGINGFACE_TOKEN')
        
        # Authenticate with Hugging Face
        try:
            if hf_token:
                # Login using token
                login(token=hf_token)
                print("Successfully authenticated with Hugging Face")
            else:
                # Prompt for interactive login if no token is found
                print("No Hugging Face token found. Attempting interactive login.")
                login()
        except Exception as e:
            print(f"Authentication error: {e}")
        
        # Load pre-trained model for text generation
        try:
            self.generator = pipeline(
                'text-generation', 
                model='bigcode/speedcoder-small',  # Lightweight code generation model
                use_auth_token=hf_token  # Pass token for model access
            )
        except Exception as e:
            print(f"Model loading error: {e}")
            self.generator = None
    
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
        Generate commit message using Hugging Face model.
        """
        if not diff or not self.generator:
            return "chore: update code changes"
        
        # Truncate diff to prevent excessive token usage
        max_diff_length = 2000
        truncated_diff = diff[:max_diff_length]
        
        try:
            # Generate commit message
            prompt = f"Generate a git commit message for these code changes:\n{truncated_diff}\n\nCommit message:"
            messages = self.generator(
                prompt, 
                max_length=100, 
                num_return_sequences=1
            )
            
            # Extract and clean the generated message
            commit_message = messages[0]['generated_text'].split('\n')[-1].strip()
            
            # Fallback if message is empty
            return commit_message or "chore: update code changes"
        
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