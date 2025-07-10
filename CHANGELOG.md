# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https.md://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https.md://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Dynamic Tool Loading System**: Implemented comprehensive dynamic tool loading with `ToolManager` class supporting reflection-based tool discovery.
- **Example Academic Search Tool**: Created `examples/example_tool.py` with sample `academic_search` function demonstrating tool integration.
- **Enhanced Tool Configuration**: Added `py_plugin` field to tool configurations for specifying Python modules and functions.
- **LangGraph Agent**: Implemented `GraphAgent` using `LangGraph` for a more robust and extensible agent architecture.
- **Interactive Chat for GraphAgent**: Created a new entry point in `__main__.py` for interactive testing of the `GraphAgent`.
- **Configuration-driven Base URL**: The API `base_url` is now loaded from `api_keys.yaml`, removing hardcoded values.
- **Unit Testing Framework**: Established a `unittest`-based testing framework in `tests/test_chat_agent.py`.
- **Logging System**: Integrated a centralized logging system to replace print statements for better debugging and output management.

### Changed
- **Tool Configuration Architecture**: Redesigned tool loading to use file paths instead of embedded configuration objects, preventing "File name too long" errors.
- **Message Processing Logic**: Modified `GraphAgent` to handle DeepSeek API message format requirements by avoiding `ToolMessage` objects.
- **Graph Workflow**: Updated LangGraph workflow to end directly after tool execution, preventing API compatibility issues.
- **Refactored `ChatAgent`**: Updated `_init_chat_model` to use the `base_url` from `api_keys.yaml`.
- **Refactored `SimpleChatAgent`**: Updated to fetch and display the `base_url`.
- **Cleaned Codebase**: Removed emojis and unnecessary print statements across the project for cleaner output.

### Fixed
- **Critical "File name too long" Error**: Fixed configuration loading bug where `ToolConfig` objects were incorrectly used as file paths.
- **Tool Plugin Format Error**: Corrected `py_plugin` field format from `module` to `module:function` in tool configurations.
- **LangChain Tool Creation Error**: Fixed `tool()` decorator usage by removing unsupported `name` parameter.
- **DeepSeek API Message Format Error**: Resolved "Messages with role 'tool' must be a response to a preceding message with 'tool_calls'" error.
- **Missing Dependencies**: Added `pydantic>=2.0.0` to project dependencies.
- **Model Not Found Error**: Corrected the model name in `example.yaml` from `deepseek-r1` to the supported `deepseek-chat`, resolving the `openai.BadRequestError`.
- **Linter Errors**: Fixed all major linter errors in `tests/test_chat_agent.py`, converting it from `pytest` to `unittest`.
- **Module Import Errors**: Resolved `ModuleNotFoundError` during testing by mocking dependencies and setting `PYTHONPATH`. 