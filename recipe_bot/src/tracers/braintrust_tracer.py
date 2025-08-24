import braintrust
from typing import Dict, Any, List
import config
import uuid
import time

class BraintrustTracer:
    def __init__(self, project_name: str = "recipe-bot"):
        self.project_name = project_name
        self.experiment = None
        
    def start_experiment(self, experiment_name: str = None):
        """Start a new Braintrust experiment"""
        if not experiment_name:
            experiment_name = f"recipe-generation-{int(time.time())}"
            
        self.experiment = braintrust.init(
            project=self.project_name,
            experiment=experiment_name,
            api_key=config.BRAINTRUST_API_KEY
        )
        return self.experiment
    
    def trace_recipe_generation(
        self,
        ingredients: List[str],
        result: Dict[str, Any],
        experiment_name: str = None
    ) -> str:
        """
        Trace a recipe generation in Braintrust
        Returns the log ID
        """
        
        if not self.experiment:
            self.start_experiment(experiment_name)
        
        # Prepare the input data
        input_data = {
            "ingredients": ingredients,
            "model": config.MODEL_NAME,
            "temperature": config.TEMPERATURE,
            "max_tokens": config.MAX_TOKENS
        }
        
        if "error" in result:
            # Log error case
            log_id = str(uuid.uuid4())
            self.experiment.log(
                input=input_data,
                output={"error": result["error"]},
                expected=None,  # No expected output for generative task
                scores={
                    "success": 0.0
                },
                metadata={
                    "error": True,
                    "ingredients_count": len(ingredients),
                    **result.get("metadata", {})
                },
                id=log_id
            )
        else:
            # Log successful generation
            metadata = result.get("metadata", {})
            recipe = result["recipe"]
            
            log_id = str(uuid.uuid4())
            self.experiment.log(
                input=input_data,
                output={
                    "recipe": recipe,
                    "raw_response": result["raw_response"]
                },
                expected=None,  # No expected output for generative task
                scores={
                    "success": 1.0,
                    "ingredients_used": self._calculate_ingredients_usage(ingredients, recipe.get("ingredients", [])),
                    "recipe_completeness": self._calculate_recipe_completeness(recipe)
                },
                metadata={
                    "model": metadata.get("model", config.MODEL_NAME),
                    "prompt_tokens": metadata.get("prompt_tokens", 0),
                    "completion_tokens": metadata.get("completion_tokens", 0),
                    "total_tokens": metadata.get("total_tokens", 0),
                    "ingredients_count": len(ingredients),
                    "recipe_name": recipe.get("name", ""),
                    "servings": recipe.get("servings", 0),
                    "cooking_time": recipe.get("cooking_time", ""),
                    "instructions_count": len(recipe.get("instructions", []))
                },
                id=log_id
            )
        
        return log_id
    
    def _calculate_ingredients_usage(self, input_ingredients: List[str], recipe_ingredients: List[str]) -> float:
        """Calculate what percentage of input ingredients were used in the recipe"""
        if not input_ingredients:
            return 0.0
            
        used_count = 0
        input_lower = [ing.lower() for ing in input_ingredients]
        recipe_text = " ".join(recipe_ingredients).lower()
        
        for ingredient in input_lower:
            if ingredient in recipe_text:
                used_count += 1
                
        return used_count / len(input_ingredients)
    
    def _calculate_recipe_completeness(self, recipe: Dict[str, Any]) -> float:
        """Calculate completeness score based on required fields"""
        required_fields = ["name", "ingredients", "instructions", "cooking_time", "servings"]
        present_fields = sum(1 for field in required_fields if recipe.get(field))
        
        # Additional points for non-empty lists
        if recipe.get("ingredients") and len(recipe["ingredients"]) > 0:
            present_fields += 0.5
        if recipe.get("instructions") and len(recipe["instructions"]) > 0:
            present_fields += 0.5
            
        return min(present_fields / len(required_fields), 1.0)
    
    def finish_experiment(self):
        """Finish the current experiment"""
        if self.experiment:
            self.experiment.finish()
            self.experiment = None
    
    def get_experiment_url(self) -> str:
        """Get the URL to view the experiment in Braintrust"""
        if self.experiment:
            return f"https://www.braintrust.dev/app/{self.project_name}/experiments/{self.experiment.id}"
        return None