from langfuse import Langfuse
from typing import Dict, Any, List
import uuid
import config

class LangfuseTracer:
    def __init__(self):
        self.langfuse = Langfuse(
            secret_key=config.LANGFUSE_SECRET_KEY,
            public_key=config.LANGFUSE_PUBLIC_KEY,
            host=config.LANGFUSE_HOST,
            debug=False  # Disable debug logging
        )
    
    def trace_recipe_generation(
        self, 
        ingredients: List[str], 
        result: Dict[str, Any], 
        session_id: str = None
    ) -> str:
        """
        Trace a recipe generation request in Langfuse
        Returns the trace ID
        """
        
        try:
            # Use the actual messages from the API call if available, otherwise fallback
            input_messages = result.get("actual_messages", [
                {
                    "role": "system", 
                    "content": config.RECIPE_SYSTEM_PROMPT
                }, 
                {
                    "role": "user", 
                    "content": f"Create a recipe using these ingredients: {', '.join(ingredients)}"
                }
            ])
            
            if "error" in result:
                # Log error case
                generation = self.langfuse.start_generation(
                    name="recipe_llm_call",
                    model=config.MODEL_NAME,
                    input=input_messages,
                    output={"error": result["error"]},
                    level="ERROR",
                    metadata={
                        "ingredients": ingredients,
                        "error": True,
                        **result.get("metadata", {})
                    }
                )
                
                # Set session ID at trace level if provided
                if session_id:
                    generation.update_trace(session_id=session_id)
            else:
                # Log successful generation
                metadata = result.get("metadata", {})
                
                generation = self.langfuse.start_generation(
                    name="recipe_llm_call",
                    model=metadata.get("model", config.MODEL_NAME),
                    input=input_messages,
                    output=result["raw_response"],
                    usage_details={
                        "prompt_tokens": metadata.get("prompt_tokens", 0),
                        "completion_tokens": metadata.get("completion_tokens", 0),
                        "total_tokens": metadata.get("total_tokens", 0)
                    },
                    cost_details={
                        "total_cost": metadata.get("cost", 0)
                    },
                    metadata={
                        "ingredients": ingredients,
                        "dietary_requirements": metadata.get("dietary_requirements"),
                        "latency": metadata.get("latency", 0),
                        "recipe_name": result["recipe"].get("name", ""),
                        "servings": result["recipe"].get("servings", 0),
                        "cooking_time": result["recipe"].get("cooking_time", "")
                    }
                )
                
                # Set session ID at trace level if provided
                if session_id:
                    generation.update_trace(session_id=session_id)
                
                # Add custom score for recipe quality - skip for now due to API complexity
                # self.langfuse.create_score(
                #     name="recipe_completeness",
                #     value=1.0 if all(key in result["recipe"] for key in ["name", "ingredients", "instructions"]) else 0.5
                # )
            
            # End the generation
            generation.end()
            
            # Get trace ID from the generation
            trace_id = generation.trace_id if hasattr(generation, 'trace_id') else str(uuid.uuid4())
            
            # Flush to ensure data is sent
            self.langfuse.flush()
            
        except Exception as e:
            print(f"⚠ Langfuse tracing error: {e}")
            # Create a fallback trace ID
            trace_id = str(uuid.uuid4())
        
        return trace_id
    
    def create_session(self, user_id: str = None) -> str:
        """Create a new session for grouping related recipe generations"""
        # Generate a session ID since Langfuse doesn't have a direct session creation method
        session_id = f"recipe_session_{uuid.uuid4()}"
        return session_id