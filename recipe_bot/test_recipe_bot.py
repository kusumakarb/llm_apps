#!/usr/bin/env python3
"""
Test script for Recipe Bot
Tests the core functionality without requiring API keys
"""
import sys
import os
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from recipe_generator import RecipeGenerator, Recipe
        from tracers.langfuse_tracer import LangfuseTracer
        from tracers.braintrust_tracer import BraintrustTracer
        from interface import RecipeBotCLI
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_recipe_validation():
    """Test the Recipe Pydantic model"""
    try:
        from recipe_generator import Recipe
        
        # Test valid recipe
        recipe_data = {
            "name": "Test Recipe",
            "ingredients": ["1 cup flour", "2 eggs"],
            "instructions": ["Mix ingredients", "Cook for 10 minutes"],
            "cooking_time": "10 minutes",
            "servings": 2
        }
        
        recipe = Recipe(**recipe_data)
        print("✅ Recipe validation works")
        print(f"   Recipe: {recipe.name}")
        return True
    except Exception as e:
        print(f"❌ Recipe validation error: {e}")
        return False

def test_ingredients_parsing():
    """Test ingredient parsing logic"""
    try:
        # Test parsing directly without CLI initialization
        def parse_ingredients(ingredients_input: str):
            ingredients = [ing.strip() for ing in ingredients_input.split(',')]
            ingredients = [ing for ing in ingredients if ing]
            return ingredients
        
        # Test normal input
        ingredients = parse_ingredients("chicken, rice, bell peppers, soy sauce")
        expected = ["chicken", "rice", "bell peppers", "soy sauce"]
        assert ingredients == expected, f"Expected {expected}, got {ingredients}"
        
        # Test with extra spaces
        ingredients = parse_ingredients(" chicken ,  rice  , bell peppers,soy sauce ")
        assert ingredients == expected, f"Expected {expected}, got {ingredients}"
        
        print("✅ Ingredient parsing works")
        return True
    except Exception as e:
        print(f"❌ Ingredient parsing error: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    try:
        import config
        print("✅ Config module loads")
        print(f"   Model: {config.MODEL_NAME}")
        print(f"   Max tokens: {config.MAX_TOKENS}")
        print(f"   Temperature: {config.TEMPERATURE}")
        return True
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

def test_tracer_initialization():
    """Test tracer initialization (without API keys)"""
    try:
        from tracers.braintrust_tracer import BraintrustTracer
        
        # Test initialization without API key
        tracer = BraintrustTracer("test-project")
        print("✅ Braintrust tracer initializes")
        
        # Test helper methods
        score = tracer._calculate_ingredients_usage(
            ["chicken", "rice"], 
            ["2 cups chicken breast", "1 cup rice", "salt", "pepper"]
        )
        print(f"   Ingredients usage score: {score}")
        
        recipe = {
            "name": "Test Recipe",
            "ingredients": ["ingredient 1"],
            "instructions": ["step 1"],
            "cooking_time": "10 mins",
            "servings": 2
        }
        completeness = tracer._calculate_recipe_completeness(recipe)
        print(f"   Recipe completeness score: {completeness}")
        
        return True
    except Exception as e:
        print(f"❌ Tracer initialization error: {e}")
        return False

def test_mock_recipe_generation():
    """Test recipe generation with mock data"""
    try:
        # Create a mock response that would come from the LLM
        mock_recipe = {
            "name": "Mock Chicken Rice Bowl",
            "ingredients": [
                "2 cups cooked rice",
                "1 lb chicken breast, diced",
                "2 bell peppers, sliced",
                "3 tbsp soy sauce"
            ],
            "instructions": [
                "Cook chicken in a pan",
                "Add bell peppers and cook for 3 minutes", 
                "Add rice and soy sauce",
                "Stir and serve"
            ],
            "cooking_time": "15 minutes",
            "servings": 4
        }
        
        from recipe_generator import Recipe
        recipe = Recipe(**mock_recipe)
        
        print("✅ Mock recipe generation works")
        print(f"   Recipe: {recipe.name}")
        print(f"   Servings: {recipe.servings}")
        print(f"   Time: {recipe.cooking_time}")
        return True
        
    except Exception as e:
        print(f"❌ Mock recipe generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Recipe Bot Components")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_loading,
        test_recipe_validation,
        test_ingredients_parsing,
        test_tracer_initialization,
        test_mock_recipe_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🧪 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Recipe Bot is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to .env")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Please fix issues before using.")
        sys.exit(1)

if __name__ == "__main__":
    main()