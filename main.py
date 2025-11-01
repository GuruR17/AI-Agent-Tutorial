"""
Simple usage examples for ResearchAgent
"""

from research_agent import ResearchAgent


# --------------------------
# Example 1: Single Query
# --------------------------
def simple_research():
    print("\n" + "="*60)
    print("Example 1: Simple Research")
    print("="*60)
    
    query = input("\n📝 What would you like to research? ").strip()
    
    if not query:
        print("❌ No query provided.")
        return
    
    verbose = input("🔍 Show progress? (y/n): ").strip().lower() == 'y'
    
    agent = ResearchAgent()
    print(f"\n🚀 Researching: '{query}'...\n")
    result = agent.research(query, verbose=verbose)
    
    print("\n" + "="*60)
    print("✅ RESULTS")
    print("="*60)
    print(f"\n📊 Summary:\n{result.summary}")
    if result.sources:
        print(f"\n🔗 Sources: {', '.join(result.sources)}")
    if result.tools_used:
        print(f"\n🛠️ Tools Used: {', '.join(result.tools_used)}")


# --------------------------
# Example 2: Batch Research
# --------------------------
def batch_research():
    print("\n" + "="*60)
    print("Example 2: Batch Research")
    print("="*60)
    
    agent = ResearchAgent()
    
    queries = [
        "CALCULATETABLE DAX query",
        "Python list comprehension",
        "React useEffect hook"
    ]
    
    results = []
    for query in queries:
        print(f"\n📝 Researching: {query}")
        result = agent.research(query, verbose=False)
        results.append(result)
        print(f"✅ Summary: {result.summary[:150]}...")
    
    return results


# --------------------------
# Example 3: Interactive Mode
# --------------------------
def interactive_mode():
    print("\n" + "="*60)
    print("🔬 Interactive Research Agent")
    print("="*60)
    
    agent = ResearchAgent()
    
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


# --------------------------
# Example 4: Save Results
# --------------------------
def research_and_save():
    print("\n" + "="*60)
    print("Example 4: Research and Save")
    print("="*60)
    
    agent = ResearchAgent()
    
    query = "CALCULATETABLE DAX best practices"
    result = agent.research(query, verbose=False)
    
    # Save to file
    with open("research_results.txt", "w") as f:
        f.write(f"Topic: {result.topic}\n\n")
        f.write(f"Summary:\n{result.summary}\n\n")
        f.write(f"Sources: {', '.join(result.sources)}\n")
        f.write(f"Tools Used: {', '.join(result.tools_used)}\n")
    
    print(f"✅ Research complete and saved to research_results.txt")
    print(f"\n📊 Summary:\n{result.summary}")


# --------------------------
# Main Menu
# --------------------------
if __name__ == "__main__":
    print("="*60)
    print("Research Agent - Usage Examples")
    print("="*60)
    print("\nChoose an example:")
    print("1. Simple Research (single query)")
    print("2. Batch Research (multiple queries)")
    print("3. Interactive Mode (continuous queries)")
    print("4. Research and Save (save to file)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        simple_research()
    elif choice == "2":
        batch_research()
    elif choice == "3":
        interactive_mode()
    elif choice == "4":
        research_and_save()
    else:
        print("Invalid choice. Running interactive mode...")
        interactive_mode()