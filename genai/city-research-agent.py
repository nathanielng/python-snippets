#!/usr/bin/env python3

"""
# Agentic Workflow: City Research Dashboard

This example demonstrates an agentic workflow using Strands agents to analyze city data and generate insights.

## Key Features
- Specialized city research agents for transportation, land use, and public health
- Web research capabilities using search APIs
- Data synthesis and dashboard generation
- HTML report creation

## How to Run
1. Navigate to the example directory
2. Run: python research-gent.py
3. Enter city research queries at the prompt

## Example Queries
- "transport New York City"
- "land use Seattle"
- "What are the transportation trends in Chicago?"
- "How is Boston using its public spaces?"

## Workflow Process
1. City Research Agent: Coordinates specialized analysis agents
2. Domain Agents: Gather and analyze transportation, land use, and health data
3. Dashboard Generation: Creates HTML reports with key insights
"""

# Dependencies:
# pip install tavily-python duckduckgo_search

import json
import logging
import os

from strands import Agent, tool
from strands.handlers.callback_handler import PrintingCallbackHandler
from strands.models import BedrockModel
from strands_tools import http_request, file_read, file_write

logging.getLogger("strands").setLevel(logging.INFO)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()],
    level = logging.INFO
)
logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', None)

TAVILY_SYSTEM_PROMPT = """
You are a search assistant with access to the Tavily API.
You can:
1. Search the internet with a query
2. Filter results by relevance and credibility
3. Extract key information from multiple sources

When displaying responses:
- Format data in a clear, structured way
- Highlight important information with bullet points
- Include source URLs and publication dates
- Keep findings under 500 words
- Prioritize recent and authoritative sources
"""

DUCKDUCKGO_SYSTEM_PROMPT = """
You are a search assistant with access to the Duck Duck Go API.
You can:
1. Search the internet with a query
2. Filter results by relevance and credibility
3. Extract key information from multiple sources

When displaying responses:
- Format data in a clear, structured way
- Highlight important information with bullet points
- Include source URLs and publication dates
- Keep findings under 500 words
- Prioritize recent and authoritative sources
"""

RESEARCHER_SYSTEM_PROMPT = """
You are a Researcher Agent that gathers information from the web.
1. Use your research tools (web_search, http_request) to find relevant information
2. Gather comprehensive information from multiple sources
3. Evaluate source credibility and publication dates
4. Include source URLs and publication dates when available
5. Keep findings concise and well-structured, under 500 words
6. Highlight key points with bullet points
7. Note any conflicting information found across sources
8. Flag if insufficient reliable information is found
"""

ANALYSIS_SYSTEM_PROMPT = """
You are an Analyst Agent specialized in analyzing and synthesizing information.
1. Analyze sentiment and emotional tone of content:
   - Identify positive/negative/neutral sentiment
   - Note emotional intensity and bias
   - Flag potentially misleading content
2. Identify key trends and patterns:
   - Extract recurring themes and topics
   - Note emerging or changing trends over time
   - Compare findings across different sources
3. Categorize and structure findings:
   - Group related information into clear categories
   - Highlight connections between topics
   - Identify gaps in available information
4. Evaluate source credibility:
   - Check author expertise and publication reputation
   - Note publication dates and timeliness
   - Flag potential conflicts of interest
5. Synthesize insights:
   - Summarize key takeaways
   - Note areas of consensus and disagreement
   - Suggest areas needing further research
6. Keep analysis clear and concise:
   - Limit findings to 500 words
   - Use bullet points for clarity
   - Include relevant source citations
"""

if TAVILY_API_KEY:
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    SYSTEM_PROMPT = TAVILY_SYSTEM_PROMPT
    logger.info("Tavily API found. Using the Tavily API for search queries")
else:
    from duckduckgo_search import DDGS
    SYSTEM_PROMPT = DUCKDUCKGO_SYSTEM_PROMPT
    logger.info("Tavily API not found. Using the Duck Duck Go API for search queries")

bedrock_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    temperature=0.1,
)


@tool
def web_search(query: str, max_results: int = 3):
    """
    Perform an internet search with the specified query
    
    Args:
        query: A question or search phrase to perform a search with
        max_results: Maximum number of search results to return (default: 3)
        
    Returns:
        Search results from either Tavily API or DuckDuckGo containing relevant web pages
    """
    if TAVILY_API_KEY:
        response = tavily_client.search(
            query,
            max_results = max_results
        )
    else:
        response = DDGS().text(
            query,
            max_results = max_results
        )
    print(json.dumps(response, indent=2, default=str))
    return response


@tool
def transport_agent(query: str):
    """
    Agent that gathers and analyzes transportation information for cities.
    
    Args:
        query: A question or search phrase about city transportation
        
    Returns:
        str: Analysis of transportation data including key insights, trends and sentiment
             from city research dashboard, limited to 400 words
    """
    agent = Agent(
        model=bedrock_model,
        system_prompt=(
            "You are an AI Assistant specialized in analyzing urban transportation systems."
            "Your responsibilities include:"
            "1. Gathering comprehensive data for city transportation dashboards including:"
            "   - Public transit metrics and performance"
            "   - Traffic patterns and congestion analysis"
            "   - Alternative transportation usage (bikes, scooters, etc.)"
            "   - Citizen sentiment and satisfaction levels"
            "2. For research queries: Identify 3-5 key insights with supporting data"
            "3. Evaluate source reliability and credibility"
            "4. Provide actionable recommendations based on findings"
            "5. Keep analysis clear and concise, under 400 words"
        ),
        tools=[ research_workflow_agent ],
        callback_handler=PrintingCallbackHandler()
    )
    response = agent(query)
    return response


@tool
def land_use_agent(query: str):
    """
    Agent that gathers and analyzes land use information for cities.
    
    Args:
        query: A question or search phrase about city land use and zoning
        
    Returns:
        str: Analysis of land use data including key insights, trends and patterns
             from city research dashboard, limited to 400 words
    """
    agent = Agent(
        model=bedrock_model,
        system_prompt=(
            "You are an AI Assistant specialized in analyzing urban land use patterns."
            "Your responsibilities include:"
            "1. Gathering comprehensive data for city land use dashboards including:"
            "   - Zoning regulations and changes"
            "   - Development density and distribution"
            "   - Green space and public land allocation"
            "   - Property usage trends and patterns"
            "2. For research queries: Identify 3-5 key insights with supporting data"
            "3. Evaluate source reliability and credibility"
            "4. Provide actionable recommendations based on findings"
            "5. Keep analysis clear and concise, under 400 words"
        ),
        tools=[ research_workflow_agent ],
        callback_handler=PrintingCallbackHandler()
    )
    response = agent(query)
    return response


@tool
def city_health_agent(query: str):
    """
    Agent that gathers and analyzes public health information for cities.
    
    Args:
        query: A question or search phrase about city health metrics and wellbeing
        
    Returns:
        str: Analysis of city health data including key insights, trends and patterns
             from city research dashboard, limited to 400 words
    """
    agent = Agent(
        model=bedrock_model,
        system_prompt=(
            "You are an AI Assistant specialized in analyzing urban public health patterns."
            "Your responsibilities include:"
            "1. Gathering comprehensive data for city health dashboards including:"
            "   - Public health metrics and outcomes"
            "   - Healthcare access and facilities"
            "   - Environmental health factors"
            "   - Community wellbeing indicators"
            "2. For research queries: Identify 3-5 key insights with supporting data"
            "3. Evaluate source reliability and credibility"
            "4. Provide actionable recommendations based on findings"
            "5. Keep analysis clear and concise, under 400 words"
        ),
        tools=[ research_workflow_agent ],
        callback_handler=PrintingCallbackHandler()
    )
    response = agent(query)
    return response


def research_agent(query: str) -> str:
    agent = Agent(
        model = bedrock_model,
        system_prompt = RESEARCHER_SYSTEM_PROMPT,
        tools = [web_search, http_request],
        callback_handler=PrintingCallbackHandler()
    )
    
    researcher_response = agent(
        f"Research: '{query}'. Use your available tools to gather information from reliable sources. "
        f"Focus on being concise and thorough, but limit web requests to 1-2 sources.",
    )
    
    # Extract only the relevant content from the researcher response
    research_findings = str(researcher_response)
    
    print("Research complete")
    return research_findings


def analysis_agent(query: str, research_findings: str) -> str:
    agent = Agent(
        model=bedrock_model,
        system_prompt=ANALYSIS_SYSTEM_PROMPT,
        callback_handler=PrintingCallbackHandler()
    )

    analyst_response = agent(
        f"Analyze these findings about '{query}':\n\n{research_findings}",
    )
    
    # Extract only the relevant content from the analyst response
    analyst_findings = str(analyst_response)
    
    print("Analyst report complete")
    return analyst_findings


def report_agent(query: str, analyst_findings: str) -> str:
    agent = Agent(
        model=bedrock_model,
        system_prompt=(
            "You are a Writer Agent that creates clear reports. "
            "1. For fact-checks: State whether claims are true or false "
            "2. For research: Present key insights in a logical structure "
            "3. Keep reports under 500 words with brief source mentions"
        ),
        tools = [ file_write ],
        callback_handler=PrintingCallbackHandler()
    )
    
    # Execute the Writer Agent with the analysis (output is shown to user)
    final_report = agent(
        f"Create a text-based report on '{query}' based on this analysis:\n\n{analyst_findings}."
         "In addition, generate a HTML dashboard and save it as a file"
    )
    return final_report


@tool
def research_workflow_agent(user_input):
    """
    Run a three-agent workflow for research and fact-checking with web sources.
    Shows progress logs during execution but presents only the final report to the user.
    
    Args:
        user_input: Research query or claim to verify
        
    Returns:
        str: The final report from the Writer Agent
    """
    
    print(f"\nProcessing: '{user_input}'")
    
    # Step 1: Researcher Agent with enhanced web capabilities
    print("\nStep 1: Researcher Agent gathering web information...")
    research_findings = research_agent(user_input)

    print("Passing research findings to Analyst Agent...\n")
    
    # Step 2: Analyst Agent to verify facts
    print("Step 2: Analyst Agent (analyses sentiment, identifies, trends, categorizes findings)...")
    analyst_findings = analysis_agent(user_input, research_findings)
    
    print("Analysis complete")
    print("Passing analysis to Writer Agent...\n")
    
    # Step 3: Writer Agent to create report
    print("Step 3: Writer Agent creating final report...")
    final_report = writer_agent(user_input, analyst_findings)
        
    print("Report creation complete")
    
    # Return the final report
    return final_report


def city_research_agent(query: str) -> str:
    agent = Agent(
        model=bedrock_model,
        system_prompt=(
            "You are a City Research Agent that can create City Dashboards"
            "with 3 components\n"
            "1. Transport component: with key insights gathered from a transport agent\n"
            "2. Land use component: with key insights gathered from a land use agent\n"
            "3. City health component: with key inisights gathered from a city health agent\n"
            "You can also combine all the 3 components into a single HTML dashboard"
        ),
        tools = [ transport_agent, land_use_agent, city_health_agent, file_read, file_write ],
        callback_handler=PrintingCallbackHandler()
    )
    
    # Execute the Writer Agent with the analysis (output is shown to user)
    response = agent(
        f"Create a City Dashboard based on '{query}'."
         "In addition, generate a HTML dashboard and save it as a file"
    )
    return response


if __name__ == "__main__":
    # Print welcome message
    print("\nCity Research Dashboard\n")
    print("This demo shows Strands agents analyzing city data and trends")
    print("using web search APIs and specialized transportation/land use agents")
    print("to generate insights about urban systems")
    print("\nOptions:")
    print("  'exit' - Exit the program") 
    print("  'transport [city]' - Get transportation analysis for a city")
    print("  'land use [city]' - Get land use analysis for a city")
    print("\nTry research questions about cities and urban systems.")
    print("\nExamples:")
    print("- \"transport New York City\"")
    print("- \"land use Seattle\"") 
    print("- \"What are the transportation trends in Chicago?\"")
    print("- \"How is Boston using its public spaces?\"")
    
    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")

            if user_input.lower() in [ "exit", "quit" ]:
                print("\nGoodbye! 👋")
                break
            
            # Process the input through the workflow of agents
            response = city_research_agent(user_input)
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try a different request.")
