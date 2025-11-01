from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import json
import re

load_dotenv()

# --------------------------
# Structured Response
# --------------------------
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# --------------------------
# Research Agent Class
# --------------------------
class ResearchAgent:
    """
    A dynamic research agent that uses LLM reasoning to decide which tools to use.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize the research agent.
        
        Args:
            model: OpenAI model to use
            temperature: Temperature for LLM responses
        """
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=ResearchResponse)
        self.conversation_history = []  # Store previous queries and results
        
        # Initialize tools
        self._init_tools()
    
    def _init_tools(self):
        """Initialize all available tools."""
        
        @tool
        def search_tool(query: str) -> str:
            """Search DuckDuckGo for information online."""
            try:
                search = DuckDuckGoSearchRun()
                results = search.run(query)
                return f"DuckDuckGo Search Results: {results}"
            except Exception as e:
                return f"Search error: {str(e)}"
        
        @tool
        def wiki_tool(query: str) -> str:
            """Fetch relevant Wikipedia information."""
            try:
                wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
                results = wikipedia.run(query)
                return f"Wikipedia: {results}"
            except Exception as e:
                return f"Wikipedia error: {str(e)}"
        
        @tool
        def save_tool(data: str) -> str:
            """Save research results to a file."""
            try:
                with open("research_output.txt", "a") as f:
                    f.write(data + "\n")
                return "Data saved to research_output.txt"
            except Exception as e:
                return f"Save error: {str(e)}"
        
        self.tool_map = {
            "search_tool": search_tool,
            "wiki_tool": wiki_tool,
            "save_tool": save_tool,
        }
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks."""
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text
    
    def research(
        self, 
        query: str, 
        max_iterations: int = 5, 
        verbose: bool = False
    ) -> ResearchResponse:
        """
        Conduct research on the given query.
        
        Args:
            query: The research question or topic
            max_iterations: Maximum number of reasoning iterations
            verbose: If True, print detailed progress
        
        Returns:
            ResearchResponse with findings
        """
        state = {
            "tools_used": [], 
            "tool_results": {}, 
            "topic": query, 
            "summary": "", 
            "sources": []
        }
        
        # Build conversation context
        context = ""
        if self.conversation_history:
            context = "\n\nPrevious conversation:\n"
            for i, item in enumerate(self.conversation_history[-3:], 1):  # Last 3 exchanges
                context += f"\nQuery {i}: {item['query']}\n"
                context += f"Answer: {item['summary'][:200]}...\n"
        
        for iteration in range(1, max_iterations + 1):
            if verbose:
                print(f"\n🔹 Iteration {iteration}")

            llm_input = f"""
User query: {query}
{context}

Tools already used: {state['tools_used']}
Previous results: {json.dumps(state['tool_results'], indent=2)}

Available tools: {list(self.tool_map.keys())}

IMPORTANT INSTRUCTIONS:
1. If this is a follow-up question (like "show me an example"), use context from previous conversation
2. Call multiple tools in ONE iteration (e.g., ["search_tool", "wiki_tool"])
3. ALWAYS include specific sources in your "sources" list
4. After calling 2+ tools, immediately provide final summary
5. Be efficient - aim to complete in 2-3 iterations maximum

Return JSON with:
- "summary": detailed findings summary (required after tools are called)
- "sources": list of sources consulted (required, extract from tool results)
- "tools_used": list of NEW tools to call NOW (can be multiple at once)

{self.parser.get_format_instructions()}
"""
            
            try:
                llm_output = self.llm.invoke(llm_input)
                llm_text = llm_output.content if hasattr(llm_output, "content") else str(llm_output)
                
                json_text = self._extract_json(llm_text)
                plan = json.loads(json_text)
                
                state["summary"] = plan.get("summary", state["summary"])
                state["sources"] = plan.get("sources", state["sources"])
                new_tools = plan.get("tools_used", [])
                
                if not new_tools and state["summary"]:
                    if len(state["tools_used"]) >= 2:
                        if verbose:
                            print("✅ Research complete")
                        break
                    elif verbose:
                        print("⚠️ Need to call more tools before completing")
                
                for tool_name in new_tools:
                    if tool_name in self.tool_map and tool_name not in state["tool_results"]:
                        if verbose:
                            print(f"🔧 Calling: {tool_name}")
                        result = self.tool_map[tool_name].run(query)
                        state["tool_results"][tool_name] = result
                        state["tools_used"].append(tool_name)
            
            except Exception as e:
                if verbose:
                    print(f"⚠️ Error: {e}")
                continue
        
        # Create response
        response = ResearchResponse(
            topic=state["topic"],
            summary=state["summary"] or "Unable to complete research",
            sources=state["sources"] or [],
            tools_used=state["tools_used"]
        )
        
        # Save to conversation history
        self.conversation_history.append({
            "query": query,
            "summary": response.summary,
            "sources": response.sources
        })
        
        return response
    
    def add_tool(self, name: str, tool_func):
        """
        Add a custom tool to the agent.
        
        Args:
            name: Name of the tool
            tool_func: Tool function decorated with @tool
        """
        self.tool_map[name] = tool_func
    
    def remove_tool(self, name: str):
        """Remove a tool from the agent."""
        if name in self.tool_map:
            del self.tool_map[name]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("🗑️ Conversation history cleared")


# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    # Create agent instance
    agent = ResearchAgent(model="gpt-4o-mini")
    
    # Option 1: Single query
    result = agent.research("CALCULATETABLE DAX query", verbose=True)
    print(f"\nSummary: {result.summary}")
    
    # Option 2: Interactive loop
    print("\n" + "="*60)
    print("🔬 Research Agent Ready")
    print("="*60)
    
    while True:
        query = input("\n📝 What can I help you research? (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        verbose = input("🔍 Show progress? (y/n): ").strip().lower() == 'y'
        
        print(f"\n🚀 Researching: '{query}'...")
        
        try:
            response = agent.research(query, verbose=verbose)
            
            print("\n" + "="*60)
            print("✅ RESULTS")
            print("="*60)
            print(f"\n📌 Topic: {response.topic}")
            print(f"\n📊 Summary:\n{response.summary}")
            if response.sources:
                print(f"\n🔗 Sources: {', '.join(response.sources)}")
            if response.tools_used:
                print(f"\n🛠️ Tools Used: {', '.join(response.tools_used)}")
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")