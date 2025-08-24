# Recipe Bot 🤖🍳

A simple recipe generator app that uses GPT-4o-mini to create recipes from available ingredients, with comprehensive tracing using Langfuse and Braintrust for observability analysis.

## Features

- 🥘 Generate recipes from available ingredients
- 🛡️ **Dietary requirements & allergy safety** - Supports any dietary restrictions
- 📊 Observability tracing with Langfuse
- 💰 Cost and token tracking
- ⚡ Latency monitoring
- 🎯 Recipe quality scoring
- 💻 Interactive CLI interface

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Required:
   - `OPENAI_API_KEY` - Your OpenAI API key
   
   Optional (for tracing):
   - `LANGFUSE_SECRET_KEY` - Your Langfuse secret key
   - `LANGFUSE_PUBLIC_KEY` - Your Langfuse public key

## Usage

### Interactive Mode
```bash
python main.py --interactive
```
or just:
```bash
python main.py
```

### Single Recipe Generation
```bash
python main.py chicken rice "bell peppers" "soy sauce"

# With dietary requirements
python main.py chicken rice vegetables --dietary gluten-free "no dairy" vegetarian
```

### Example Session
```
🤖 Welcome to Recipe Bot!
Enter ingredients separated by commas, or 'quit' to exit
Example: chicken, rice, bell peppers, soy sauce

🥘 Enter ingredients: chicken, rice, bell peppers, soy sauce
🥗 Any dietary requirements or allergies? (press Enter to skip): gluten-free, no dairy
📋 Dietary considerations: gluten-free, no dairy

🔄 Generating recipe for: chicken, rice, bell peppers, soy sauce...

============================================================
🍳 Chicken Fried Rice with Bell Peppers
============================================================

👥 Servings: 4
⏱️  Cooking Time: 20 minutes

📋 Ingredients:
  1. 2 cups cooked rice (preferably day-old)
  2. 1 lb chicken breast, diced
  3. 2 bell peppers, sliced
  4. 3 tablespoons soy sauce
  5. 2 tablespoons vegetable oil
  6. 2 eggs, beaten
  7. 2 green onions, chopped
  8. Salt and pepper to taste

👨‍🍳 Instructions:
  1. Heat 1 tablespoon oil in a large wok or skillet over high heat
  2. Add diced chicken and cook until golden brown, about 5-7 minutes
  3. Push chicken to one side, add beaten eggs and scramble
  4. Add bell peppers and stir-fry for 2-3 minutes
  5. Add rice and soy sauce, stir-fry for 3-4 minutes
  6. Season with salt, pepper, and garnish with green onions

📊 Generation Stats:
  • Model: gpt-4o-mini
  • Tokens: 285
  • Latency: 2.34s
  • Cost: $0.0023
============================================================
```

## Project Structure

```
recipe_bot/
├── main.py                     # Main entry point
├── config.py                   # Configuration and API keys
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
└── src/
    ├── recipe_generator.py    # Core LLM recipe generation logic
    ├── interface.py           # CLI interface
    └── tracers/
        ├── langfuse_tracer.py # Langfuse integration
        └── braintrust_tracer.py # Braintrust integration
```

## Observability

### Langfuse Tracing
- Tracks individual recipe generation sessions
- Monitors token usage, costs, and latency
- Provides recipe quality scoring
- Groups related requests in sessions

## Metrics Tracked

- **Input/Output Tokens**: For cost optimization
- **Latency**: Response time monitoring
- **Cost**: Per-request cost tracking
- **Recipe Quality**: Completeness score based on required fields
- **Success Rate**: Error rate monitoring

## API Key Setup

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env` as `OPENAI_API_KEY`

### Langfuse
1. Sign up at https://langfuse.com
2. Create a project
3. Get your keys from project settings
4. Add to `.env` as `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`


## Development

The app is designed for easy extension:

- **Add new tracers**: Implement in `src/tracers/`
- **Enhance prompts**: Modify `recipe_generator.py`
- **Add web interface**: Extend `interface.py` with Flask/FastAPI
- **Improve scoring**: Update quality metrics in tracers