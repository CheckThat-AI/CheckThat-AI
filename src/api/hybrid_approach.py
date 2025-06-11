"""
Hybrid approach: Web service for chat + GitHub Actions for batch evaluation
"""
import httpx
import json
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import os

app = FastAPI()

class GitHubActionsClient:
    def __init__(self, repo_owner: str, repo_name: str, token: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    async def trigger_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger GitHub Actions workflow for batch evaluation"""
        
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # Upload dataset to GitHub (could use Gist or repository)
        dataset_url = await self._upload_dataset(evaluation_data['file_data'])
        
        payload = {
            "event_type": "run-evaluation",
            "client_payload": {
                "models": ",".join(evaluation_data['models']),
                "prompt_styles": ",".join(evaluation_data['prompt_styles']),
                "dataset_url": dataset_url,
                "refine_iterations": evaluation_data.get('self_refine_iterations', 0),
                "issue_number": evaluation_data.get('issue_number')  # For posting results
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/dispatches",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 204:
                return {"status": "success", "message": "Evaluation started on GitHub Actions"}
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to trigger GitHub Actions: {response.text}"
                )
    
    async def _upload_dataset(self, file_data: Dict[str, str]) -> str:
        """Upload dataset to GitHub Gist and return URL"""
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # Decode base64 content
        import base64
        content = base64.b64decode(file_data['content']).decode('utf-8')
        
        gist_payload = {
            "description": f"Evaluation dataset: {file_data['name']}",
            "public": False,
            "files": {
                file_data['name']: {
                    "content": content
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.github.com/gists",
                headers=headers,
                json=gist_payload
            )
            
            if response.status_code == 201:
                gist_data = response.json()
                # Return raw URL for the file
                return gist_data['files'][file_data['name']]['raw_url']
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload dataset to GitHub"
                )

@app.post("/api/evaluation/github-actions")
async def start_github_evaluation(evaluation_data: Dict[str, Any]):
    """Start evaluation using GitHub Actions instead of local processing"""
    
    github_client = GitHubActionsClient(
        repo_owner=os.getenv("GITHUB_REPO_OWNER"),
        repo_name=os.getenv("GITHUB_REPO_NAME"), 
        token=os.getenv("GITHUB_TOKEN")
    )
    
    result = await github_client.trigger_evaluation(evaluation_data)
    return result

@app.get("/api/evaluation/status/{run_id}")
async def get_evaluation_status(run_id: str):
    """Get status of GitHub Actions evaluation run"""
    
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{os.getenv('GITHUB_REPO_OWNER')}/{os.getenv('GITHUB_REPO_NAME')}/actions/runs/{run_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            run_data = response.json()
            return {
                "status": run_data["status"],  # queued, in_progress, completed
                "conclusion": run_data.get("conclusion"),  # success, failure, etc.
                "created_at": run_data["created_at"],
                "updated_at": run_data["updated_at"]
            }
        else:
            raise HTTPException(status_code=404, detail="Run not found") 