import requests
import os
from typing import Dict, List, Optional
import logging
from langchain_ollama import OllamaLLM

logger = logging.getLogger(__name__)

def search_web(query: str, num_results: int = 5) -> Dict:
    """
    Perform web search using DuckDuckGo Instant Answer API (free) as fallback,
    or Serper API if available.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        Dictionary with search results and metadata
    """
    
    # Try Serper API first (if API key is available)
    serper_key = os.getenv("SERPER_API_KEY")
    if serper_key:
        try:
            return _search_with_serper(query, num_results, serper_key)
        except Exception as e:
            logger.warning(f"Serper API failed: {e}, falling back to DuckDuckGo")
    
    # Fallback to DuckDuckGo (free but limited)
    try:
        return _search_with_duckduckgo(query)
    except Exception as e:
        logger.error(f"All web search methods failed: {e}")
        return {
            "success": False,
            "error": "Web search temporarily unavailable",
            "results": []
        }

def _search_with_serper(query: str, num_results: int, api_key: str) -> Dict:
    """Search using Serper API (paid but comprehensive)"""
    url = "https://google.serper.dev/search"
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "q": query,
        "num": num_results
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    results = []
    if "organic" in data:
        for item in data["organic"]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
                "source": "web_search"
            })
    
    return {
        "success": True,
        "results": results,
        "answer": data.get("answerBox", {}).get("answer", ""),
        "search_engine": "Google (via Serper)"
    }

def _search_with_duckduckgo(query: str) -> Dict:
    """Search using DuckDuckGo Instant Answer API (free but limited)"""
    url = "https://api.duckduckgo.com/"
    
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1"
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    results = []
    
    # Get instant answer if available
    instant_answer = ""
    if data.get("Answer"):
        instant_answer = data["Answer"]
    elif data.get("AbstractText"):
        instant_answer = data["AbstractText"]
    
    # Get related topics
    if data.get("RelatedTopics"):
        for topic in data["RelatedTopics"][:3]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append({
                    "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " ").title(),
                    "snippet": topic["Text"],
                    "link": topic.get("FirstURL", ""),
                    "source": "web_search"
                })
    
    return {
        "success": True,
        "results": results,
        "answer": instant_answer,
        "search_engine": "DuckDuckGo"
    }

def synthesize_web_results_with_llm(search_results: Dict, query: str) -> str:
    """
    Use Ollama Mistral to synthesize web search results into a coherent answer
    
    Args:
        search_results: Raw search results from web search
        query: Original search query
        
    Returns:
        LLM-synthesized answer from web results
    """
    if not search_results.get("success", False) or not search_results.get("results"):
        return "No relevant web information found for your query."
    
    try:
        # Initialize Ollama LLM (same as your existing setup)
        llm = OllamaLLM(model="mistral")
        
        # Prepare context from web results
        results = search_results.get("results", [])
        search_engine = search_results.get("search_engine", "Web Search")
        
        context_pieces = []
        for i, result in enumerate(results[:5], 1):
            context_pieces.append(
                f"Source {i}: {result['title']}\n"
                f"Content: {result['snippet']}\n"
                f"URL: {result['link']}\n"
            )
        
        context = "\n".join(context_pieces)
        
        # Create synthesis prompt
        synthesis_prompt = f"""Based on the following web search results, provide a comprehensive and well-structured answer to the user's question: "{query}"

Web Search Results:
{context}

Instructions:
1. Synthesize the information from multiple sources into a coherent, informative answer
2. Focus on answering the user's specific question
3. If there are conflicting information, mention it briefly
4. Keep the response clear and concise but comprehensive
5. Do not mention source numbers or URLs in your response - just provide the synthesized information
6. Write in a natural, helpful tone

Please provide a well-structured answer based on the web search results above:"""

        # Get LLM response
        synthesized_answer = llm.invoke(synthesis_prompt)
        
        return synthesized_answer
        
    except Exception as e:
        logger.error(f"LLM synthesis failed: {e}")
        # Fallback to basic formatting
        return _format_basic_web_results(search_results, query)

def _format_basic_web_results(search_results: Dict, query: str) -> str:
    """Fallback formatting if LLM synthesis fails"""
    results = search_results.get("results", [])
    answer = search_results.get("answer", "")
    
    formatted_answer = "🌐 **Web Search Results:**\n\n"
    
    if answer:
        formatted_answer += f"**Quick Answer:** {answer}\n\n"
    
    if results:
        for i, result in enumerate(results[:3], 1):
            formatted_answer += f"{i}. **{result['title']}**\n"
            formatted_answer += f"   {result['snippet']}\n\n"
    
    return formatted_answer

def format_web_search_response(search_results: Dict, query: str) -> Dict:
    """
    Format web search results using LLM synthesis for consistent display
    
    Args:
        search_results: Raw search results from web search
        query: Original search query
        
    Returns:
        Formatted response for display with LLM-synthesized answer
    """
    if not search_results.get("success", False):
        return {
            "answer": f"❌ Web search failed: {search_results.get('error', 'Unknown error')}",
            "sources": [],
            "search_info": "Web search unavailable"
        }
    
    results = search_results.get("results", [])
    search_engine = search_results.get("search_engine", "Web Search")
    
    if not results:
        return {
            "answer": f"🌐 No web results found for: '{query}'",
            "sources": [],
            "search_info": f"Searched via {search_engine}"
        }
    
    # Use LLM to synthesize the results
    try:
        synthesized_content = synthesize_web_results_with_llm(search_results, query)
        
        # Format the final response
        formatted_answer = f"**Answer not found in provided documents, searching the web:**\n\n{synthesized_content}\n\n*Information synthesized from web search via {search_engine}*"
        
    except Exception as e:
        logger.error(f"Error in synthesis: {e}")
        # Fallback to basic formatting
        formatted_answer = f"**Answer not found in provided documents, searching the web:**\n\n"
        formatted_answer += _format_basic_web_results(search_results, query)
        formatted_answer += f"\n\n*Source: {search_engine}*"
    
    # Prepare sources for display
    sources = []
    for result in results:
        if result.get("link"):
            sources.append(f"🌐 {result['link']}")
    
    return {
        "answer": formatted_answer,
        "sources": sources,
        "search_info": f"Web search via {search_engine} + LLM synthesis"
    }

def has_relevant_rag_results(rag_result: Dict, min_score_threshold: float = 0.3) -> bool:
    """
    Determine if RAG results are relevant enough to avoid web search
    
    Args:
        rag_result: Result from RAG query
        min_score_threshold: Minimum relevance score to consider relevant
        
    Returns:
        True if RAG results are sufficient, False if web search is needed
    """
    source_documents = rag_result.get("source_documents", [])
    
    # No documents found
    if not source_documents:
        return False
    
    # Check if the result seems generic or unhelpful
    result_text = rag_result.get("result", "").lower()
    
    # Generic responses that indicate poor relevance
    generic_indicators = [
        "i don't know",
        "i cannot",
        "no information",
        "not mentioned",
        "unclear",
        "insufficient information",
        "not enough context"
    ]
    
    if any(indicator in result_text for indicator in generic_indicators):
        return False
    
    # If we have documents and the response seems substantial, consider it relevant
    if len(source_documents) > 0 and len(result_text.strip()) > 50:
        return True
    
    return False
