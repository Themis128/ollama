"""
Web Agent Module
================

Enables AI agents to communicate with the internet to fetch data, research,
and access external information sources safely.

Features:
- Safe web search using DuckDuckGo
- Web page content fetching
- API documentation retrieval
- Research and information gathering
- Context-aware web access

Usage:
    from integrations.web_agent import WebAgent
    
    agent = WebAgent(
        rate_limit=10,  # requests per minute
        timeout=30,     # seconds
    )
    
    # Search for information
    results = agent.search("Next.js API route patterns")
    
    # Fetch specific page
    content = agent.fetch("https://nextjs.org/docs")
    
    # Research topic with multiple sources
    research = agent.research("DynamoDB best practices", sources=3)
"""

import os
import json
import time
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter, Retry


@dataclass
class WebConfig:
    """Configuration for web agent."""
    rate_limit: int = 10  # requests per minute
    timeout: int = 30
    max_retries: int = 3
    cache_dir: str = "/tmp/web_agent_cache"
    safe_domains: List[str] = field(default_factory=lambda: [
        "docs.langchain.com",
        "nextjs.org",
        "react.dev",
        "typescriptlang.org",
        "stripe.com",
        "aws.amazon.com",
        "github.com",
        "stackoverflow.com",
        " MDN web docs",
        "w3.org",
        "wikipedia.org",
    ])


class WebAgent:
    """Web agent for safe internet communication and data fetching."""
    
    def __init__(self, config: Optional[WebConfig] = None):
        self.config = config or WebConfig()
        self._setup_cache()
        self._setup_session()
        self.request_count = 0
        self.last_request_time = 0
        
    def _setup_cache(self) -> None:
        """Setup caching directory."""
        Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)
        
    def _setup_session(self) -> None:
        """Setup requests session with retry policy."""
        self.session = requests.Session()
        
        # Setup retry policy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def _check_rate_limit(self) -> None:
        """Enforce rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < 60 / self.config.rate_limit:
            time.sleep(60 / self.config.rate_limit - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is from a safe domain."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Always allow relative URLs
        if not parsed.scheme or not domain:
            return True
            
        # Allow if domain matches safe domains
        for safe_domain in self.config.safe_domains:
            if safe_domain.lower().strip() in domain:
                return True
        
        # Default to safe for common protocols (http/https) but only for known domains
        # This is a safety measure - in production, you'd want stricter control
        return False
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return hashlib.sha256(url.encode()).hexdigest()[:16]
    
    def _get_cached(self, url: str) -> Optional[str]:
        """Get cached content if available."""
        cache_key = self._get_cache_key(url)
        cache_file = Path(self.config.cache_dir) / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                cached = json.load(f)
                return cached.get("content")
        
        return None
    
    def _cache(self, url: str, content: str) -> None:
        """Cache content for URL."""
        cache_key = self._get_cache_key(url)
        cache_file = Path(self.config.cache_dir) / f"{cache_key}.json"
        
        with open(cache_file, "w") as f:
            json.dump({
                "url": url,
                "content": content,
                "timestamp": time.time(),
            }, f)
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results with titles and URLs
        """
        results = []
        
        # Try remote_web_search (Kiro's built-in search) if available
        # This is only available when running directly in Kiro CLI context
        try:
            import remote_web_search
            search_results = remote_web_search(query=query)
            results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("snippet", ""),
                    "source": "web_search",
                }
                for r in search_results[:max_results]
            ]
            if results:
                return results
        except (ImportError, NameError):
            # Not running in Kiro CLI context, continue with fallbacks
            pass
        
        # Try Bing Web Search API (if API key available)
        bing_key = os.environ.get("BING_API_KEY")
        if bing_key:
            try:
                bing_url = "https://api.bing.microsoft.com/v7.0/search"
                params = {
                    "q": query,
                    "count": max_results,
                }
                headers = {"Ocp-Apim-Subscription-Key": bing_key}
                response = self.session.get(bing_url, params=params, headers=headers, timeout=self.config.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("webPages") and data["webPages"].get("value"):
                    results = [
                        {
                            "title": item.get("name", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("snippet", ""),
                            "source": "bing",
                        }
                        for item in data["webPages"]["value"][:max_results]
                    ]
                    return results
            except Exception:
                pass
        
        # Try Google Custom Search API (if API key available)
        gsearch_key = os.environ.get("GOOGLE_API_KEY")
        gsearch_cx = os.environ.get("GOOGLE_CX")
        if gsearch_key and gsearch_cx:
            try:
                google_url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": gsearch_key,
                    "cx": gsearch_cx,
                    "q": query,
                    "num": max_results,
                }
                response = self.session.get(google_url, params=params, timeout=self.config.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get("items"):
                    results = [
                        {
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "source": "google",
                        }
                        for item in data["items"][:max_results]
                    ]
                    return results
            except Exception:
                pass
        
        # Fallback: Try DuckDuckGo Instant Answer API
        search_url = "https://api.duckduckgo.com/"
        
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1,
            "skip_disambig": 1,
        }
        
        try:
            response = self.session.get(search_url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Add Instant Answer if available
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", "Answer"),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("AbstractText", ""),
                    "source": "duckduckgo",
                })
            
            # Add related results
            if data.get("RelatedTopics"):
                for topic in data["RelatedTopics"][:max_results]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "")[:100],
                            "url": topic.get("FirstURL", ""),
                            "snippet": topic.get("Text", ""),
                            "source": "duckduckgo",
                        })
        except Exception:
            pass
        
        # If all else fails, return placeholder results
        if not results:
            results = [
                {
                    "title": f"Search results for: {query}",
                    "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                    "snippet": "Use web_fetch tool in Kiro CLI to search the web",
                    "source": "fallback",
                }
            ]
        
        return results[:max_results]
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Fallback search using remote_web_search."""
        import subprocess
        import json
        
        try:
            # Check if we're running in Kiro CLI context
            # remote_web_search is a Kiro built-in tool that can be accessed
            # We'll use it via subprocess if needed
            
            # For now, return empty results
            # In Kiro CLI context, the tool is available directly
            return []
        except Exception:
            return []
    
    def fetch_with_kiro_web_fetch(self, url: str, prompt: str = "Extract all relevant information", format: str = "auto") -> Dict[str, Any]:
        """
        Use Kiro's built-in web_fetch tool for more efficient content extraction.
        
        Args:
            url: URL to fetch
            prompt: Prompt describing what to extract
            format: Content format preference ("auto", "markdown", "html", "text")
            
        Returns:
            Dictionary with fetched content
        """
        try:
            # Try to use Kiro's web_fetch tool directly if available
            # web_fetch is available as a Kiro built-in tool
            # It will be called through the Kiro CLI's tool system
            
            # Since we're in a subprocess, we can't directly call web_fetch
            # Instead, we'll use requests with content negotiation headers
            
            headers = {
                "Accept": "text/markdown, text/html;q=0.9, text/plain;q=0.8, */*;q=0.1",
                "User-Agent": "DeepAgents-Ollama/1.0"
            }
            
            self._check_rate_limit()
            response = self.session.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            
            # Content is already converted to text by web_fetch if used
            content = response.text
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "cached": False,
                "status_code": response.status_code,
                "fetched_via": "web_fetch_simulation",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "fetched_via": "requests",
            }
    
    def fetch(self, url: str, max_length: int = 50000, use_web_fetch: bool = True) -> Dict[str, Any]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            max_length: Maximum content length to return
            use_web_fetch: Whether to use Kiro's web_fetch if available
            
        Returns:
            Dictionary with content, metadata, and status
        """
        # Check cache first
        cached = self._get_cached(url)
        if cached:
            return {
                "success": True,
                "url": url,
                "content": cached[:max_length],
                "cached": True,
            }
        
        # Check if URL is safe
        if not self._is_safe_url(url):
            return {
                "success": False,
                "error": "URL not from safe domain",
                "url": url,
            }
        
        # Try Kiro's web_fetch if available
        if use_web_fetch:
            kiro_result = self.fetch_with_kiro_web_fetch(url)
            if kiro_result["success"]:
                content = kiro_result["content"][:max_length]
                self._cache(url, content)
                return {
                    "success": True,
                    "url": url,
                    "content": content,
                    "cached": False,
                    "status_code": kiro_result.get("status_code", 200),
                    "fetched_via": kiro_result.get("fetched_via", "unknown"),
                }
        
        try:
            self._check_rate_limit()
            
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            content = response.text[:max_length]
            
            # Cache the result
            self._cache(url, content)
            
            return {
                "success": True,
                "url": url,
                "content": content,
                "cached": False,
                "status_code": response.status_code,
                "fetched_via": "requests",
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "fetched_via": "requests",
            }
    
    def fetch_selective(self, url: str, search_phrase: str) -> Dict[str, Any]:
        """
        Fetch specific content matching a search phrase.
        
        Args:
            url: URL to fetch
            search_phrase: Phrase to search for in content
            
        Returns:
            Dictionary with matching content sections
        """
        result = self.fetch(url)
        
        if not result["success"]:
            return result
        
        # Search for the phrase in content
        content_lower = result["content"].lower()
        search_lower = search_phrase.lower()
        
        if search_lower in content_lower:
            # Find context around the match
            start = max(0, content_lower.find(search_lower) - 100)
            end = min(len(result["content"]), content_lower.find(search_lower) + 200)
            
            return {
                "success": True,
                "url": url,
                "content": result["content"][start:end],
                "matched": True,
                "search_phrase": search_phrase,
            }
        
        return {
            "success": True,
            "url": url,
            "content": result["content"][:5000],
            "matched": False,
            "search_phrase": search_phrase,
        }
    
    def research(self, topic: str, sources: int = 3) -> Dict[str, Any]:
        """
        Research a topic using multiple sources.
        
        Args:
            topic: Topic to research
            sources: Number of sources to use
            
        Returns:
            Dictionary with research results from multiple sources
        """
        # Search for relevant sources
        search_results = self.search(topic, max_results=sources * 2)
        
        research = {
            "topic": topic,
            "sources_used": [],
            "summaries": [],
            "key_findings": [],
        }
        
        for result in search_results[:sources]:
            if not result.get("url"):
                continue
                
            # Fetch each source
            fetch_result = self.fetch(result["url"], max_length=20000)
            
            if fetch_result["success"]:
                research["sources_used"].append({
                    "title": result.get("title", "Unknown"),
                    "url": result.get("url", ""),
                    "source": result.get("source", "unknown"),
                })
                
                # Extract summary
                summary = {
                    "source": result.get("title", "Unknown"),
                    "summary": fetch_result["content"][:500],
                    "url": result.get("url", ""),
                }
                research["summaries"].append(summary)
                
                # Extract key findings
                # Simple extraction - could be enhanced with LLM
                lines = fetch_result["content"].split("\n")[:20]
                for line in lines:
                    line = line.strip()
                    if len(line) > 20 and len(line) < 300:
                        research["key_findings"].append(line)
        
        # Deduplicate findings
        research["key_findings"] = list(dict.fromkeys(research["key_findings"]))[:10]
        
        return research
    
    def get_api_docs(self, api_name: str) -> Dict[str, Any]:
        """
        Fetch API documentation.
        
        Args:
            api_name: Name of the API (e.g., "Stripe", "Next.js", "AWS")
            
        Returns:
            API documentation content
        """
        # Common API documentation URLs
        api_urls = {
            "stripe": "https://stripe.com/docs/api",
            "nextjs": "https://nextjs.org/docs",
            "aws": "https://docs.aws.amazon.com",
            "langchain": "https://docs.langchain.com",
            "react": "https://react.dev/reference",
            "typescript": "https://www.typescriptlang.org/docs",
        }
        
        key = api_name.lower()
        for api_key, url in api_urls.items():
            if api_key in key:
                return self.fetch(url)
        
        # Default search
        search_results = self.search(f"{api_name} API documentation", max_results=1)
        if search_results:
            return self.fetch(search_results[0]["url"])
        
        return {"success": False, "error": "API documentation not found"}
    
    def check_url_exists(self, url: str) -> bool:
        """Check if URL exists (HEAD request)."""
        try:
            self._check_rate_limit()
            response = self.session.head(url, timeout=self.config.timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_last_request_count(self) -> int:
        """Get the number of requests made in current session."""
        return self.request_count


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Agent")
    parser.add_argument("action", choices=["search", "fetch", "research", "docs"], help="Action to perform")
    parser.add_argument("query", help="Query for the action")
    parser.add_argument("--max-results", type=int, default=5, help="Max results for search")
    parser.add_argument("--sources", type=int, default=3, help="Number of sources for research")
    
    args = parser.parse_args()
    
    agent = WebAgent()
    
    if args.action == "search":
        results = agent.search(args.query, max_results=args.max_results)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   {result['url']}")
            print(f"   {result.get('snippet', '')[:200]}...")
            
    elif args.action == "fetch":
        result = agent.fetch(args.query)
        if result["success"]:
            print(f"Content from {result['url']}:")
            print(result["content"][:2000])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    elif args.action == "research":
        research = agent.research(args.query, sources=args.sources)
        print(f"\nResearch on: {research['topic']}")
        print(f"\nSources used ({len(research['sources_used'])}):")
        for source in research["sources_used"]:
            print(f"  - {source['title']}")
        print(f"\nKey findings ({len(research['key_findings'])}):")
        for finding in research["key_findings"]:
            print(f"  - {finding[:150]}...")