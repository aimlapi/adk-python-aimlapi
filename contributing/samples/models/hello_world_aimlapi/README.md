# Using aimlapi.com Models with ADK and LiteLLM

This example demonstrates how to use models served by
[aimlapi.com](https://aimlapi.com) with ADK through LiteLLM integration.

aimlapi.com is an OpenAI-compatible aggregator that serves models from several
vendors behind one key. For comprehensive information about using it with
LiteLLM, refer to the
[official LiteLLM documentation](https://docs.litellm.ai/docs/providers/aiml).

## Setup

### 1. Get an aimlapi.com API Key

Use the following procedure to get an aimlapi.com API key.

1. Sign up at [aimlapi.com](https://aimlapi.com)
1. Navigate to the API Keys section and generate a key
1. Copy your API key

### 2. Install LiteLLM

Install LiteLLM by running the following code.

```bash
pip install litellm
```

## Using aimlapi.com Models in ADK

### Environment Variables

Set the required environment variables:

```bash
export AIML_API_KEY="your-aimlapi-key"
export AIML_API_BASE="https://api.aimlapi.com/v1"  # Optional
```

`AIML_API_KEY` is the name LiteLLM reads; ADK passes it through untouched.

### Code Examples

#### Basic Agent Creation

```python
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

# Create agent with an aimlapi.com model
agent = Agent(
    model=LiteLlm(model="aiml/openai/gpt-4o-mini"),
    name="aimlapi_agent",
    instruction="You are a helpful assistant.",
    description="Agent using a model served by aimlapi.com",
)
```

A plain model string works too, because `LLMRegistry` hands any `provider/model`
name LiteLLM knows about to `LiteLlm`:

```python
agent = Agent(model="aiml/openai/gpt-4o-mini", name="aimlapi_agent")
```

#### Available Models

Use the `aiml/` prefix in front of the catalog id. The catalog id keeps its own
slash — LiteLLM splits the provider off the *first* one only, so
`aiml/openai/gpt-4o-mini` reaches the API as `openai/gpt-4o-mini`.

```python
# Examples of available models
models = [
    "aiml/openai/gpt-4o-mini",
    "aiml/openai/gpt-5-5",
    "aiml/anthropic/claude-sonnet-4.5",
    "aiml/google/gemini-2.5-flash",
    # ... and many more
]
```

The full catalog is `GET https://api.aimlapi.com/v1/models`, whose chat entries
are the ones with `"type": "openai/chat-completions"`. An id is valid if it
appears either as an `id` or in another entry's `aliases`.

## Integration Details

ADK uses LiteLLM as a wrapper to access aimlapi.com models. The integration:

1. **Model Format**: Uses `aiml/<vendor>/<model-name>` format
1. **Authentication**: Requires `AIML_API_KEY` environment variable
1. **Base URL**: Optional `AIML_API_BASE`, defaulting to
   `https://api.aimlapi.com/v1`
1. **Compatibility**: Works with all ADK features (tools, sessions, etc.)
1. **Supported Endpoints**: `/chat/completions`. LiteLLM's `aiml` provider also
   carries image generation; it has no embeddings route, so
   `aiml/`-prefixed names are for chat models only.

## Notes

- **Do not validate a key by fetching the model catalog.**
  `GET /v1/models` answers `200` with no key or a wrong one; only an actual
  completion call returns `401`.
- **Catalog membership is not proof a model serves.** A few published ids
  return `404` on a real call, and a few working ids are missing from the
  catalog. Call an id once before depending on it.
- **`max_tokens` does not bound reasoning tokens on every model**, and some
  models report `completion_tokens` that exclude reasoning tokens, so a token
  count read back from a response can under-report the billed total.
