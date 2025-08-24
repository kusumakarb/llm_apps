import time
from typing import List, Dict, Any
from openai import OpenAI
from pydantic import BaseModel, Field
from langfuse import observe, get_client
import config

class Recipe(BaseModel):
    name: str = Field(..., description="Name of the recipe")
    ingredients: List[str] = Field(..., description="List of ingredients with quantities")
    instructions: List[str] = Field(..., description="Step-by-step cooking instructions")
    cooking_time: str = Field(..., description="Estimated cooking time")
    servings: int = Field(..., description="Number of servings")

class RecipeGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    @observe()
    def generate_recipe_with_observe(self, ingredients: List[str], dietary_requirements: List[str] = None, session_id: str = None, langfuse_observation_id=None, langfuse_trace_id=None) -> Dict[str, Any]:
        """Generate recipe using @observe decorator for automatic Langfuse tracing"""
        
        # Set session ID at trace level if provided
        if session_id:
            try:
                langfuse_client = get_client()
                langfuse_client.update_current_trace(session_id=session_id)
            except Exception as e:
                print(f"Warning: Could not set session ID: {e}")
        
        result = self._generate_recipe_core(ingredients, dietary_requirements)
        
        # Try to get trace information using multiple methods
        trace_info = {}
        
        # Method 1: Using special keyword arguments
        if langfuse_observation_id:
            trace_info['observation_id'] = langfuse_observation_id
        if langfuse_trace_id:
            trace_info['trace_id'] = langfuse_trace_id
            
        # Method 2: Using get_client() - try this as fallback
        try:
            if not trace_info.get('trace_id'):
                langfuse_client = get_client()
                current_trace_id = langfuse_client.get_current_trace_id()
                if current_trace_id:
                    trace_info['trace_id'] = current_trace_id
                    
            if not trace_info.get('observation_id'):
                langfuse_client = get_client()
                current_obs_id = langfuse_client.get_current_observation_id()
                if current_obs_id:
                    trace_info['observation_id'] = current_obs_id
        except Exception as e:
            trace_info['error'] = f"Could not retrieve trace info: {str(e)}"
        
        # Add trace information to the result for interface display
        if trace_info:
            trace_info['tracing_method'] = '@observe() decorator'
            if session_id:
                trace_info['session_id'] = session_id
            result['trace_info'] = trace_info
        
        return result
        
    def generate_recipe(self, ingredients: List[str], dietary_requirements: List[str] = None) -> Dict[str, Any]:
        """Public interface - uses @observe decorated version"""
        return self.generate_recipe_with_observe(ingredients, dietary_requirements)
    
    def _generate_recipe_core(self, ingredients: List[str], dietary_requirements: List[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        prompt = self._create_prompt(ingredients, dietary_requirements)
        
        try:
            response = self.client.beta.chat.completions.parse(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": config.RECIPE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
                response_format=Recipe
            )

            print(f"---------------------------------------------------------------------------")
            print(f"Actual LLM Response:\n{response}")
            print(f"---------------------------------------------------------------------------")

            end_time = time.time()
            latency = end_time - start_time
            
            # Get structured response directly - already parsed as Pydantic model
            recipe = response.choices[0].message.parsed
            
            # Store the actual messages for tracing
            actual_messages = [
                {"role": "system", "content": config.RECIPE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            # Return enriched data for tracing
            return {
                "recipe": recipe.model_dump(),
                "metadata": {
                    "model": config.MODEL_NAME,
                    "input_ingredients": ingredients,
                    "dietary_requirements": dietary_requirements,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                    "latency": latency,
                    "cost": self._calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
                },
                "raw_response": response.choices[0].message.content,
                "actual_messages": actual_messages
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "metadata": {
                    "model": config.MODEL_NAME,
                    "input_ingredients": ingredients,
                    "latency": time.time() - start_time
                }
            }
    
    def _create_prompt(self, ingredients: List[str], dietary_requirements: List[str] = None) -> str:
        ingredients_str = ", ".join(ingredients)
        
        # Build dietary requirements section
        dietary_section = ""
        if dietary_requirements:
            dietary_str = ", ".join(dietary_requirements)
            dietary_section = f"""
IMPORTANT DIETARY REQUIREMENTS & ALLERGIES: {dietary_str}
Please ensure this recipe is completely safe for someone with these dietary restrictions/allergies."""

        return f"""Create a recipe using these available ingredients: {ingredients_str}
{dietary_section}

Rules:
- Use as many of the provided ingredients as possible
- Add reasonable quantities for each ingredient
- Include common pantry items (salt, pepper, oil, etc.) if needed
- Provide clear, step-by-step instructions
- Make it practical and delicious
- CRITICAL: If dietary requirements are specified, absolutely avoid any ingredients or suggestions that conflict with those restrictions
- Double-check that all ingredients (including pantry items) are safe for the specified dietary needs
- Aim for 4 servings"""
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # GPT-4o-mini pricing (as of 2024)
        prompt_cost = prompt_tokens * 0.00015 / 1000  # $0.15 per 1K tokens
        completion_cost = completion_tokens * 0.0006 / 1000  # $0.60 per 1K tokens
        return prompt_cost + completion_cost