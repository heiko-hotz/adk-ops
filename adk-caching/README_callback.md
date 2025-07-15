# Model-Level Caching Implementation

This implementation demonstrates how to implement caching at the model level using ADK's `BaseLlm` class instead of using tool callbacks.

## Changes Made

### From Tool Callbacks to Model Callbacks

The original implementation in `caching_agent_callback/agent.py` used tool callbacks (`before_tool_callback` and `after_tool_callback`) to implement caching. However, since there were no tools defined in the agent, this approach was not effective.

### New Implementation

The updated implementation creates a custom `CachingLlm` class that inherits from `BaseLlm` and implements caching at the model request/response level.

#### Key Changes:

1. **Removed tool callback functions:**
   - `before_tool_cache_check`
   - `after_tool_cache_populate`
   - `create_cache_key`

2. **Added model-level caching:**
   - `CachingLlm` class that inherits from `BaseLlm`
   - `get_request_hash` function that creates cache keys from user messages
   - `generate_content_async` method that implements the caching logic

3. **Cache Management:**
   - Cache keys are generated from the last user message in the request
   - Cache hits return cached responses immediately
   - Cache misses call the underlying model and cache the response

### How It Works

1. **Cache Key Generation**: The `get_request_hash` function creates an MD5 hash of the last user message in the request.

2. **Cache Check**: Before making a model call, the `CachingLlm` checks if a response for the same user message already exists in the cache.

3. **Cache Hit**: If found, it returns the cached response immediately without calling the model.

4. **Cache Miss**: If not found, it makes the actual model call, caches the response, and returns it.

## Usage

### Running the Test

```bash
python main_callback.py
```

### Expected Output

The test will demonstrate:
- First call: Cache miss (model is called)
- Second call with same text: Cache hit (cached response returned)
- Third call with different text: Cache miss (model is called)
- Fourth call repeating first question: Cache hit (cached response returned)

### Example Output

```
--- Caching Agent Test (Model-Level Caching) ---

--- First call (cache miss) ---
You > What is the exact speed of light in a vacuum?

❌ Cache MISS. Calling the underlying model: gemini-2.5-flash
📝 Model response cached for future use.
Agent > The speed of light in a vacuum is approximately 299,792,458 meters per second...

--- Second call (cache hit) ---
You > What is the exact speed of light in a vacuum?

✅ Cache HIT. Returning cached response for model request.
Agent > The speed of light in a vacuum is approximately 299,792,458 meters per second...
```

## Benefits of Model-Level Caching

1. **More Appropriate**: Since there are no tools in the agent, model-level caching is more appropriate than tool callbacks.

2. **Efficient**: Avoids unnecessary model calls for repeated questions.

3. **Transparent**: The caching is transparent to the agent's behavior - it still gets the same responses.

4. **Flexible**: Can be easily extended to implement more sophisticated caching strategies (TTL, LRU, etc.).

## Environment Setup

Make sure you have the required environment variables set:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="your-location"
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

Or create a `.env` file with these variables.

## Architecture

```
User Query → CachingLlm → Cache Check → Cache Hit? → Return Cached Response
                     ↓
                 Cache Miss → Call Model → Cache Response → Return Response
```

This implementation provides a clean, efficient way to add caching to model requests without relying on tool callbacks when no tools are present. 