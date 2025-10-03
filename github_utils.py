import os
from github import Github

def update_github_file(file_path, new_content):
    # Authenticate with GitHub
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo("arashid02-n/copeywriting")  # replace with your repo
    
    try:
        file = repo.get_contents(file_path, ref="main")
        repo.update_file(
            file.path,
            "Update copy with AI suggestion",
            new_content,
            file.sha,
            branch="main"
        )
    except Exception as e:
        # If file doesn't exist, create it
        repo.create_file(
            file_path,
            "Create new file with AI suggestion",
            new_content,
            branch="main"
        )
