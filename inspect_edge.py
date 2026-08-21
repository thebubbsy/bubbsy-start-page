import os
import json
import re

edge_base = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data')

def extract_bookmarks(node, path=''):
    results = []
    name = node.get('name', '')
    node_type = node.get('type', '')
    current_path = f"{path} > {name}" if path else name
    
    if node_type == 'url':
        results.append({
            'name': name,
            'url': node.get('url', ''),
            'folder': path
        })
    elif node_type == 'folder':
        children = node.get('children', [])
        for c in children:
            results.extend(extract_bookmarks(c, current_path))
    return results

for prof in ['Profile 1', 'Default']:
    bm_file = os.path.join(edge_base, prof, 'Bookmarks')
    if os.path.exists(bm_file):
        with open(bm_file, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        all_bms = []
        roots = data.get('roots', {})
        for root_name, root_node in roots.items():
            if isinstance(root_node, dict):
                all_bms.extend(extract_bookmarks(root_node, root_name))
        
        print(f"\n=================== {prof} (Total: {len(all_bms)}) ===================")
        # Filter non-onlyfans/gaming to see tech, dev, osint, data, ai
        tech_bms = []
        for b in all_bms:
            url = b['url'].lower()
            name = b['name'].lower()
            folder = b['folder'].lower()
            if any(k in url or k in name or k in folder for k in [
                'ai', 'gpt', 'claude', 'anthropic', 'openai', 'gemini', 'perplexity', 'mistral', 
                'deepseek', 'groq', 'cohere', 'midjourney', 'stable', 'hugging', 'ollama', 
                'replicate', 'agent', 'rag', 'llm', 'prompt', 'openrouter', 'v0', 'cursor', 
                'github', 'gitlab', 'osint', 'tool', 'search', 'model', 'api', 'bot', 'data',
                'server', 'cloud', 'intel', 'cyber', 'sec', 'dev', 'python', 'shodan', 'censys'
            ]):
                tech_bms.append(b)
        
        print(f"Tech/Tool/AI bookmarks in {prof}: {len(tech_bms)}")
        for b in tech_bms:
            safe_name = b['name'].encode('ascii', errors='replace').decode('ascii')
            print(f"  [{b['folder']}] {safe_name} -> {b['url']}")
