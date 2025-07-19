# Google ADK Examples

This repository collects several standalone examples that showcase features of the [Google Agent Development Kit](https://github.com/google-gemini/agent-development-kit). Each folder contains a minimal agent that can be run independently once your environment is configured.

## Examples

| Folder | Description |
|-------|-------------|
| `adk-caching/` | Demonstrates model-level caching by subclassing `BaseLlm` to store and reuse responses. Includes a short script that shows cache misses and hits. |
| `adk-delegation/` | Shows how a root agent can delegate questions to specialist agents (math and chemistry) based on the user's request. |
| `adk-dynamic-routing/` | Uses a custom LLM class to route requests to either `gemini-2.5-flash` or `gemini-2.5-pro` depending on prompt length. |
| `adk-retries/` | Adds retry logic around model calls. The `RetryableLlm` attempts a request multiple times and logs failures. |
| `adk-feedback-analysis-example/` | A small application that logs sessions to SQLite, runs post hoc analysis, and prints aggregate reports. |

## Running an Example

1. Create a `.env` file or export the following variables so the Gemini client can authenticate:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="your-location"
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

2. Change into the example directory and run `python main.py` to see it in action.

Each folder's code is intentionally short and commented to illustrate a single concept in ADK. Explore them to learn how agents, models, and tools fit together.

