import sys
from pathlib import Path
from typing import Union, Type
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.logging import RichHandler
from rich.console import Console
import logging
path = Path(__file__).parent.parent.parent
sys.path.append(str(path))

from .claim_norm import ClaimNorm
from utils.anthropic import AnthropicModel
from utils.gemini import GeminiModel
from utils.openai import OpenAIModel
from utils.xai import xAIModel
from schemas.claims import NormalizedClaim
from schemas.feedback import Feedback
from utils.prompts import sys_prompt, instruction, chain_of_thought_trigger, few_shot_prompt, few_shot_CoT_prompt, feedback_prompt, feedback_sys_prompt, refine_sys_prompt

class Refine:
    def __init__(self, model: Union[OpenAIModel, xAIModel, AnthropicModel, GeminiModel], num_iters: int):
        self.model = model
        self.num_iters = num_iters
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        # Configure logging with Rich handler
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=self.console, rich_tracebacks=True)]
        )
        self.feedback_sys_prompt = feedback_sys_prompt
        self.refine_sys_prompt = refine_sys_prompt
        
    def refine_claim(self, original_query: str, current_claim: str):
        try:
            # Process data with progress tracking
            with open(self.results_file_path, 'w') as results_file:
                progress_bar = Progress(
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    BarColumn(),
                    MofNCompleteColumn(),
                    TextColumn("•"),
                    TimeElapsedColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=self.console,
                    transient=False  # Keep progress bar visible after completion
                )
                with progress_bar as p:
                    task = p.add_task("🧠 Refining Claim", total=self.num_iters)
                    for index in range(self.num_iters):
                        try:
                            feedback_sys_prompt = self.feedback_sys_prompt
                            feedback_user_prompt = f"""
                                ## Original Query
                                {original_query}

                                ## Current Response  
                                {current_claim}

                                ## Task
                                {feedback_prompt}
                            """
                            feedback = self._get_feedback(feedback_user_prompt, feedback_sys_prompt)
                            if feedback is not None and feedback.score > 0.5:
                                
                             
                            # Advance progress bar
                            p.advance(task)
                             
                        except Exception as e:
                            self.logger.error(f"❌ Error processing item {index}: {e}")
                            p.advance(task)  # Still advance even on error
        
        finally:
            # Clean up cache when done
            if self.cache_context and self._cache_initialized and self.cache_id:
                try:
                    self.teacher_model.delete_cached_content(self.cache_id)
                    self.logger.info("🧹 Cleaned up context cache")
                except Exception as e:
                    self.logger.warning(f"Failed to clean up cache: {e}")
            
        self.console.print(f"\n✅ [green]Refinement completed![/green] Processed {self.num_iters} items.")
        self.console.print(f"📁 Results saved to {self.results_file_path}")
    
    def _get_feedback(self, feedback_user_prompt: str, feedback_sys_prompt: str) -> Feedback:
        return self.model.generate_structured_response(feedback_sys_prompt, feedback_user_prompt)
