#!/usr/bin/env python3
import sys
import os
import json
from typing import List
import argparse

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recipe_generator import RecipeGenerator
from src.tracers.langfuse_tracer import LangfuseTracer
# from src.tracers.braintrust_tracer import BraintrustTracer  # Disabled

class RecipeBotCLI:
    def __init__(self):
        self.generator = RecipeGenerator()
        self.langfuse_tracer = None
        self.braintrust_tracer = None
        
        # Initialize tracers if API keys are available
        try:
            import config
            if config.LANGFUSE_SECRET_KEY and config.LANGFUSE_PUBLIC_KEY:
                self.langfuse_tracer = LangfuseTracer()
                print("✓ Langfuse tracing enabled")
            else:
                print("⚠ Langfuse tracing disabled (missing API keys)")
                
            # Braintrust tracing disabled for now
            # if config.BRAINTRUST_API_KEY:
            #     self.braintrust_tracer = BraintrustTracer()
            #     print("✓ Braintrust tracing enabled")
            # else:
            print("⚠ Braintrust tracing disabled")
        except Exception as e:
            print(f"⚠ Error initializing tracers: {e}")
    
    def parse_ingredients(self, ingredients_input: str) -> List[str]:
        """Parse ingredients from user input"""
        # Split by comma and clean up
        ingredients = [ing.strip() for ing in ingredients_input.split(',')]
        # Remove empty strings
        ingredients = [ing for ing in ingredients if ing]
        return ingredients
    
    def display_recipe(self, recipe_data: dict):
        """Display the recipe in a nice format"""
        recipe = recipe_data["recipe"]
        metadata = recipe_data.get("metadata", {})
        trace_info = recipe_data.get("trace_info", {})
        
        print("\n" + "="*60)
        print(f"🍳 {recipe['name']}")
        print("="*60)
        
        print(f"\n👥 Servings: {recipe['servings']}")
        print(f"⏱️  Cooking Time: {recipe['cooking_time']}")
        
        print(f"\n📋 Ingredients:")
        for i, ingredient in enumerate(recipe['ingredients'], 1):
            print(f"  {i}. {ingredient}")
        
        print(f"\n👨‍🍳 Instructions:")
        for i, instruction in enumerate(recipe['instructions'], 1):
            print(f"  {i}. {instruction}")
        
        print(f"\n📊 Generation Stats:")
        print(f"  • Model: {metadata.get('model', 'N/A')}")
        print(f"  • Tokens: {metadata.get('total_tokens', 'N/A')}")
        print(f"  • Latency: {metadata.get('latency', 0):.2f}s")
        print(f"  • Cost: ${metadata.get('cost', 0):.4f}")
        
        # Display trace information if available
        if trace_info:
            print(f"\n📊 Langfuse Tracing:")
            print(f"  • Method: {trace_info.get('tracing_method', 'N/A')}")
            if trace_info.get('trace_id'):
                print(f"  • Trace ID: {trace_info['trace_id']}")
            if trace_info.get('observation_id'):
                print(f"  • Observation ID: {trace_info['observation_id']}")
            if trace_info.get('error'):
                print(f"  • Error: {trace_info['error']}")
        
        print("="*60)
    
    def run_interactive(self):
        """Run in interactive mode"""
        print("🤖 Welcome to Recipe Bot!")
        print("Enter ingredients separated by commas, or 'quit' to exit")
        print("Example: chicken, rice, bell peppers, soy sauce")
        print()
        
        # Session ID creation disabled - using @observe() decorator instead
        # session_id = None
        # if self.langfuse_tracer:
        #     session_id = self.langfuse_tracer.create_session()
        
        # Braintrust disabled
        # if self.braintrust_tracer:
        #     self.braintrust_tracer.start_experiment("interactive-session")
        
        while True:
            try:
                ingredients_input = input("\n🥘 Enter ingredients: ").strip()
                
                if ingredients_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thanks for using Recipe Bot!")
                    break
                
                if not ingredients_input:
                    print("Please enter some ingredients!")
                    continue
                
                ingredients = self.parse_ingredients(ingredients_input)
                if not ingredients:
                    print("Please enter valid ingredients separated by commas!")
                    continue
                
                # Ask for dietary requirements
                dietary_input = input("🥗 Any dietary requirements or allergies? (press Enter to skip): ").strip()
                dietary_requirements = None
                if dietary_input:
                    dietary_requirements = self.parse_ingredients(dietary_input)  # Reuse same parsing logic
                    print(f"📋 Dietary considerations: {', '.join(dietary_requirements)}")
                
                print(f"\n🔄 Generating recipe for: {', '.join(ingredients)}...")
                
                # Generate recipe
                result = self.generator.generate_recipe(ingredients, dietary_requirements)
                
                if "error" in result:
                    print(f"❌ Error generating recipe: {result['error']}")
                else:
                    self.display_recipe(result)
                
                # Manual tracing disabled - using @observe() decorator instead
                # try:
                #     if self.langfuse_tracer:
                #         trace_id = self.langfuse_tracer.trace_recipe_generation(
                #             ingredients, result, session_id
                #         )
                #         print(f"📊 Langfuse trace ID: {trace_id}")
                # except Exception as e:
                #     print(f"⚠ Langfuse tracing failed: {e}")
                
                # Braintrust tracing disabled
                # try:
                #     if self.braintrust_tracer:
                #         log_id = self.braintrust_tracer.trace_recipe_generation(ingredients, result)
                #         print(f"📊 Braintrust log ID: {log_id}")
                # except Exception as e:
                #     print(f"⚠ Braintrust tracing failed: {e}")
                
            except KeyboardInterrupt:
                print("\n👋 Thanks for using Recipe Bot!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
        
        # Clean up - Braintrust disabled
        # if self.braintrust_tracer:
        #     self.braintrust_tracer.finish_experiment()
        #     url = self.braintrust_tracer.get_experiment_url()
        #     if url:
        #         print(f"📊 View Braintrust experiment: {url}")
    
    def run_single(self, ingredients: List[str], dietary_requirements: List[str] = None):
        """Run single recipe generation"""
        if dietary_requirements:
            print(f"📋 Dietary considerations: {', '.join(dietary_requirements)}")
        print(f"🔄 Generating recipe for: {', '.join(ingredients)}...")
        
        # Braintrust disabled
        # if self.braintrust_tracer:
        #     self.braintrust_tracer.start_experiment("single-generation")
        
        # Generate recipe
        result = self.generator.generate_recipe(ingredients, dietary_requirements)
        
        if "error" in result:
            print(f"❌ Error generating recipe: {result['error']}")
            return
        
        self.display_recipe(result)
        
        # Manual tracing disabled - using @observe() decorator instead
        # try:
        #     if self.langfuse_tracer:
        #         trace_id = self.langfuse_tracer.trace_recipe_generation(ingredients, result)
        #         print(f"📊 Langfuse trace ID: {trace_id}")
        # except Exception as e:
        #     print(f"⚠ Langfuse tracing failed: {e}")
        
        # Braintrust tracing disabled
        # try:
        #     if self.braintrust_tracer:
        #         log_id = self.braintrust_tracer.trace_recipe_generation(ingredients, result)
        #         print(f"📊 Braintrust log ID: {log_id}")
        #         self.braintrust_tracer.finish_experiment()
        #         url = self.braintrust_tracer.get_experiment_url()
        #         if url:
        #             print(f"📊 View Braintrust experiment: {url}")
        # except Exception as e:
        #     print(f"⚠ Braintrust tracing failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Recipe Bot - Generate recipes from ingredients")
    parser.add_argument(
        'ingredients', 
        nargs='*', 
        help='Ingredients separated by spaces (use quotes for multi-word ingredients)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--dietary', '-d',
        nargs='*',
        help='Dietary requirements or allergies (e.g., --dietary vegetarian "no nuts" gluten-free)'
    )
    
    args = parser.parse_args()
    
    cli = RecipeBotCLI()
    
    if args.interactive or not args.ingredients:
        cli.run_interactive()
    else:
        cli.run_single(args.ingredients, args.dietary)

if __name__ == "__main__":
    main()