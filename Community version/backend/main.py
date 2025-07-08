"""
main.py
-------
This module implements the FastAPI backend for the LLM vulnerability scanning system. It provides endpoints for session management, report retrieval, running scans, and tool calls, and acts as a bridge between the frontend and the agent container.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import re


app = FastAPI()

ADK_API_URL = "http://agent:8000"

# Allow CORS from any origin (for development and integration with frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
async def get_status():
    """
    Health check endpoint to verify the backend is running.
    Returns:
        dict: A simple status message.
    """
    return {"message": "OK"}


@app.post("/api/create_session")
async def create_session():
    """
    Creates a new session by forwarding the request to the agent's session endpoint.
    Returns:
        dict: The response from the agent API.
    Raises:
        HTTPException: If the agent is unreachable or returns an error.
    """
    # Use AsyncClient so we don't block the event loop
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(
                f"{ADK_API_URL}/apps/multi_tool_agent/users/username/sessions",
            )
        except httpx.RequestError as exc:
            # If ADK server is down or unreachable, return a 502 so that React sees CORS headers
            raise HTTPException(status_code=502, detail=f"ADK request failed: {exc}")

    # Forward ADK's JSON response
    return resp.json()


@app.get("/api/get_reports")
async def get_reports():
    """
    Retrieves all attack reports from the /attack_data Docker volume.
    Returns:
        list: A list of report data loaded from JSON files.
    """
    reports = []
    for file in os.listdir("/attack_data"):
        print(file)
        if file.endswith(".json") and "REPORT" in file:
            with open(os.path.join("/attack_data", file), "r") as f:
                data = json.load(f)
                reports.append(data)
    return reports


@app.post("/api/run")
async def run(payload: dict):
    """
    Forwards a scan request to the agent's /run endpoint and processes the response.
    Args:
        payload (dict): The request payload to forward.
    Returns:
        dict: The response from the agent, possibly including a report file path.
    Raises:
        HTTPException: If the agent is unreachable or returns an error.
    """
    adk_url = f"{ADK_API_URL}/run"

    async with httpx.AsyncClient(timeout=5000.0) as client:
        try:
            # Forward exactly what we received to ADK's /run
            print("\n\npayload\n\n", payload)
            resp = await client.post(f"{ADK_API_URL}/run", json=payload)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502, detail=f"Failed to reach ADK at {adk_url}: {exc}"
            )

    # If ADK returned a non‐200, bubble that back:
    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"ADK returned {resp.status_code}: {resp.text}",
        )

    json_resp = resp.json()
    # We need to check if the return from ADK contains a report file indicator.    
    # 1) if the JSON has an explicit report_file key, return it
    if isinstance(json_resp, dict) and json_resp.get("report_file"):
        return json_resp

    # 2) otherwise fall back to regex on the raw body
    text = resp.text
    match = re.search(
        r'(/attack_data/REPORT_[\d\-T:]+_attack_summary\.json)',
        text
    )
    if match:
        return {"report_file": match.group(1)}

    # 3) give up and return whatever JSON we got (or None)
    return json_resp

@app.get("/api/attack_data/{filename}")
async def get_attack_data(filename: str):
    """
    Retrieves a single attack report (JSON) from the /attack_data Docker volume.
    Args:
        filename (str): The name of the report file to retrieve.
    Returns:
        dict: The report data loaded from the file.
    Raises:
        HTTPException: If the file does not exist.
    """
    if os.path.exists(os.path.join("/attack_data", filename)):
        with open(os.path.join("/attack_data", filename), "r") as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

@app.post("/api/tool_call")
async def tool_call(payload: dict):
    """
    Receives a tool/function call request from the frontend, executes the tool, and returns the result.
    Example payload: {"name": "list_probes", "arguments": {}}
    Args:
        payload (dict): The tool call request from the frontend.
    Returns:
        dict: The result of the tool execution or an error message.
    """
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agent', 'multi_tool_agent')))
    from GarakWrapper import run_scan, list_probes

    tool_name = payload.get("name")
    arguments = payload.get("arguments", {})

    if tool_name == "list_probes":
        return list_probes()
    elif tool_name == "run_scan":
        model_name = arguments.get("model_name")
        probes = arguments.get("probes")
        report_path = run_scan(model_name, probes)
        return {"report_file": str(report_path)}
    else:
        return {"error": f"Unknown tool: {tool_name}"}

