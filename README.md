# Anthropic API Proxy for Gemini & OpenAI Models 🔄

**Use Anthropic clients (like Claude Code) with Gemini or OpenAI backends.** 🤝

A proxy server that lets you use Anthropic clients with Gemini or OpenAI models via LiteLLM. 🌉


![Anthropic API Proxy](pic.png)

## Quick Start ⚡

### Prerequisites

- OpenAI API key 🔑
- Google AI Studio (Gemini) API key (if using Google provider) 🔑
- [uv](https://github.com/astral-sh/uv) installed.

### Setup 🛠️

#### Option 1: Install as a Tool (Recommended) ⚡

Install directly as a `uv` tool for easy command-line access:

```bash
# Install from GitHub
uv tool install git+https://github.com/samhavens/claude-code-proxy.git

# Or install from a local clone
git clone https://github.com/samhavens/claude-code-proxy.git
cd claude-code-proxy
uv tool install .
```

This gives you the `anthropic-proxy` and `claude-proxy` commands globally!

#### Option 2: Manual Setup 🔧

1. **Clone this repository**:
   ```bash
   git clone https://github.com/samhavens/claude-code-proxy.git
   cd claude-code-proxy
   ```

2. **Install uv** (if you haven't already):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   *(`uv` will handle dependencies based on `pyproject.toml` when you run the server)*

3. **Configure Environment Variables**:
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your API keys and model configurations:

   *   `ANTHROPIC_API_KEY`: (Optional) Needed only if proxying *to* Anthropic models.
   *   `OPENAI_API_KEY`: Your OpenAI API key (Required if using the default OpenAI preference or as fallback).
   *   `GEMINI_API_KEY`: Your Google AI Studio (Gemini) API key (Required if PREFERRED_PROVIDER=google).
   *   `PREFERRED_PROVIDER` (Optional): Set to `openai` (default) or `google`. This determines the primary backend for mapping `haiku`/`sonnet`.
   *   `BIG_MODEL` (Optional): The model to map `sonnet` requests to. Defaults to `gpt-4.1` (if `PREFERRED_PROVIDER=openai`) or `gemini-2.5-pro-preview-03-25`.
   *   `SMALL_MODEL` (Optional): The model to map `haiku` requests to. Defaults to `gpt-4.1-mini` (if `PREFERRED_PROVIDER=openai`) or `gemini-2.0-flash`.
   *   `DEFAULT_SYSTEM_MESSAGE` (Optional): A system message that will be appended to any existing system message. Useful for adding proxy-specific instructions or context.

   **Mapping Logic:**
   - If `PREFERRED_PROVIDER=openai` (default), `haiku`/`sonnet` map to `SMALL_MODEL`/`BIG_MODEL` prefixed with `openai/`.
   - If `PREFERRED_PROVIDER=google`, `haiku`/`sonnet` map to `SMALL_MODEL`/`BIG_MODEL` prefixed with `gemini/` *if* those models are in the server's known `GEMINI_MODELS` list (otherwise falls back to OpenAI mapping).

#### Running the Server 🚀

**If you installed as a tool:**
```bash
# Start the server with default settings
anthropic-proxy

# Or with custom options
anthropic-proxy --port 8082 --reload

# See all options
anthropic-proxy --help
```

**If you're using manual setup:**
```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082 --reload
```
*(`--reload` is optional, for development)*

### Using with Claude Code 🎮

1. **Install Claude Code** (if you haven't already):
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Connect to your proxy**:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:8082 claude
   ```

3. **That's it!** Your Claude Code client will now use the configured backend models (defaulting to Gemini) through the proxy. 🎯

### Quick Start Aliases 🚀

For even faster access, add these aliases to your shell config (`.bashrc`, `.zshrc`, etc.):

#### Method 1: Simple Aliases (Fixed Delay)
```bash
# Add to your ~/.zshrc or ~/.bashrc
alias oai-claude='(PREFERRED_PROVIDER=openai anthropic-proxy &) && sleep 2 && ANTHROPIC_BASE_URL=http://localhost:8082 claude'
alias gemini-claude='(PREFERRED_PROVIDER=google anthropic-proxy &) && sleep 2 && ANTHROPIC_BASE_URL=http://localhost:8082 claude'
```

#### Method 2: Smart Aliases (Waits for Server)
```bash
# Add to your ~/.zshrc or ~/.bashrc
alias oai-claude='start-claude --provider openai'
alias gemini-claude='start-claude --provider google'
alias custom-claude='start-claude --provider openai --big-model gpt-4o --small-model gpt-4o-mini'
```

#### Method 3: Direct Commands
```bash
# Start with OpenAI backend (waits for server to be ready)
start-claude --provider openai

# Start with Gemini backend
start-claude --provider google

# Start with custom models
start-claude --provider openai --big-model gpt-4o --small-model gpt-4o-mini

# Start with custom system message
start-claude --provider openai --system-message "You are running through a proxy. Be aware you're using OpenAI models."

# See all options
start-claude --help
```

**Usage:**
```bash
# Any of these work:
oai-claude
gemini-claude
custom-claude
start-claude --provider openai
```

**Note:** Method 2 and 3 use the `start-claude` command which waits for the server to be ready before launching Claude, making it more reliable than fixed delays.

## Model Mapping 🗺️

The proxy automatically maps Claude models to either OpenAI or Gemini models based on the configured model:

| Claude Model | Default Mapping | When BIG_MODEL/SMALL_MODEL is a Gemini model |
|--------------|--------------|---------------------------|
| haiku | openai/gpt-4o-mini | gemini/[model-name] |
| sonnet | openai/gpt-4o | gemini/[model-name] |

### Supported Models

#### OpenAI Models
The following OpenAI models are supported with automatic `openai/` prefix handling:
- o3
- o3-mini
- o1
- o1-mini
- o1-pro
- gpt-4.5-preview
- gpt-4o
- gpt-4o-audio-preview
- chatgpt-4o-latest
- gpt-4o-mini
- gpt-4o-mini-audio-preview
- gpt-4.1
- gpt-4.1-mini

#### Gemini Models
The following Gemini models are supported with automatic `gemini/` prefix handling:
- gemini-2.5-pro-preview-03-25
- gemini-2.0-flash

### Model Prefix Handling
The proxy automatically adds the appropriate prefix to model names:
- OpenAI models get the `openai/` prefix 
- Gemini models get the `gemini/` prefix
- The BIG_MODEL and SMALL_MODEL will get the appropriate prefix based on whether they're in the OpenAI or Gemini model lists

For example:
- `gpt-4o` becomes `openai/gpt-4o`
- `gemini-2.5-pro-preview-03-25` becomes `gemini/gemini-2.5-pro-preview-03-25`
- When BIG_MODEL is set to a Gemini model, Claude Sonnet will map to `gemini/[model-name]`

### Customizing Model Mapping

Control the mapping using environment variables in your `.env` file or directly:

**Example 1: Default (Use OpenAI)**
No changes needed in `.env` beyond API keys, or ensure:
```dotenv
OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-google-key" # Needed if PREFERRED_PROVIDER=google
# PREFERRED_PROVIDER="openai" # Optional, it's the default
# BIG_MODEL="gpt-4.1" # Optional, it's the default
# SMALL_MODEL="gpt-4.1-mini" # Optional, it's the default
```

**Example 2: Prefer Google**
```dotenv
GEMINI_API_KEY="your-google-key"
OPENAI_API_KEY="your-openai-key" # Needed for fallback
PREFERRED_PROVIDER="google"
# BIG_MODEL="gemini-2.5-pro-preview-03-25" # Optional, it's the default for Google pref
# SMALL_MODEL="gemini-2.0-flash" # Optional, it's the default for Google pref
```

**Example 3: Use Specific OpenAI Models**
```dotenv
OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-google-key"
PREFERRED_PROVIDER="openai"
BIG_MODEL="gpt-4o" # Example specific model
SMALL_MODEL="gpt-4o-mini" # Example specific model
```

**Example 4: Add Default System Message**
```dotenv
OPENAI_API_KEY="your-openai-key"
DEFAULT_SYSTEM_MESSAGE="You are running through a proxy that translates between Anthropic and OpenAI APIs. Please be aware that you're actually using OpenAI's models, not Claude."
```

## How It Works 🧩

This proxy works by:

1. **Receiving requests** in Anthropic's API format 📥
2. **Translating** the requests to OpenAI format via LiteLLM 🔄
3. **Sending** the translated request to OpenAI 📤
4. **Converting** the response back to Anthropic format 🔄
5. **Returning** the formatted response to the client ✅

The proxy handles both streaming and non-streaming responses, maintaining compatibility with all Claude clients. 🌊

## Known Issues ⚠️

### Text Spacing Issues
If you notice missing spaces after periods or other spacing issues in the model's output (e.g., "yep—set" instead of "yep—set "), this is likely coming from the **source model's output itself**, not from the proxy processing. The proxy passes text content through directly without modification.

This can happen with:
- **OpenAI models** that have different text formatting than Claude
- **Model-specific quirks** in how certain models handle punctuation and spacing
- **Tokenization differences** between models

**Workaround**: You can add a system message to instruct the model about proper spacing and formatting.

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request. 🎁
