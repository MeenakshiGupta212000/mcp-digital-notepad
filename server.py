import os
from pathlib import Path
import chromadb
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# 1. Initialize MCP Server and Paths
mcp = FastMCP("AutomatedResearcher")
NOTES_DIR = Path("./my_notes")
NOTES_DIR.mkdir(exist_ok=True)

# 2. Initialize AI Vector DB (ChromaDB)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="personal_notes")

# 3. Create "List Notes" Tool
@mcp.tool()
def list_notes() -> str:
    """List all available markdown notes in the directory."""
    notes = [f.name for f in NOTES_DIR.glob("*.md")]
    if not notes:
        return "No notes found. The directory is empty."
    return "Available notes: " + ", ".join(notes)

# 4. Create "Read Note" Tool
@mcp.tool()
def read_note(filename: str) -> str:
    """Read the complete text of a specific note."""
    filepath = NOTES_DIR / filename
    if not filepath.exists():
        return f"error: Note '{filename}' does not exist"
    return filepath.read_text(encoding="utf-8")

# 5. Create "Save Note" Tool
@mcp.tool()
def save_note(filename: str, content: str) -> str:
    """Create a new markdown note or overwrite an existing one."""
    if not filename.endswith('.md'):
        filename += '.md'
    filepath = NOTES_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    
    # FIX: Changed 'metadata' to 'metadatas'
    collection.upsert(
        documents=[content],
        metadatas=[{"filename": filename}],
        ids=[filename]
    )
    return f"Success! saved note as {filename}"

# 6. Create "Semantic Search" Tool
@mcp.tool()
def search_memory(query: str) -> str:
    """Search the notes based on the meaning of the query, not just exact keywords."""
    res = collection.query(
        query_texts=[query],
        n_results=2 
    )
    
    if not res['documents'][0]:
        return "No relevant notes found."
        
    response = "Here are the most conceptually similar notes:\n\n"
    found_match = False
    
    for i, doc in enumerate(res['documents'][0]):
        filename = res['metadatas'][0][i]['filename']
        distance = res['distances'][0][i] # NEW: Get the math score
        
        # In ChromaDB, a LOWER distance means it's a closer match. 
        # A distance over 1.66 usually means the concepts are unrelated.
        if distance > 1.66:
            continue # Skip this note, it's irrelevant!
            
        found_match = True
        response += f"---From {filename} (Distance: {distance:.2f})---\n{doc}\n\n"
    
    if not found_match:
        return f"I searched my memory, but found nothing relevant to '{query}'."
        
    return response

# automated web researcher (agentic workflow component)
@mcp.tool()
def fetch_and_remember_website(url:str, filename:str)->str:
    """Scrape a website, extract its text, and automatically save it to AI memory."""
    try:
        # use httpx to download webpage content
        headers={"USer-Agent":"MCP-Researcher-Bot/1.0"}
        response=httpx.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        # use beautifulSoup to clean HTML and get pure text
        soup=BeautifulSoup(response.text, "html.parser")
        # remove script and style elements so we dont get junk code
        for script in soup(["script", "style"]):
            script.extract()
        text_content=soup.get_text(separator="\n")
        # Clean up whitespace gaps
        lines=(line.strip() for line in text_content.splitlines())
        chunks=(phrase for line in lines for phrase in line.split(" "))
        clean_txt="\n".join(chunk for chunk in chunks if chunk )
        # Take the first 3000 characters so we don't overwhelm the database entry
        truncate_txt=clean_txt[:3000]
        #automatically use our save_note func to store it & embed it
        save_res=save_note(filename, truncate_txt)
        return f"successfully read website {save_res}"
    except Exception as e:
        return f"Failed to scrape website. Error : {str(e)}"
if __name__ == "__main__":
    mcp.run()