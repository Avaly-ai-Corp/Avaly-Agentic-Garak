# textattack.dockerfile
# ---------------------
# This Dockerfile sets up the environment for running the multi_tool_agent with all required dependencies for LLM vulnerability scanning.

# Use the official Python 3.10 slim image as the base
FROM python:3.10-slim

# Set TensorFlow log level to suppress warnings (3 = FATAL)
ENV TF_CPP_MIN_LOG_LEVEL=3

# Configure PyTorch CUDA allocation for expandable segments
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Set TensorFlow GPU allocator to use cuda_malloc_async
ENV TF_GPU_ALLOCATOR=cuda_malloc_async

# Set Hugging Face token (empty by default, can be overridden at runtime)
ENV HF_TOKEN=""

# Set the timezone to America/Toronto
ENV TZ=America/Toronto

# Install timezone data
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# Install required Python packages for LLM scanning and model management
RUN pip install --no-cache-dir \
    garak \
    google-adk \
    litellm \
    hf_xet \
    huggingface_hub \
    grpcio-status==1.48.2 

# Copy the multi_tool_agent source code into the container workspace
COPY ./multi_tool_agent /workspace/multi_tool_agent

# Expose the port that the ADK API server will run on
EXPOSE 8000

# Set the working directory and default entrypoint for the container
WORKDIR /workspace
ENTRYPOINT ["adk", "api_server", "--host", "0.0.0.0", "--port", "8000"]

# Example usage:
# docker run --rm --gpus all -p 8000:8000 [image-name]