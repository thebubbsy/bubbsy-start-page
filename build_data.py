import json
import os
import re

from modules_extra import (
    AUS_EXTRA_WIDGETS,
    GLOBAL_EXTRA_WIDGETS,
    EXTRA_WIDGET_IDS,
    apply_au_priority,
)

def clean_domain(url):
    if not url:
        return ""
    try:
        domain = re.sub(r'^https?:\/\/', '', url)
        domain = domain.split('/')[0].split('?')[0].split(':')[0]
        return domain.lower()
    except Exception:
        return ""

def build_data():
    base_file = 'data/osint_data.json'
    if not os.path.exists(base_file):
        print("Base data not found!")
        return

    with open(base_file, 'r', encoding='utf-8') as f:
        base_data = json.load(f)

    columns = base_data.get('columns', [])
    world_clocks = base_data.get('world_clocks', [])
    rss_feeds = base_data.get('rss_feeds', [])

    # Filter out AI & Australian widgets to cleanly rebuild them with clean evergreen titles
    # (id-based so any additional [AUS]/visual widgets added by hand in osint_data.json survive rebuilds)
    REBUILT_WIDGET_IDS = {9001, 9002, 9003, 9004, 9005, 9006, 9101, 9102, 9103, 9104, 9105, 9106,
                          9107, 9108, 9109, 9110, 9111, 9112, 9201, 9202, 9203, 9204, 9205, 9206}
    REBUILT_WIDGET_IDS |= EXTRA_WIDGET_IDS
    for col in columns:
        col['widgets'] = [w for w in col.get('widgets', []) if w.get('id') not in REBUILT_WIDGET_IDS]

    # Clean, evergreen AI Modules (no outdated model versions or cringe emojis)
    ai_widgets = [
        {
            'id': 9001,
            'title': 'AI ASSISTANTS & CHAT',
            'type': 'urllist',
            'group': 'ai_hub',
            'icon': 'sparkles',
            'color': '#10b981',
            'links': [
                {'title': 'ChatGPT', 'url': 'https://chatgpt.com/', 'description': 'Conversational AI and reasoning by OpenAI', 'domain': 'chatgpt.com', 'favicon': 'https://f.start.me/chatgpt.com'},
                {'title': 'Claude', 'url': 'https://claude.ai/', 'description': 'AI assistant for coding, research, and analysis by Anthropic', 'domain': 'claude.ai', 'favicon': 'https://f.start.me/claude.ai'},
                {'title': 'Google Gemini', 'url': 'https://gemini.google.com/', 'description': 'Multimodal context and search-grounded assistant by Google', 'domain': 'google.com', 'favicon': 'https://f.start.me/gemini.google.com'},
                {'title': 'DeepSeek Chat', 'url': 'https://chat.deepseek.com/', 'description': 'Open-weight reasoning and coding assistant', 'domain': 'deepseek.com', 'favicon': 'https://f.start.me/deepseek.com'},
                {'title': 'Perplexity', 'url': 'https://www.perplexity.ai/', 'description': 'Live web search and answer engine with sources', 'domain': 'perplexity.ai', 'favicon': 'https://f.start.me/perplexity.ai'},
                {'title': 'Mistral Le Chat', 'url': 'https://chat.mistral.ai/', 'description': 'Fast European AI assistant by Mistral AI', 'domain': 'mistral.ai', 'favicon': 'https://f.start.me/mistral.ai'},
                {'title': 'Groq', 'url': 'https://groq.com/', 'description': 'Ultra-fast LPU inference engine for open models', 'domain': 'groq.com', 'favicon': 'https://f.start.me/groq.com'},
                {'title': 'Microsoft Copilot', 'url': 'https://copilot.microsoft.com/', 'description': 'AI companion for search and productivity by Microsoft', 'domain': 'microsoft.com', 'favicon': 'https://f.start.me/copilot.microsoft.com'},
                {'title': 'Meta AI', 'url': 'https://www.meta.ai/', 'description': 'Open intelligence platform by Meta', 'domain': 'meta.ai', 'favicon': 'https://f.start.me/meta.ai'},
                {'title': 'Cohere Coral', 'url': 'https://coral.cohere.com/', 'description': 'Enterprise knowledge retrieval and agent platform', 'domain': 'cohere.com', 'favicon': 'https://f.start.me/cohere.com'},
                {'title': 'Poe', 'url': 'https://poe.com/', 'description': 'Multi-model hub to query and compare various bots', 'domain': 'poe.com', 'favicon': 'https://f.start.me/poe.com'},
                {'title': 'Pi', 'url': 'https://pi.ai/', 'description': 'Conversational dialogue and voice companion', 'domain': 'pi.ai', 'favicon': 'https://f.start.me/pi.ai'}
            ]
        },
        {
            'id': 9002,
            'title': 'AI SEARCH & RESEARCH',
            'type': 'urllist',
            'group': 'ai_hub',
            'icon': 'search',
            'color': '#06b6d4',
            'links': [
                {'title': 'Genspark', 'url': 'https://www.genspark.ai/', 'description': 'Autonomous multi-agent research search engine', 'domain': 'genspark.ai', 'favicon': 'https://f.start.me/genspark.ai'},
                {'title': 'Exa', 'url': 'https://exa.ai/', 'description': 'Embedding-based neural search designed for AI agents', 'domain': 'exa.ai', 'favicon': 'https://f.start.me/exa.ai'},
                {'title': 'Tavily', 'url': 'https://tavily.com/', 'description': 'Search API built for LLM research agents', 'domain': 'tavily.com', 'favicon': 'https://f.start.me/tavily.com'},
                {'title': 'Firecrawl', 'url': 'https://www.firecrawl.dev/', 'description': 'Turn websites into clean markdown for AI workflows', 'domain': 'firecrawl.dev', 'favicon': 'https://f.start.me/firecrawl.dev'},
                {'title': 'Consensus', 'url': 'https://consensus.app/', 'description': 'AI search across scientific papers and peer-reviewed studies', 'domain': 'consensus.app', 'favicon': 'https://f.start.me/consensus.app'},
                {'title': 'Elicit', 'url': 'https://elicit.com/', 'description': 'Automated research assistant for academic literature', 'domain': 'elicit.com', 'favicon': 'https://f.start.me/elicit.com'},
                {'title': 'Phind', 'url': 'https://www.phind.com/', 'description': 'Technical search engine optimized for developers', 'domain': 'phind.com', 'favicon': 'https://f.start.me/phind.com'},
                {'title': 'Scite', 'url': 'https://scite.ai/', 'description': 'Smart citation analysis for research claims', 'domain': 'scite.ai', 'favicon': 'https://f.start.me/scite.ai'},
                {'title': 'Semantic Scholar', 'url': 'https://www.semanticscholar.org/', 'description': 'AI-backed scholarly literature search', 'domain': 'semanticscholar.org', 'favicon': 'https://f.start.me/semanticscholar.org'},
                {'title': 'Kagi', 'url': 'https://kagi.com/', 'description': 'Fast, ad-free search with integrated summarizer', 'domain': 'kagi.com', 'favicon': 'https://f.start.me/kagi.com'}
            ]
        },
        {
            'id': 9003,
            'title': 'AI CODE & AGENTS',
            'type': 'urllist',
            'group': 'ai_hub',
            'icon': 'code',
            'color': '#8b5cf6',
            'links': [
                {'title': 'Cursor', 'url': 'https://www.cursor.com/', 'description': 'AI code editor with codebase indexing and Composer', 'domain': 'cursor.com', 'favicon': 'https://f.start.me/cursor.com'},
                {'title': 'v0', 'url': 'https://v0.dev/', 'description': 'Generative UI system producing React and Tailwind code', 'domain': 'v0.dev', 'favicon': 'https://f.start.me/v0.dev'},
                {'title': 'Bolt.new', 'url': 'https://bolt.new/', 'description': 'In-browser AI fullstack development sandbox', 'domain': 'bolt.new', 'favicon': 'https://f.start.me/bolt.new'},
                {'title': 'Claude Code', 'url': 'https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview', 'description': 'Agentic terminal tool for autonomous coding', 'domain': 'anthropic.com', 'favicon': 'https://f.start.me/anthropic.com'},
                {'title': 'Lovable', 'url': 'https://lovable.dev/', 'description': 'Fullstack app builder from natural language prompts', 'domain': 'lovable.dev', 'favicon': 'https://f.start.me/lovable.dev'},
                {'title': 'Windsurf', 'url': 'https://codeium.com/windsurf', 'description': 'Agentic coding environment by Codeium', 'domain': 'codeium.com', 'favicon': 'https://f.start.me/codeium.com'},
                {'title': 'OpenMemory', 'url': 'https://github.com/CaviraOSS/OpenMemory', 'description': 'Self-hosted long-term memory layer for AI agents', 'domain': 'github.com', 'favicon': 'https://f.start.me/github.com'},
                {'title': 'context-mode', 'url': 'https://github.com/mksglu/context-mode', 'description': 'Model Context Protocol virtualization tooling', 'domain': 'github.com', 'favicon': 'https://f.start.me/github.com'},
                {'title': 'Dify', 'url': 'https://dify.ai/', 'description': 'Open-source platform for building LLM applications and RAG', 'domain': 'dify.ai', 'favicon': 'https://f.start.me/dify.ai'},
                {'title': 'LangSmith', 'url': 'https://smith.langchain.com/', 'description': 'Observability and evaluation platform for AI agents', 'domain': 'langchain.com', 'favicon': 'https://f.start.me/langchain.com'},
                {'title': 'Flowise', 'url': 'https://flowiseai.com/', 'description': 'Drag-and-drop builder for custom LLM workflows', 'domain': 'flowiseai.com', 'favicon': 'https://f.start.me/flowiseai.com'},
                {'title': 'CrewAI', 'url': 'https://www.crewai.com/', 'description': 'Framework for orchestrating multi-agent workflows', 'domain': 'crewai.com', 'favicon': 'https://f.start.me/crewai.com'}
            ]
        },
        {
            'id': 9004,
            'title': 'LOCAL AI & OPEN SOURCE',
            'type': 'urllist',
            'group': 'ai_hub',
            'icon': 'cpu',
            'color': '#ec4899',
            'links': [
                {'title': 'Ollama', 'url': 'https://ollama.com/', 'description': 'Run open-weight models locally via CLI and API', 'domain': 'ollama.com', 'favicon': 'https://f.start.me/ollama.com'},
                {'title': 'Hugging Face', 'url': 'https://huggingface.co/models', 'description': 'Repository for open models, datasets, and Spaces', 'domain': 'huggingface.co', 'favicon': 'https://f.start.me/huggingface.co'},
                {'title': 'LM Studio', 'url': 'https://lmstudio.ai/', 'description': 'Run local LLMs with a desktop GUI', 'domain': 'lmstudio.ai', 'favicon': 'https://f.start.me/lmstudio.ai'},
                {'title': 'Jan', 'url': 'https://jan.ai/', 'description': 'Open-source local ChatGPT alternative that runs offline', 'domain': 'jan.ai', 'favicon': 'https://f.start.me/jan.ai'},
                {'title': 'OpenRouter', 'url': 'https://openrouter.ai/', 'description': 'Unified API router for hundreds of AI models', 'domain': 'openrouter.ai', 'favicon': 'https://f.start.me/openrouter.ai'},
                {'title': 'Chatbot Arena', 'url': 'https://lmarena.ai/', 'description': 'Community benchmark leaderboard for AI models', 'domain': 'lmarena.ai', 'favicon': 'https://f.start.me/lmarena.ai'},
                {'title': 'Together AI', 'url': 'https://www.together.ai/', 'description': 'Cloud inference platform for open-source models', 'domain': 'together.ai', 'favicon': 'https://f.start.me/together.ai'},
                {'title': 'Replicate', 'url': 'https://replicate.com/', 'description': 'Run open machine learning models in the cloud', 'domain': 'replicate.com', 'favicon': 'https://f.start.me/replicate.com'},
                {'title': 'LocalAI', 'url': 'https://localai.io/', 'description': 'Self-hosted OpenAI-compatible REST API', 'domain': 'localai.io', 'favicon': 'https://f.start.me/localai.io'},
                {'title': 'vLLM', 'url': 'https://vllm.ai/', 'description': 'High-throughput engine for serving LLMs', 'domain': 'vllm.ai', 'favicon': 'https://f.start.me/vllm.ai'},
                {'title': 'ComfyUI', 'url': 'https://github.com/comfyanonymous/ComfyUI', 'description': 'Modular node-based interface for image and video diffusion', 'domain': 'github.com', 'favicon': 'https://f.start.me/github.com'}
            ]
        },
        {
            'id': 9005,
            'title': 'AI IMAGE & VIDEO',
            'type': 'urllist',
            'group': 'ai_hub',
            'icon': 'image',
            'color': '#f59e0b',
            'links': [
                {'title': 'Midjourney', 'url': 'https://www.midjourney.com/', 'description': 'Photorealistic image synthesis platform', 'domain': 'midjourney.com', 'favicon': 'https://f.start.me/midjourney.com'},
                {'title': 'FLUX (Black Forest Labs)', 'url': 'https://blackforestlabs.ai/', 'description': 'Text-to-image models and generation', 'domain': 'blackforestlabs.ai', 'favicon': 'https://f.start.me/blackforestlabs.ai'},
                {'title': 'Recraft', 'url': 'https://www.recraft.ai/', 'description': 'Design tool generating vector SVG and 3D graphics', 'domain': 'recraft.ai', 'favicon': 'https://f.start.me/recraft.ai'},
                {'title': 'Bing Image Creator', 'url': 'https://www.bing.com/images/create', 'description': 'Free web image generation', 'domain': 'bing.com', 'favicon': 'https://f.start.me/bing.com'},
                {'title': 'Runway', 'url': 'https://runwayml.com/', 'description': 'Generative video tools and motion synthesis', 'domain': 'runwayml.com', 'favicon': 'https://f.start.me/runwayml.com'},
                {'title': 'Luma Dream Machine', 'url': 'https://lumalabs.ai/dream-machine', 'description': 'Realistic video generation from text and imagery', 'domain': 'lumalabs.ai', 'favicon': 'https://f.start.me/lumalabs.ai'},
                {'title': 'Kling AI', 'url': 'https://klingai.com/', 'description': 'AI video generator with cinematic motion', 'domain': 'klingai.com', 'favicon': 'https://f.start.me/klingai.com'},
                {'title': 'Pika', 'url': 'https://pika.art/', 'description': 'Generative video and animation platform', 'domain': 'pika.art', 'favicon': 'https://f.start.me/pika.art'},
                {'title': 'CutItOut', 'url': 'https://cut-it-out.vercel.app/', 'description': 'Fast AI background remover tool', 'domain': 'vercel.app', 'favicon': 'https://f.start.me/cut-it-out.vercel.app'},
                {'title': 'Magnific', 'url': 'https://magnific.ai/', 'description': 'High-resolution image upscaling and detail enhancer', 'domain': 'magnific.ai', 'favicon': 'https://f.start.me/magnific.ai'},
                {'title': 'Krea', 'url': 'https://www.krea.ai/', 'description': 'Real-time drawing canvas and visual enhancer', 'domain': 'krea.ai', 'favicon': 'https://f.start.me/krea.ai'},
                {'title': 'Ideogram', 'url': 'https://ideogram.ai/', 'description': 'Image generator with typography and text rendering', 'domain': 'ideogram.ai', 'favicon': 'https://f.start.me/ideogram.ai'}
            ]
        },
        {
            'id': 9006,
            'title': 'AI VOICE & AUDIO',
            'type': 'urllist',
            'group': 'ai_hub',
            'icon': 'mic',
            'color': '#3b82f6',
            'links': [
                {'title': 'ElevenLabs', 'url': 'https://elevenlabs.io/', 'description': 'Natural voice generation and speech synthesis', 'domain': 'elevenlabs.io', 'favicon': 'https://f.start.me/elevenlabs.io'},
                {'title': 'Suno', 'url': 'https://suno.com/', 'description': 'Generate songs and audio from text prompts', 'domain': 'suno.com', 'favicon': 'https://f.start.me/suno.com'},
                {'title': 'Udio', 'url': 'https://www.udio.com/', 'description': 'Music synthesis and composition engine', 'domain': 'udio.com', 'favicon': 'https://f.start.me/udio.com'},
                {'title': 'OpenAI Whisper', 'url': 'https://github.com/openai/whisper', 'description': 'Open-source speech recognition and transcription', 'domain': 'github.com', 'favicon': 'https://f.start.me/github.com'},
                {'title': 'HeyGen', 'url': 'https://www.heygen.com/', 'description': 'AI video avatar and lip-sync platform', 'domain': 'heygen.com', 'favicon': 'https://f.start.me/heygen.com'},
                {'title': 'Play.ht', 'url': 'https://play.ht/', 'description': 'Realistic voice cloning and audio generation', 'domain': 'play.ht', 'favicon': 'https://f.start.me/play.ht'},
                {'title': 'Meshy', 'url': 'https://www.meshy.ai/', 'description': 'Text and image to 3D mesh model generator', 'domain': 'meshy.ai', 'favicon': 'https://f.start.me/meshy.ai'}
            ]
        }
    ]

    # Australian OSINT modules
    aus_widgets = [
        {
            'id': 9101,
            'title': '[AUS] CORPORATIONS, ABN & ASIC',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'briefcase',
            'color': '#10b981',
            'links': [
                {'title': 'ABN Lookup (Australian Business Register)', 'url': 'https://abr.business.gov.au/', 'description': 'Search Australian Business Numbers, GST status, business names, and trading entities', 'domain': 'business.gov.au', 'favicon': 'https://f.start.me/business.gov.au'},
                {'title': 'ASIC Connect (Company & Business Register)', 'url': 'https://connectonline.asic.gov.au/', 'description': 'Search Australian company directors, registered office, ACN, and document filings', 'domain': 'asic.gov.au', 'favicon': 'https://f.start.me/asic.gov.au'},
                {'title': 'AFSA Bankruptcy Register (NPII)', 'url': 'https://www.afsa.gov.au/', 'description': 'National Personal Insolvency Index - check bankruptcy and insolvency records in Australia', 'domain': 'afsa.gov.au', 'favicon': 'https://f.start.me/afsa.gov.au'},
                {'title': 'ASX Company Announcements & Filings', 'url': 'https://www.asx.com.au/markets/trade-our-cash-market/announcements', 'description': 'Live disclosures, financial reports, and executive holdings for Australian listed companies', 'domain': 'asx.com.au', 'favicon': 'https://f.start.me/asx.com.au'},
                {'title': 'IP Australia (Trade Marks Search - ATMOSS)', 'url': 'https://search.ipaustralia.gov.au/trademarks/search/quick', 'description': 'Search registered Australian trade marks, patent holders, and commercial IP owners', 'domain': 'ipaustralia.gov.au', 'favicon': 'https://f.start.me/ipaustralia.gov.au'},
                {'title': 'ACNC (Australian Charities Register)', 'url': 'https://www.acnc.gov.au/charity/charities', 'description': 'Search registered charities, board members, financial reports, and non-profits', 'domain': 'acnc.gov.au', 'favicon': 'https://f.start.me/acnc.gov.au'},
                {'title': 'CreditorWatch Commercial Credit Reports', 'url': 'https://creditorwatch.com.au/', 'description': 'Credit history, court judgments, and cross-directorship alerts for Australian businesses', 'domain': 'creditorwatch.com.au', 'favicon': 'https://f.start.me/creditorwatch.com.au'},
                {'title': 'Dun & Bradstreet Australia / Illion', 'url': 'https://www.illion.com.au/', 'description': 'Australian commercial credit intelligence and company directory', 'domain': 'illion.com.au', 'favicon': 'https://f.start.me/illion.com.au'}
            ]
        },
        {
            'id': 9102,
            'title': '[AUS] GOVERNMENT, LEGISLATION & DATA',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'landmark',
            'color': '#06b6d4',
            'links': [
                {'title': 'Federal Register of Legislation', 'url': 'https://www.legislation.gov.au/', 'description': 'Complete repository of Australian Commonwealth Acts, Regulations, and Gazettes', 'domain': 'legislation.gov.au', 'favicon': 'https://f.start.me/legislation.gov.au'},
                {'title': 'data.gov.au (Australian Open Data)', 'url': 'https://data.gov.au/', 'description': 'Central portal for public datasets published by Australian government agencies', 'domain': 'data.gov.au', 'favicon': 'https://f.start.me/data.gov.au'},
                {'title': 'Trove (National Library of Australia)', 'url': 'https://trove.nla.gov.au/', 'description': 'Digitized historic Australian newspapers (1803-present), gazettes, photos, and archives', 'domain': 'trove.nla.gov.au', 'favicon': 'https://f.start.me/nla.gov.au'},
                {'title': 'National Archives of Australia (RecordSearch)', 'url': 'https://recordsearch.naa.gov.au/', 'description': 'Search federal government files, immigration passenger lists, security dossiers, and defense records', 'domain': 'naa.gov.au', 'favicon': 'https://f.start.me/naa.gov.au'},
                {'title': 'AusTender (Government Procurement Contracts)', 'url': 'https://www.tenders.gov.au/', 'description': 'All Commonwealth procurement contracts, tender notices, and supplier expenditure', 'domain': 'tenders.gov.au', 'favicon': 'https://f.start.me/tenders.gov.au'},
                {'title': 'Australian Parliament House (APH Directory)', 'url': 'https://www.aph.gov.au/Senators_and_Members', 'description': 'Directory of Senators, MPs, parliamentary declarations, and Hansard transcripts', 'domain': 'aph.gov.au', 'favicon': 'https://f.start.me/aph.gov.au'},
                {'title': 'Australian Bureau of Statistics (ABS Data)', 'url': 'https://www.abs.gov.au/', 'description': 'Census data, regional population profiles, economic indicators, and trade statistics', 'domain': 'abs.gov.au', 'favicon': 'https://f.start.me/abs.gov.au'},
                {'title': 'Transparency Portal (Australian Gov Reports)', 'url': 'https://www.transparency.gov.au/', 'description': 'Annual reports and performance data across Australian government bodies', 'domain': 'transparency.gov.au', 'favicon': 'https://f.start.me/transparency.gov.au'}
            ]
        },
        {
            'id': 9103,
            'title': '[AUS] POLICE, COURTS & LAW ENFORCEMENT',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'shield',
            'color': '#f43f5e',
            'links': [
                {'title': 'Australian Federal Police (AFP)', 'url': 'https://www.afp.gov.au/', 'description': 'National policing, wanted persons, cybercrime alerts, and federal investigations', 'domain': 'afp.gov.au', 'favicon': 'https://f.start.me/afp.gov.au'},
                {'title': 'AusLII (Australasian Legal Information Institute)', 'url': 'https://www.austlii.edu.au/', 'description': 'High Court, Federal Court, Supreme Court judgments and legislation database', 'domain': 'austlii.edu.au', 'favicon': 'https://f.start.me/austlii.edu.au'},
                {'title': 'Crime Stoppers Australia', 'url': 'https://crimestoppers.com.au/', 'description': 'National unsolved crime appeals, fugitive lists, and anonymous reporting', 'domain': 'crimestoppers.com.au', 'favicon': 'https://f.start.me/crimestoppers.com.au'},
                {'title': 'National Missing Persons Coordination Centre', 'url': 'https://www.missingpersons.gov.au/', 'description': 'Australian official missing persons register and unsolved profiles', 'domain': 'missingpersons.gov.au', 'favicon': 'https://f.start.me/missingpersons.gov.au'},
                {'title': 'NSW Police Force Wanted & News', 'url': 'https://www.police.nsw.gov.au/', 'description': 'NSW Police media releases, wanted persons, and incident reports', 'domain': 'police.nsw.gov.au', 'favicon': 'https://f.start.me/police.nsw.gov.au'},
                {'title': 'Victoria Police News & Wanted', 'url': 'https://www.police.vic.gov.au/', 'description': 'VicPol incident reports, crime appeals, and public notices', 'domain': 'police.vic.gov.au', 'favicon': 'https://f.start.me/police.vic.gov.au'},
                {'title': 'Queensland Police Service (QPS News)', 'url': 'https://mypolice.qld.gov.au/', 'description': 'Queensland Police news, stolen vehicle alerts, and public appeals', 'domain': 'police.qld.gov.au', 'favicon': 'https://f.start.me/police.qld.gov.au'},
                {'title': 'Western Australia Police Force', 'url': 'https://www.police.wa.gov.au/', 'description': 'WA Police crime alerts, wanted persons, and court listings', 'domain': 'police.wa.gov.au', 'favicon': 'https://f.start.me/police.wa.gov.au'},
                {'title': 'ACIC (Criminal Intelligence Commission)', 'url': 'https://www.acic.gov.au/', 'description': 'Australia national criminal intelligence agency and illicit market reports', 'domain': 'acic.gov.au', 'favicon': 'https://f.start.me/acic.gov.au'},
                {'title': 'NSW Caselaw Judgments', 'url': 'https://www.caselaw.nsw.gov.au/', 'description': 'Judgments and decisions from NSW Courts, Tribunals, and Coroner Court', 'domain': 'caselaw.nsw.gov.au', 'favicon': 'https://f.start.me/caselaw.nsw.gov.au'}
            ]
        },
        {
            'id': 9104,
            'title': '[AUS] REAL ESTATE, LAND & CADASTRE',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'map-pin',
            'color': '#f59e0b',
            'links': [
                {'title': 'Realestate.com.au Property Search', 'url': 'https://www.realestate.com.au/', 'description': 'Search Australian residential, commercial property histories, floorplans, and sales', 'domain': 'realestate.com.au', 'favicon': 'https://f.start.me/realestate.com.au'},
                {'title': 'Domain.com.au Property Records', 'url': 'https://www.domain.com.au/', 'description': 'Property price estimates, sold histories, zoning, and auction results in Australia', 'domain': 'domain.com.au', 'favicon': 'https://f.start.me/domain.com.au'},
                {'title': 'NSW SIX Maps (Spatial Information Exchange)', 'url': 'https://maps.six.nsw.gov.au/', 'description': 'NSW high-res cadastral mapping, property lot/DP boundaries, and historical aerial photos', 'domain': 'six.nsw.gov.au', 'favicon': 'https://f.start.me/nsw.gov.au'},
                {'title': 'VicPlan (Victoria Planning & Land Zones)', 'url': 'https://mapshare.vic.gov.au/vicplan/', 'description': 'Victorian property boundaries, planning zones, overlays, and council permits', 'domain': 'mapshare.vic.gov.au', 'favicon': 'https://f.start.me/vic.gov.au'},
                {'title': 'Queensland Globe (Cadastre & Imagery)', 'url': 'https://qldglobe.information.qld.gov.au/', 'description': 'Interactive satellite imagery, land parcel boundaries, topography, and property data for QLD', 'domain': 'information.qld.gov.au', 'favicon': 'https://f.start.me/qld.gov.au'},
                {'title': 'Geoscience Australia NationalMap', 'url': 'https://nationalmap.gov.au/', 'description': 'National Australian geospatial data, infrastructure, satellite imagery, and environmental layers', 'domain': 'nationalmap.gov.au', 'favicon': 'https://f.start.me/nationalmap.gov.au'},
                {'title': 'Landgate WA Map Viewer', 'url': 'https://www.landgate.wa.gov.au/', 'description': 'Western Australia property certificates, titles, surveys, and spatial data', 'domain': 'landgate.wa.gov.au', 'favicon': 'https://f.start.me/landgate.wa.gov.au'},
                {'title': 'LocationSA Map Viewer', 'url': 'https://location.sa.gov.au/viewer/', 'description': 'South Australian spatial data, land titles, and infrastructure map viewer', 'domain': 'location.sa.gov.au', 'favicon': 'https://f.start.me/sa.gov.au'},
                {'title': 'theLIST LISTmap (Tasmania)', 'url': 'https://theLIST.tas.gov.au/', 'description': 'Tasmanian land titles, cadastral parcels, planning zones, and property spatial data', 'domain': 'thelist.tas.gov.au', 'favicon': 'https://f.start.me/thelist.tas.gov.au'},
                {'title': 'NR Maps (Northern Territory)', 'url': 'https://nrmaps.nt.gov.au/nrmaps.html', 'description': 'Northern Territory land parcels, tenure, pastoral leases, and natural resource map layers', 'domain': 'nrmaps.nt.gov.au', 'favicon': 'https://f.start.me/nrmaps.nt.gov.au'}
            ]
        },
        {
            'id': 9105,
            'title': '[AUS] PUBLIC RECORDS, ELECTORAL & OBITUARIES',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'book-open',
            'color': '#8b5cf6',
            'links': [
                {'title': 'AEC (Australian Electoral Commission)', 'url': 'https://check.aec.gov.au/', 'description': 'Verify voter enrolment status, electorate boundaries, and political donation disclosures', 'domain': 'aec.gov.au', 'favicon': 'https://f.start.me/aec.gov.au'},
                {'title': 'VEC Disclosed Donations (VIC)', 'url': 'https://disclosures.vec.vic.gov.au/', 'description': 'Victorian Electoral Commission public register of disclosed political donations', 'domain': 'vec.vic.gov.au', 'favicon': 'https://f.start.me/vec.vic.gov.au'},
                {'title': 'WA Electoral Commission Funding & Disclosure', 'url': 'https://www.elections.wa.gov.au/candidates-and-parties/funding-and-disclosure', 'description': 'Western Australian political donation and electoral funding disclosure returns', 'domain': 'elections.wa.gov.au', 'favicon': 'https://f.start.me/elections.wa.gov.au'},
                {'title': 'ECSA Funding & Disclosure (SA)', 'url': 'https://www.ecsa.sa.gov.au/parties-and-candidates/funding-and-disclosure-all-participants', 'description': 'South Australian Electoral Commission register of political funding and donation disclosures', 'domain': 'ecsa.sa.gov.au', 'favicon': 'https://f.start.me/ecsa.sa.gov.au'},
                {'title': 'TEC Disclosure & Funding (TAS)', 'url': 'https://www.tec.tas.gov.au/disclosure-and-funding/', 'description': 'Tasmanian Electoral Commission political donation and electoral expenditure disclosures', 'domain': 'tec.tas.gov.au', 'favicon': 'https://f.start.me/tec.tas.gov.au'},
                {'title': 'NSW Registry of Births, Deaths & Marriages', 'url': 'https://bdm.nsw.gov.au/', 'description': 'Official NSW civil registry for birth, death, marriage and change of name certificates', 'domain': 'bdm.nsw.gov.au', 'favicon': 'https://f.start.me/bdm.nsw.gov.au'},
                {'title': 'Victoria Births, Deaths & Marriages', 'url': 'https://www.bdm.vic.gov.au/', 'description': 'Official Victorian civil registry for birth, death, marriage and relationship records', 'domain': 'bdm.vic.gov.au', 'favicon': 'https://f.start.me/bdm.vic.gov.au'},
                {'title': 'Queensland Births, Deaths & Marriages', 'url': 'https://www.qld.gov.au/law/births-deaths-marriages-and-divorces', 'description': 'Official Queensland civil registry for birth, death, marriage and divorce records', 'domain': 'qld.gov.au', 'favicon': 'https://f.start.me/qld.gov.au'},
                {'title': 'WA Registry of Births, Deaths & Marriages', 'url': 'https://www.wa.gov.au/organisation/department-of-justice/the-registry-of-births-deaths-and-marriages', 'description': 'Official Western Australian civil registry for birth, death, marriage and name change records', 'domain': 'wa.gov.au', 'favicon': 'https://f.start.me/wa.gov.au'},
                {'title': 'SA Births, Deaths & Marriages (CBS)', 'url': 'https://www.cbs.sa.gov.au/births,-deaths-and-marriages', 'description': 'Official South Australian civil registry for birth, death, marriage and relationship records', 'domain': 'cbs.sa.gov.au', 'favicon': 'https://f.start.me/cbs.sa.gov.au'},
                {'title': 'Tasmania Births, Deaths & Marriages', 'url': 'https://www.justice.tas.gov.au/bdm/home', 'description': 'Official Tasmanian civil registry for birth, death, marriage and change of name records', 'domain': 'justice.tas.gov.au', 'favicon': 'https://f.start.me/justice.tas.gov.au'},
                {'title': 'NT Births, Deaths & Marriages', 'url': 'https://nt.gov.au/law/bdm/search-births-deaths-and-marriages-records', 'description': 'Official Northern Territory civil registry search and certificate application service', 'domain': 'nt.gov.au', 'favicon': 'https://f.start.me/nt.gov.au'},
                {'title': 'ACT Births, Relationships & Deaths (Access Canberra)', 'url': 'https://www.accesscanberra.act.gov.au/births-relationships-and-deaths', 'description': 'Official ACT civil registry for birth, relationship and death records via Access Canberra', 'domain': 'accesscanberra.act.gov.au', 'favicon': 'https://f.start.me/accesscanberra.act.gov.au'},
                {'title': 'Ryerson Index (Australian Death & Funeral Notices)', 'url': 'https://www.ryersonindex.org/', 'description': 'Database of 8.5M+ death and funeral notices indexed from Australian newspapers', 'domain': 'ryersonindex.org', 'favicon': 'https://f.start.me/ryersonindex.org'},
                {'title': 'White Pages Australia', 'url': 'https://www.whitepages.com.au/', 'description': 'Australian residential phone numbers, addresses, and individual directory lookup', 'domain': 'whitepages.com.au', 'favicon': 'https://f.start.me/whitepages.com.au'},
                {'title': 'Yellow Pages Australia', 'url': 'https://www.yellowpages.com.au/', 'description': 'Australian commercial telephone directory, business locations, and contacts', 'domain': 'yellowpages.com.au', 'favicon': 'https://f.start.me/yellowpages.com.au'},
                {'title': 'Findmypast Australia & New Zealand', 'url': 'https://www.findmypast.com.au/', 'description': 'Australian electoral rolls, census records, convict lists, and military service files', 'domain': 'findmypast.com.au', 'favicon': 'https://f.start.me/findmypast.com.au'},
                {'title': 'Ancestry Australia Archives', 'url': 'https://www.ancestry.com.au/', 'description': 'Australian historical records, bdm indexes, passenger manifests, and directories', 'domain': 'ancestry.com.au', 'favicon': 'https://f.start.me/ancestry.com.au'},
                {'title': 'HeavenAddress Australia Memorials', 'url': 'https://www.heavenaddress.com/', 'description': 'Australian online cemetery memorials, obituaries, and tribute records', 'domain': 'heavenaddress.com', 'favicon': 'https://f.start.me/heavenaddress.com'}
            ]
        },
        {
            'id': 9106,
            'title': '[AUS] TRANSPORT, VEHICLE REGO & MARITIME',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'truck',
            'color': '#3b82f6',
            'links': [
                {'title': 'PPSR (Personal Property Securities Register)', 'url': 'https://www.ppsr.gov.au/', 'description': 'Search vehicle VIN/chassis numbers in Australia for financial security interests and written-off status', 'domain': 'ppsr.gov.au', 'favicon': 'https://f.start.me/ppsr.gov.au'},
                {'title': 'Service NSW Vehicle Registration Check', 'url': 'https://www.service.nsw.gov.au/transaction/check-a-vehicle-registration', 'description': 'Free NSW license plate rego status, CTP insurer, and expiry lookup', 'domain': 'service.nsw.gov.au', 'favicon': 'https://f.start.me/nsw.gov.au'},
                {'title': 'VicRoads Registration Check', 'url': 'https://www.vicroads.vic.gov.au/registration/buy-sell-or-transfer-a-vehicle/check-vehicle-registration/vehicle-registration-enquiry', 'description': 'Free Victorian vehicle registration and VIN verification tool', 'domain': 'vicroads.vic.gov.au', 'favicon': 'https://f.start.me/vic.gov.au'},
                {'title': 'QLD Transport Vehicle Registration Check', 'url': 'https://www.service.transport.qld.gov.au/checkrego/application/VehicleSearch.xhtml', 'description': 'Check Queensland registration status by plate or VIN', 'domain': 'service.transport.qld.gov.au', 'favicon': 'https://f.start.me/qld.gov.au'},
                {'title': 'CASA (Civil Aviation Safety Authority Register)', 'url': 'https://www.casa.gov.au/aircraft/register-aircraft/civil-aircraft-register', 'description': 'Search all registered VH- Australian aircraft, owners, and operators', 'domain': 'casa.gov.au', 'favicon': 'https://f.start.me/casa.gov.au'},
                {'title': 'AMSA (Australian Maritime Safety Authority)', 'url': 'https://www.amsa.gov.au/vessels-operators/ship-registration/australian-register-ships', 'description': 'Australian General Shipping Register, commercial vessels, and maritime safety notices', 'domain': 'amsa.gov.au', 'favicon': 'https://f.start.me/amsa.gov.au'}
            ]
        },
        {
            'id': 9107,
            'title': '[AUS] NEWS, MEDIA & STREAMING',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'newspaper',
            'color': '#f97316',
            'links': [
                {'title': 'news.com.au', 'url': 'https://www.news.com.au/', 'description': "Australia's most-read commercial news site: national, world, sport & entertainment", 'domain': 'news.com.au', 'favicon': 'https://f.start.me/news.com.au'},
                {'title': '9News', 'url': 'https://www.9news.com.au/', 'description': 'Nine Network live news, investigations and breaking stories', 'domain': '9news.com.au', 'favicon': 'https://f.start.me/9news.com.au'},
                {'title': '7NEWS Australia', 'url': 'https://7news.com.au/', 'description': 'Seven Network national news and current affairs', 'domain': '7news.com.au', 'favicon': 'https://f.start.me/7news.com.au'},
                {'title': 'The Age', 'url': 'https://www.theage.com.au/', 'description': 'Melbourne & Victorian daily newspaper published by Nine', 'domain': 'theage.com.au', 'favicon': 'https://f.start.me/theage.com.au'},
                {'title': 'Sydney Morning Herald', 'url': 'https://www.smh.com.au/', 'description': 'Sydney & NSW daily newspaper published by Nine', 'domain': 'smh.com.au', 'favicon': 'https://f.start.me/smh.com.au'},
                {'title': 'The Australian', 'url': 'https://www.theaustralian.com.au/', 'description': 'National broadsheet published by News Corp Australia', 'domain': 'theaustralian.com.au', 'favicon': 'https://f.start.me/theaustralian.com.au'},
                {'title': 'Crikey', 'url': 'https://www.crikey.com.au/', 'description': 'Independent Australian political and media commentary', 'domain': 'crikey.com.au', 'favicon': 'https://f.start.me/crikey.com.au'},
                {'title': 'The Conversation (AU)', 'url': 'https://theconversation.com/au', 'description': 'Academic expert analysis on Australian issues', 'domain': 'theconversation.com', 'favicon': 'https://f.start.me/theconversation.com'},
                {'title': 'ABC iview', 'url': 'https://iview.abc.net.au/', 'description': 'ABC catch-up TV streaming, live channels, news and documentaries', 'domain': 'iview.abc.net.au', 'favicon': 'https://f.start.me/abc.net.au'},
                {'title': 'SBS On Demand', 'url': 'https://www.sbs.com.au/ondemand', 'description': 'Free multicultural and international streaming by SBS', 'domain': 'sbs.com.au', 'favicon': 'https://f.start.me/sbs.com.au'},
                {'title': '10 Play', 'url': 'https://10play.com.au/', 'description': 'Network 10 catch-up streaming and live TV', 'domain': '10play.com.au', 'favicon': 'https://f.start.me/10play.com.au'},
                {'title': 'NITV (National Indigenous Television)', 'url': 'https://www.sbs.com.au/nitv', 'description': 'First Nations news, documentaries and programs', 'domain': 'sbs.com.au', 'favicon': 'https://f.start.me/sbs.com.au'},
                {'title': 'Media Watch (ABC)', 'url': 'https://www.abc.net.au/mediawatch', 'description': "ABC's weekly media accountability and criticism program", 'domain': 'abc.net.au', 'favicon': 'https://f.start.me/abc.net.au'},
                {'title': 'ACMA (Media & Communications Regulator)', 'url': 'https://www.acma.gov.au/', 'description': 'Australian media, broadcasting, telecom and spectrum regulator', 'domain': 'acma.gov.au', 'favicon': 'https://f.start.me/acma.gov.au'}
            ]
        },
        {
            'id': 9108,
            'title': '[AUS] GOVERNMENT SERVICES & MYGOV',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'id-badge',
            'color': '#10b981',
            'links': [
                {'title': 'myGov', 'url': 'https://www.my.gov.au/', 'description': 'Single sign-on portal for ATO, Medicare, Centrelink and more', 'domain': 'my.gov.au', 'favicon': 'https://f.start.me/my.gov.au'},
                {'title': 'Services Australia', 'url': 'https://www.servicesaustralia.gov.au/', 'description': 'Centrelink, Medicare, Child Support and NDIS services', 'domain': 'servicesaustralia.gov.au', 'favicon': 'https://f.start.me/servicesaustralia.gov.au'},
                {'title': 'Australian Taxation Office (ATO)', 'url': 'https://www.ato.gov.au/', 'description': 'Tax, ABN, superannuation, lodgment and payment obligations', 'domain': 'ato.gov.au', 'favicon': 'https://f.start.me/ato.gov.au'},
                {'title': 'Medicare (Services Australia)', 'url': 'https://www.servicesaustralia.gov.au/medicare', 'description': 'Medicare enrolment, claims, and health services', 'domain': 'servicesaustralia.gov.au', 'favicon': 'https://f.start.me/servicesaustralia.gov.au'},
                {'title': 'Centrelink (Services Australia)', 'url': 'https://www.servicesaustralia.gov.au/centrelink', 'description': 'Payments, income support and concession services', 'domain': 'servicesaustralia.gov.au', 'favicon': 'https://f.start.me/servicesaustralia.gov.au'},
                {'title': 'eSafety Commissioner', 'url': 'https://www.esafety.gov.au/', 'description': 'Australian online safety regulator, complaints and takedowns', 'domain': 'esafety.gov.au', 'favicon': 'https://f.start.me/esafety.gov.au'},
                {'title': 'Fair Work Ombudsman', 'url': 'https://www.fairwork.gov.au/', 'description': 'Workplace rights, employer obligations and disputes', 'domain': 'fairwork.gov.au', 'favicon': 'https://f.start.me/fairwork.gov.au'},
                {'title': 'Moneysmart (ASIC)', 'url': 'https://moneysmart.gov.au/', 'description': 'ASIC financial literacy and guidance portal', 'domain': 'moneysmart.gov.au', 'favicon': 'https://f.start.me/moneysmart.gov.au'},
                {'title': 'Service NSW', 'url': 'https://www.service.nsw.gov.au/', 'description': 'NSW government services portal: rego, licences, fines & records', 'domain': 'service.nsw.gov.au', 'favicon': 'https://f.start.me/service.nsw.gov.au'},
                {'title': 'Service Victoria', 'url': 'https://www.service.vic.gov.au/', 'description': 'Victorian government services portal', 'domain': 'service.vic.gov.au', 'favicon': 'https://f.start.me/service.vic.gov.au'},
                {'title': 'Queensland Government', 'url': 'https://www.qld.gov.au/', 'description': 'Queensland government services and information', 'domain': 'qld.gov.au', 'favicon': 'https://f.start.me/qld.gov.au'},
                {'title': 'My Health Record', 'url': 'https://www.myhealthrecord.gov.au/', 'description': 'National online health records system', 'domain': 'myhealthrecord.gov.au', 'favicon': 'https://f.start.me/myhealthrecord.gov.au'},
                {'title': 'NDIS (National Disability Insurance Scheme)', 'url': 'https://www.ndis.gov.au/', 'description': 'NDIS participant and provider information', 'domain': 'ndis.gov.au', 'favicon': 'https://f.start.me/ndis.gov.au'}
            ]
        },
        {
            'id': 9109,
            'title': '[AUS] TELCO, POSTAL & ADDRESS',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'phone',
            'color': '#06b6d4',
            'links': [
                {'title': 'Australia Post', 'url': 'https://auspost.com.au/', 'description': 'Postal services, PO boxes, postcodes and address redirection', 'domain': 'auspost.com.au', 'favicon': 'https://f.start.me/auspost.com.au'},
                {'title': 'Australia Post Track & Trace', 'url': 'https://auspost.com.au/mypost/track', 'description': 'Track Australian domestic and international parcels', 'domain': 'auspost.com.au', 'favicon': 'https://f.start.me/auspost.com.au'},
                {'title': 'G-NAF Geocoded Address Data', 'url': 'https://data.gov.au/dataset/geocoded-national-address-file-g-naf', 'description': 'National geocoded address file (G-NAF) for address verification and geocoding', 'domain': 'data.gov.au', 'favicon': 'https://f.start.me/data.gov.au'},
                {'title': 'NBN Co Address Lookup', 'url': 'https://www.nbnco.com.au/', 'description': 'National Broadband Network rollout, address and technology lookup', 'domain': 'nbnco.com.au', 'favicon': 'https://f.start.me/nbnco.com.au'},
                {'title': 'Telstra', 'url': 'https://www.telstra.com.au/', 'description': 'Telstra services, plans and phone number support', 'domain': 'telstra.com.au', 'favicon': 'https://f.start.me/telstra.com.au'},
                {'title': 'Optus', 'url': 'https://www.optus.com.au/', 'description': 'Optus mobile, broadband and business services', 'domain': 'optus.com.au', 'favicon': 'https://f.start.me/optus.com.au'},
                {'title': 'Vodafone Australia', 'url': 'https://www.vodafone.com.au/', 'description': 'Vodafone mobile plans and coverage', 'domain': 'vodafone.com.au', 'favicon': 'https://f.start.me/vodafone.com.au'},
                {'title': 'Geoscape Australia (Address Data)', 'url': 'https://geoscape.com.au/', 'description': 'G-NAF geocoded address data and cadastral products for Australia', 'domain': 'geoscape.com.au', 'favicon': 'https://f.start.me/geoscape.com.au'},
                {'title': 'ACMA Telecommunications', 'url': 'https://www.acma.gov.au/industry/spectrum/radiocomms-licences/radiocomms-licence-numbers', 'description': 'ACMA radiocommunications licence and spectrum information', 'domain': 'acma.gov.au', 'favicon': 'https://f.start.me/acma.gov.au'}
            ]
        },
        {
            'id': 9110,
            'title': '[AUS] EMERGENCY, WEATHER & PUBLIC SAFETY',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'cloud-lightning',
            'color': '#f59e0b',
            'links': [
                {'title': 'BOM Climate Data Online', 'url': 'http://www.bom.gov.au/climate/data/', 'description': 'Historical Australian weather observations and climate records', 'domain': 'bom.gov.au', 'favicon': 'https://f.start.me/bom.gov.au'},
                {'title': 'BOM Weather Radar Network', 'url': 'http://www.bom.gov.au/australia/radar/', 'description': 'National live rainfall and wind radar loops', 'domain': 'bom.gov.au', 'favicon': 'https://f.start.me/bom.gov.au'},
                {'title': 'BOM Severe Weather Warnings', 'url': 'http://www.bom.gov.au/australia/warnings/', 'description': 'Current cyclone, flood, fire weather and severe storm warnings', 'domain': 'bom.gov.au', 'favicon': 'https://f.start.me/bom.gov.au'},
                {'title': 'Fire Danger Ratings (AFAC)', 'url': 'https://www.afac.com.au/', 'description': 'Australian Fire Authorities Council — national fire danger ratings', 'domain': 'afac.com.au', 'favicon': 'https://f.start.me/afac.com.au'},
                {'title': 'NSW RFS Fires Near Me', 'url': 'https://www.rfs.nsw.gov.au/fire-information/fires-near-me', 'description': 'Live NSW bushfire incidents and planned burns', 'domain': 'rfs.nsw.gov.au', 'favicon': 'https://f.start.me/rfs.nsw.gov.au'},
                {'title': 'VicEmergency', 'url': 'https://www.emergency.vic.gov.au/', 'description': 'Victorian fire, flood, storm and incident warnings', 'domain': 'emergency.vic.gov.au', 'favicon': 'https://f.start.me/emergency.vic.gov.au'},
                {'title': 'Queensland Fire & Emergency Services', 'url': 'https://www.qfes.qld.gov.au/', 'description': 'QLD bushfire, incident and hazard alerts', 'domain': 'qfes.qld.gov.au', 'favicon': 'https://f.start.me/qfes.qld.gov.au'},
                {'title': 'Emergency WA (DFES)', 'url': 'https://www.emergency.wa.gov.au/', 'description': 'Western Australian incident alerts and warnings', 'domain': 'emergency.wa.gov.au', 'favicon': 'https://f.start.me/emergency.wa.gov.au'},
                {'title': 'SA Country Fire Service', 'url': 'https://www.cfs.sa.gov.au/', 'description': 'South Australian CFS incident warnings', 'domain': 'cfs.sa.gov.au', 'favicon': 'https://f.start.me/cfs.sa.gov.au'},
                {'title': 'Secure NT', 'url': 'https://securent.nt.gov.au/', 'description': 'Northern Territory bushfire, flood, cyclone and storm warnings from BOM, NTFRS and NTES', 'domain': 'securent.nt.gov.au', 'favicon': 'https://f.start.me/securent.nt.gov.au'},
                {'title': 'TAS ALERT', 'url': 'https://alert.tas.gov.au/', 'description': 'Tasmanian emergency warnings and alerts', 'domain': 'alert.tas.gov.au', 'favicon': 'https://f.start.me/alert.tas.gov.au'},
                {'title': 'ACT ESA', 'url': 'https://esa.act.gov.au/', 'description': 'ACT Emergency Services Agency warnings and incidents', 'domain': 'esa.act.gov.au', 'favicon': 'https://f.start.me/esa.act.gov.au'},
                {'title': 'Emergency Alert (National)', 'url': 'https://www.emergencyalert.gov.au/', 'description': 'National telephone-based emergency warning system', 'domain': 'emergencyalert.gov.au', 'favicon': 'https://f.start.me/emergencyalert.gov.au'},
                {'title': 'ABC Emergency', 'url': 'https://www.abc.net.au/news/emergency', 'description': 'ABC emergency broadcast coverage and alert aggregator', 'domain': 'abc.net.au', 'favicon': 'https://f.start.me/abc.net.au'}
            ]
        },
        {
            'id': 9111,
            'title': '[AUS] DEFENCE, BORDERS & NATIONAL SECURITY',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'shield',
            'color': '#f43f5e',
            'links': [
                {'title': 'Department of Defence', 'url': 'https://www.defence.gov.au/', 'description': 'Australian Defence Force structure, projects and capability', 'domain': 'defence.gov.au', 'favicon': 'https://f.start.me/defence.gov.au'},
                {'title': 'Australian Signals Directorate (ASD)', 'url': 'https://www.asd.gov.au/', 'description': 'Signals intelligence and offensive/defensive cyber agency', 'domain': 'asd.gov.au', 'favicon': 'https://f.start.me/asd.gov.au'},
                {'title': 'ASIO', 'url': 'https://www.asio.gov.au/', 'description': 'Australian Security Intelligence Organisation public statements', 'domain': 'asio.gov.au', 'favicon': 'https://f.start.me/asio.gov.au'},
                {'title': 'Australian Border Force', 'url': 'https://www.abf.gov.au/', 'description': 'Border control, customs and visa enforcement', 'domain': 'abf.gov.au', 'favicon': 'https://f.start.me/abf.gov.au'},
                {'title': 'Department of Home Affairs', 'url': 'https://www.homeaffairs.gov.au/', 'description': 'Immigration, visas, citizenship and national security policy', 'domain': 'homeaffairs.gov.au', 'favicon': 'https://f.start.me/homeaffairs.gov.au'},
                {'title': 'AUSTRAC', 'url': 'https://www.austrac.gov.au/', 'description': 'Financial intelligence and AML/CTF regulator', 'domain': 'austrac.gov.au', 'favicon': 'https://f.start.me/austrac.gov.au'},
                {'title': 'DFAT Smartraveller', 'url': 'https://www.smartraveller.gov.au/', 'description': 'Official travel advisories and consular assistance', 'domain': 'smartraveller.gov.au', 'favicon': 'https://f.start.me/smartraveller.gov.au'},
                {'title': 'National Emergency Management Agency (NEMA)', 'url': 'https://nema.gov.au/', 'description': 'National disaster and emergency coordination', 'domain': 'nema.gov.au', 'favicon': 'https://f.start.me/nema.gov.au'},
                {'title': 'Office of National Intelligence (ONI)', 'url': 'https://www.oni.gov.au/', 'description': 'Coordination and assessment across Australia intelligence community', 'domain': 'oni.gov.au', 'favicon': 'https://f.start.me/oni.gov.au'}
            ]
        },
        {
            'id': 9112,
            'title': '[AUS] SPORT, ARTS & AUSSIE CULTURE',
            'type': 'urllist',
            'group': 'aus_intel',
            'icon': 'trophy',
            'color': '#8b5cf6',
            'links': [
                {'title': 'NRL', 'url': 'https://www.nrl.com/', 'description': 'National Rugby League: teams, draws and results', 'domain': 'nrl.com', 'favicon': 'https://f.start.me/nrl.com'},
                {'title': 'AFL', 'url': 'https://www.afl.com.au/', 'description': 'Australian Football League: teams, fixtures and ladders', 'domain': 'afl.com.au', 'favicon': 'https://f.start.me/afl.com.au'},
                {'title': 'Cricket Australia', 'url': 'https://www.cricket.com.au/', 'description': 'Australian cricket teams, series and scores', 'domain': 'cricket.com.au', 'favicon': 'https://f.start.me/cricket.com.au'},
                {'title': 'Tennis Australia', 'url': 'https://www.tennis.com.au/', 'description': 'Australian tennis, rankings and tournament draws', 'domain': 'tennis.com.au', 'favicon': 'https://f.start.me/tennis.com.au'},
                {'title': 'triple j', 'url': 'https://www.abc.net.au/triplej', 'description': 'ABC youth radio, Unearthed and the Hottest 100', 'domain': 'abc.net.au', 'favicon': 'https://f.start.me/abc.net.au'},
                {'title': 'ABC Listen', 'url': 'https://www.abc.net.au/listen', 'description': 'ABC radio and podcast streaming', 'domain': 'abc.net.au', 'favicon': 'https://f.start.me/abc.net.au'},
                {'title': 'Beachsafe (Surf Life Saving)', 'url': 'https://beachsafe.org.au/', 'description': 'Live Australian beach conditions and patrol status', 'domain': 'beachsafe.org.au', 'favicon': 'https://f.start.me/beachsafe.org.au'},
                {'title': 'National Gallery of Australia', 'url': 'https://nga.gov.au/', 'description': 'National art collection and exhibitions', 'domain': 'nga.gov.au', 'favicon': 'https://f.start.me/nga.gov.au'},
                {'title': 'ACMI', 'url': 'https://www.acmi.net.au/', 'description': 'Australian Centre for the Moving Image', 'domain': 'acmi.net.au', 'favicon': 'https://f.start.me/acmi.net.au'},
                {'title': 'Australian War Memorial', 'url': 'https://www.awm.gov.au/', 'description': 'National military history museum and memorial records', 'domain': 'awm.gov.au', 'favicon': 'https://f.start.me/awm.gov.au'},
                {'title': 'National Museum of Australia', 'url': 'https://www.nma.gov.au/', 'description': 'Australian social history and collections', 'domain': 'nma.gov.au', 'favicon': 'https://f.start.me/nma.gov.au'},
                {'title': 'australia.gov.au', 'url': 'https://www.australia.gov.au/', 'description': 'Official Australian government entry portal', 'domain': 'australia.gov.au', 'favicon': 'https://f.start.me/australia.gov.au'}
            ]
        }
    ]

    # Interactive visual toolkit (new group: visual_tools)
    visual_widgets = [
        {
            'id': 9201,
            'title': 'INTERACTIVE VISUAL TOOLKIT',
            'type': 'urllist',
            'group': 'visual_tools',
            'icon': 'globe',
            'color': '#ec4899',
            'links': [
                {'title': 'Google Earth Timelapse', 'url': 'https://earthengine.google.com/timelapse/', 'description': 'Watch 40 years of Earth change from space in interactive 3D', 'domain': 'earthengine.google.com', 'favicon': 'https://f.start.me/earthengine.google.com'},
                {'title': 'Windy.com', 'url': 'https://www.windy.com/', 'description': 'Global animated weather, wind, waves and air quality maps', 'domain': 'windy.com', 'favicon': 'https://f.start.me/windy.com'},
                {'title': 'Ventusky', 'url': 'https://www.ventusky.com/', 'description': 'Live animated global weather visualization', 'domain': 'ventusky.com', 'favicon': 'https://f.start.me/ventusky.com'},
                {'title': 'Earth Nullschool', 'url': 'https://earth.nullschool.net/', 'description': 'Real-time global wind, ocean and pollution currents', 'domain': 'earth.nullschool.net', 'favicon': 'https://f.start.me/earth.nullschool.net'},
                {'title': 'Zoom Earth', 'url': 'https://zoom.earth/', 'description': 'Live satellite and radar imagery updated every 10 minutes', 'domain': 'zoom.earth', 'favicon': 'https://f.start.me/zoom.earth'},
                {'title': 'NASA Worldview', 'url': 'https://worldview.earthdata.nasa.gov/', 'description': 'NASA satellite imagery explorer with 800+ layers', 'domain': 'worldview.earthdata.nasa.gov', 'favicon': 'https://f.start.me/worldview.earthdata.nasa.gov'},
                {'title': 'Google Arts & Culture', 'url': 'https://artsandculture.google.com/', 'description': 'Zoom into 4K museum artworks and historical artifacts', 'domain': 'artsandculture.google.com', 'favicon': 'https://f.start.me/artsandculture.google.com'},
                {'title': 'Radio Garden', 'url': 'https://radio.garden/', 'description': 'Spin the globe and listen to live radio from anywhere', 'domain': 'radio.garden', 'favicon': 'https://f.start.me/radio.garden'},
                {'title': 'Old Maps Online', 'url': 'https://www.oldmapsonline.org/', 'description': 'Search millions of historical maps by location and era', 'domain': 'oldmapsonline.org', 'favicon': 'https://f.start.me/oldmapsonline.org'},
                {'title': 'SunCalc', 'url': 'https://www.suncalc.org/', 'description': 'Sun position, shadow and golden hour calculator for any location', 'domain': 'suncalc.org', 'favicon': 'https://f.start.me/suncalc.org'},
                {'title': 'Shadowmap', 'url': 'https://shadowmap.org/', 'description': '3D sunlight and shadow simulation for any city', 'domain': 'shadowmap.org', 'favicon': 'https://f.start.me/shadowmap.org'},
                {'title': 'Light Pollution Map', 'url': 'https://www.lightpollutionmap.info/', 'description': 'Dark sky and light pollution visualization', 'domain': 'lightpollutionmap.info', 'favicon': 'https://f.start.me/lightpollutionmap.info'},
                {'title': 'Stellarium Web', 'url': 'https://stellarium-web.org/', 'description': 'Free browser planetarium — explore the night sky', 'domain': 'stellarium-web.org', 'favicon': 'https://f.start.me/stellarium-web.org'},
                {'title': 'GDELT Project', 'url': 'https://www.gdeltproject.org/', 'description': 'Global news event database — hundreds of millions of events', 'domain': 'gdeltproject.org', 'favicon': 'https://f.start.me/gdeltproject.org'},
                {'title': 'Kepler.gl', 'url': 'https://kepler.gl/demo', 'description': 'Massive geospatial datasets visualized in your browser', 'domain': 'kepler.gl', 'favicon': 'https://f.start.me/kepler.gl'},
                {'title': 'Google Mars', 'url': 'https://www.google.com/mars/', 'description': 'Interactive 3D map of the red planet', 'domain': 'google.com', 'favicon': 'https://f.start.me/google.com'}
            ]
        }
    ]

    # Hacker search engines (curated from edoardottt/awesome-hacker-search-engines)
    hacker_widgets = [
        {
            'id': 9202,
            'title': 'HACKER SEARCH: SERVERS & ATTACK SURFACE',
            'type': 'urllist',
            'group': 'cyber_intel',
            'icon': 'server',
            'color': '#f43f5e',
            'links': [
                {'title': 'Quake (360 Cyberspace Map)', 'url': 'https://quake.360.net/quake/#/index', 'description': 'Cyberspace surveying and mapping system by 360', 'domain': 'quake.360.net', 'favicon': 'https://f.start.me/quake.360.net'},
                {'title': 'Hunter (Internet Asset Search)', 'url': 'https://hunter.how/', 'description': 'Internet search engine for security researchers', 'domain': 'hunter.how', 'favicon': 'https://f.start.me/hunter.how'},
                {'title': 'ODIN', 'url': 'https://getodin.com/', 'description': 'One of the most powerful search engines for scanned internet assets', 'domain': 'getodin.com', 'favicon': 'https://f.start.me/getodin.com'},
                {'title': 'Modat Magnify', 'url': 'https://magnify.modat.io/', 'description': 'The largest internet device DNA dataset available', 'domain': 'magnify.modat.io', 'favicon': 'https://f.start.me/magnify.modat.io'},
                {'title': 'Natlas', 'url': 'https://natlas.io/', 'description': 'Scaling network scanning search engine', 'domain': 'natlas.io', 'favicon': 'https://f.start.me/natlas.io'},
                {'title': 'BinaryEdge', 'url': 'https://www.binaryedge.io/', 'description': 'Continuous internet-wide scanning data and attack surface', 'domain': 'binaryedge.io', 'favicon': 'https://f.start.me/binaryedge.io'},
                {'title': 'FullHunt', 'url': 'https://fullhunt.io/', 'description': 'Attack surface database of the entire internet', 'domain': 'fullhunt.io', 'favicon': 'https://f.start.me/fullhunt.io'},
                {'title': 'RedHunt Labs', 'url': 'https://redhuntlabs.com/', 'description': 'Discover and monitor your external attack surface, continuously', 'domain': 'redhuntlabs.com', 'favicon': 'https://f.start.me/redhuntlabs.com'},
                {'title': 'NetworksDB', 'url': 'https://networksdb.io/', 'description': 'Public IPv4/IPv6 networks and domains owned by organizations', 'domain': 'networksdb.io', 'favicon': 'https://f.start.me/networksdb.io'},
                {'title': 'ASNlookup', 'url': 'https://asnlookup.com/', 'description': 'Lookup ASN, organization, CIDR and registered IP addresses', 'domain': 'asnlookup.com', 'favicon': 'https://f.start.me/asnlookup.com'},
                {'title': 'BGPview', 'url': 'https://bgpview.io/', 'description': 'Investigate IP addresses, ASNs, IXPs, BGP and prefixes', 'domain': 'bgpview.io', 'favicon': 'https://f.start.me/bgpview.io'},
                {'title': 'bgp.tools', 'url': 'https://bgp.tools/', 'description': 'Browse the internet routing ecosystem', 'domain': 'bgp.tools', 'favicon': 'https://f.start.me/bgp.tools'},
                {'title': 'Cloudflare Radar', 'url': 'https://radar.cloudflare.com/', 'description': 'Global internet traffic, attack and technology trends', 'domain': 'radar.cloudflare.com', 'favicon': 'https://f.start.me/radar.cloudflare.com'},
                {'title': 'Hurricane Electric BGP Toolkit', 'url': 'https://bgp.he.net/', 'description': 'Free ASN, IP and prefix BGP lookups', 'domain': 'bgp.he.net', 'favicon': 'https://f.start.me/bgp.he.net'},
                {'title': 'IPinfo', 'url': 'https://ipinfo.io/', 'description': 'The trusted source for IP address data and geolocation', 'domain': 'ipinfo.io', 'favicon': 'https://f.start.me/ipinfo.io'},
                {'title': 'HackMyIP', 'url': 'https://hackmyip.com/', 'description': 'Free privacy toolkit: IP, DNS, leak tests and more', 'domain': 'hackmyip.com', 'favicon': 'https://f.start.me/hackmyip.com'},
                {'title': 'Awseye', 'url': 'https://awseye.com/', 'description': 'OSINT and recon on publicly accessible AWS data', 'domain': 'awseye.com', 'favicon': 'https://f.start.me/awseye.com'},
                {'title': 'S4E', 'url': 'https://app.s4e.io/', 'description': 'Continuous threat exposure management scans of digital assets', 'domain': 'app.s4e.io', 'favicon': 'https://f.start.me/app.s4e.io'}
            ]
        },
        {
            'id': 9203,
            'title': 'HACKER SEARCH: VULNERABILITIES & EXPLOITS',
            'type': 'urllist',
            'group': 'cyber_intel',
            'icon': 'bug',
            'color': '#f59e0b',
            'links': [
                {'title': 'NIST NVD', 'url': 'https://nvd.nist.gov/vuln/search', 'description': 'US National Vulnerability Database', 'domain': 'nvd.nist.gov', 'favicon': 'https://f.start.me/nvd.nist.gov'},
                {'title': 'MITRE CVE', 'url': 'https://cve.mitre.org/cve/search_cve_list.html', 'description': 'Catalog of publicly disclosed cybersecurity vulnerabilities', 'domain': 'cve.mitre.org', 'favicon': 'https://f.start.me/cve.mitre.org'},
                {'title': 'osv.dev', 'url': 'https://osv.dev/list', 'description': 'Open source vulnerability database by Google', 'domain': 'osv.dev', 'favicon': 'https://f.start.me/osv.dev'},
                {'title': 'Vulners', 'url': 'https://vulners.com/', 'description': 'Your search engine for security intelligence', 'domain': 'vulners.com', 'favicon': 'https://f.start.me/vulners.com'},
                {'title': 'VulDB', 'url': 'https://vuldb.com/', 'description': 'One of the largest vulnerability databases', 'domain': 'vuldb.com', 'favicon': 'https://f.start.me/vuldb.com'},
                {'title': 'CVE Details', 'url': 'https://www.cvedetails.com/', 'description': 'The ultimate security vulnerability datasource', 'domain': 'cvedetails.com', 'favicon': 'https://f.start.me/cvedetails.com'},
                {'title': 'OpenCVE', 'url': 'https://www.opencve.io/cve', 'description': 'Easiest way to track CVE updates and get alerted', 'domain': 'opencve.io', 'favicon': 'https://f.start.me/opencve.io'},
                {'title': 'cvefeed.io', 'url': 'https://cvefeed.io/', 'description': 'Up-to-date feed of the latest CVEs and advisories', 'domain': 'cvefeed.io', 'favicon': 'https://f.start.me/cvefeed.io'},
                {'title': 'InTheWild', 'url': 'https://inthewild.io/feed', 'description': 'Free open source feed of exploited vulnerabilities', 'domain': 'inthewild.io', 'favicon': 'https://f.start.me/inthewild.io'},
                {'title': 'Exploit-DB', 'url': 'https://www.exploit-db.com/', 'description': 'Exploit database and proof-of-concept code', 'domain': 'exploit-db.com', 'favicon': 'https://f.start.me/exploit-db.com'},
                {'title': 'Packet Storm', 'url': 'https://packetstormsecurity.com/', 'description': 'Exploits, advisories, tools and whitepapers', 'domain': 'packetstormsecurity.com', 'favicon': 'https://f.start.me/packetstormsecurity.com'},
                {'title': 'GTFOBins', 'url': 'https://gtfobins.github.io/', 'description': 'Unix binaries for privilege escalation and security bypasses', 'domain': 'gtfobins.github.io', 'favicon': 'https://f.start.me/gtfobins.github.io'},
                {'title': 'LOLBAS', 'url': 'https://lolbas-project.github.io/', 'description': 'Living Off The Land Windows binaries and scripts', 'domain': 'lolbas-project.github.io', 'favicon': 'https://f.start.me/lolbas-project.github.io'},
                {'title': 'Payloads All The Things', 'url': 'https://swisskyrepo.github.io/PayloadsAllTheThings/', 'description': 'Payloads and bypasses for web application security', 'domain': 'swisskyrepo.github.io', 'favicon': 'https://f.start.me/swisskyrepo.github.io'},
                {'title': 'RevShells', 'url': 'https://www.revshells.com/', 'description': 'Online reverse shell generator with encoding options', 'domain': 'revshells.com', 'favicon': 'https://f.start.me/revshells.com'},
                {'title': 'HackerOne Hacktivity', 'url': 'https://hackerone.com/hacktivity', 'description': 'See the latest hacker activity on HackerOne', 'domain': 'hackerone.com', 'favicon': 'https://f.start.me/hackerone.com'},
                {'title': 'Bugcrowd Crowdstream', 'url': 'https://bugcrowd.com/crowdstream', 'description': 'Accepted and disclosed submissions on Bugcrowd programs', 'domain': 'bugcrowd.com', 'favicon': 'https://f.start.me/bugcrowd.com'},
                {'title': 'GTFOArgs', 'url': 'https://gtfoargs.github.io/', 'description': 'Unix binaries that can be manipulated for argument injection', 'domain': 'gtfoargs.github.io', 'favicon': 'https://f.start.me/gtfoargs.github.io'},
                {'title': 'LOLDrivers', 'url': 'https://www.loldrivers.io/', 'description': 'Known malicious and vulnerable Windows drivers', 'domain': 'loldrivers.io', 'favicon': 'https://f.start.me/loldrivers.io'},
                {'title': 'shell-storm Shellcodes', 'url': 'https://shell-storm.org/shellcode/index.html', 'description': 'Shellcode database for study cases', 'domain': 'shell-storm.org', 'favicon': 'https://f.start.me/shell-storm.org'},
                {'title': 'Zero Day Initiative', 'url': 'https://www.zerodayinitiative.com/advisories/published/', 'description': 'Publicly disclosed vulnerabilities discovered by ZDI researchers', 'domain': 'zerodayinitiative.com', 'favicon': 'https://f.start.me/zerodayinitiative.com'},
                {'title': 'WADComs', 'url': 'https://wadcoms.github.io/', 'description': 'Offensive security commands for Windows/AD environments', 'domain': 'wadcoms.github.io', 'favicon': 'https://f.start.me/wadcoms.github.io'}
            ]
        },
        {
            'id': 9204,
            'title': 'HACKER SEARCH: LEAKS, CREDENTIALS & HASHES',
            'type': 'urllist',
            'group': 'cyber_intel',
            'icon': 'key',
            'color': '#ec4899',
            'links': [
                {'title': 'Dehashed', 'url': 'https://www.dehashed.com/', 'description': 'Free deep-web scans and protection against credential leaks', 'domain': 'dehashed.com', 'favicon': 'https://f.start.me/dehashed.com'},
                {'title': 'LeakCheck', 'url': 'https://leakcheck.io/', 'description': 'Make sure your credentials have not been compromised', 'domain': 'leakcheck.io', 'favicon': 'https://f.start.me/leakcheck.io'},
                {'title': 'Snusbase', 'url': 'https://snusbase.com/', 'description': 'Stay on top of the latest database breaches', 'domain': 'snusbase.com', 'favicon': 'https://f.start.me/snusbase.com'},
                {'title': 'WeLeakInfo', 'url': 'https://weleakinfo.io/', 'description': 'View breached and leaked databases', 'domain': 'weleakinfo.io', 'favicon': 'https://f.start.me/weleakinfo.io'},
                {'title': 'Leak-Lookup', 'url': 'https://leak-lookup.com/', 'description': 'Search across thousands of data breaches', 'domain': 'leak-lookup.com', 'favicon': 'https://f.start.me/leak-lookup.com'},
                {'title': 'CrackStation', 'url': 'https://crackstation.net/', 'description': 'Massive pre-computed lookup tables to crack password hashes', 'domain': 'crackstation.net', 'favicon': 'https://f.start.me/crackstation.net'},
                {'title': 'HashKiller', 'url': 'https://hashkiller.io/listmanager', 'description': 'Pre-cracked hashes, easily searchable', 'domain': 'hashkiller.io', 'favicon': 'https://f.start.me/hashkiller.io'},
                {'title': 'ntlm.pw', 'url': 'https://ntlm.pw/', 'description': 'NTLM hash lookup with 8B+ entries', 'domain': 'ntlm.pw', 'favicon': 'https://f.start.me/ntlm.pw'},
                {'title': 'HaveIBeenSold', 'url': 'https://haveibeensold.app/', 'description': 'Find out if your email has been sold to third parties', 'domain': 'haveibeensold.app', 'favicon': 'https://f.start.me/haveibeensold.app'},
                {'title': 'WhiteIntel', 'url': 'https://whiteintel.io/', 'description': 'Check if a company or its customers were hit by infostealer malware', 'domain': 'whiteintel.io', 'favicon': 'https://f.start.me/whiteintel.io'},
                {'title': 'Hudson Rock', 'url': 'https://www.hudsonrock.com/threat-intelligence-cybercrime-tools', 'description': 'Free cybercrime intelligence on compromised credentials', 'domain': 'hudsonrock.com', 'favicon': 'https://f.start.me/hudsonrock.com'},
                {'title': 'InfoStealers.info', 'url': 'https://infostealers.info/', 'description': 'Instant insights from infostealer data', 'domain': 'infostealers.info', 'favicon': 'https://f.start.me/infostealers.info'},
                {'title': 'LeakRadar', 'url': 'https://leakradar.io/', 'description': 'Check email credentials against infostealer logs', 'domain': 'leakradar.io', 'favicon': 'https://f.start.me/leakradar.io'},
                {'title': 'Distributed Denial of Secrets', 'url': 'https://ddosecrets.com/', 'description': 'Non-profit archive publishing and preserving leaks', 'domain': 'ddosecrets.com', 'favicon': 'https://f.start.me/ddosecrets.com'},
                {'title': 'Cryptome', 'url': 'https://cryptome.org/', 'description': 'Documents for publication prohibited by governments worldwide', 'domain': 'cryptome.org', 'favicon': 'https://f.start.me/cryptome.org'}
            ]
        },
        {
            'id': 9205,
            'title': 'HACKER SEARCH: DNS, CERTS & INFRA',
            'type': 'urllist',
            'group': 'cyber_intel',
            'icon': 'network',
            'color': '#06b6d4',
            'links': [
                {'title': 'RapidDNS', 'url': 'https://rapiddns.io/', 'description': 'Query subdomains or sites of a same IP easily', 'domain': 'rapiddns.io', 'favicon': 'https://f.start.me/rapiddns.io'},
                {'title': 'Farsight DNSDB', 'url': 'https://www.farsightsecurity.com/', 'description': 'Passive DNS historical database', 'domain': 'farsightsecurity.com', 'favicon': 'https://f.start.me/farsightsecurity.com'},
                {'title': 'Chaos (ProjectDiscovery)', 'url': 'https://chaos.projectdiscovery.io/#/', 'description': 'Enhance research and analyse changes around DNS', 'domain': 'chaos.projectdiscovery.io', 'favicon': 'https://f.start.me/chaos.projectdiscovery.io'},
                {'title': 'DNSViz', 'url': 'https://dnsviz.net/', 'description': 'Visualize the status of a DNS zone', 'domain': 'dnsviz.net', 'favicon': 'https://f.start.me/dnsviz.net'},
                {'title': 'Validin', 'url': 'https://app.validin.com/', 'description': 'Massive DNS record collection with free history search', 'domain': 'app.validin.com', 'favicon': 'https://f.start.me/app.validin.com'},
                {'title': 'AskDNS', 'url': 'https://askdns.com/', 'description': 'Lookup connected domain names and IP addresses', 'domain': 'askdns.com', 'favicon': 'https://f.start.me/askdns.com'},
                {'title': 'DNSTwister', 'url': 'https://dnstwister.report/', 'description': 'Anti-phishing domain name search and DNS monitoring', 'domain': 'dnstwister.report', 'favicon': 'https://f.start.me/dnstwister.report'},
                {'title': 'NSLookup.io', 'url': 'https://www.nslookup.io/', 'description': 'Find all DNS records for a domain name', 'domain': 'nslookup.io', 'favicon': 'https://f.start.me/nslookup.io'},
                {'title': 'DNSMap', 'url': 'https://dnsmap.io/', 'description': 'Worldwide DNS propagation checker', 'domain': 'dnsmap.io', 'favicon': 'https://f.start.me/dnsmap.io'},
                {'title': 'dnslookup.pro', 'url': 'https://dnslookup.pro/', 'description': 'Advanced DNS record analysis and troubleshooting', 'domain': 'dnslookup.pro', 'favicon': 'https://f.start.me/dnslookup.pro'},
                {'title': 'dnsaudit.io', 'url': 'https://dnsaudit.io/', 'description': 'Find DNS misconfigurations, risks and security gaps', 'domain': 'dnsaudit.io', 'favicon': 'https://f.start.me/dnsaudit.io'},
                {'title': 'CertSpotter', 'url': 'https://sslmate.com/certspotter/', 'description': 'Monitor domains for expiring, unauthorized and invalid certs', 'domain': 'sslmate.com', 'favicon': 'https://f.start.me/sslmate.com'},
                {'title': 'ciphersuite.info', 'url': 'https://ciphersuite.info/', 'description': 'TLS ciphersuite search by IANA, OpenSSL or GnuTLS name', 'domain': 'ciphersuite.info', 'favicon': 'https://f.start.me/ciphersuite.info'},
                {'title': 'certs.io', 'url': 'https://certs.io/', 'description': 'Search TLS certificates across the internet', 'domain': 'certs.io', 'favicon': 'https://f.start.me/certs.io'},
                {'title': 'tls.bufferover.run', 'url': 'https://tls.bufferover.run/', 'description': 'Quickly find certificates in IPv4 space', 'domain': 'tls.bufferover.run', 'favicon': 'https://f.start.me/tls.bufferover.run'},
                {'title': 'ZETAlytics', 'url': 'https://zetalytics.com/', 'description': 'Unrivalled global network visibility in searchable datasets', 'domain': 'zetalytics.com', 'favicon': 'https://f.start.me/zetalytics.com'},
                {'title': 'FacebookCT', 'url': 'https://developers.facebook.com/tools/ct/search/', 'description': 'Facebook certificate transparency search for a domain', 'domain': 'developers.facebook.com', 'favicon': 'https://f.start.me/developers.facebook.com'}
            ]
        },
        {
            'id': 9206,
            'title': 'HACKER SEARCH: THREAT INTEL & MALWARE',
            'type': 'urllist',
            'group': 'cyber_intel',
            'icon': 'radar',
            'color': '#8b5cf6',
            'links': [
                {'title': 'MITRE ATT&CK', 'url': 'https://attack.mitre.org/', 'description': 'Knowledge base of adversary tactics and techniques', 'domain': 'attack.mitre.org', 'favicon': 'https://f.start.me/attack.mitre.org'},
                {'title': 'MalwareBazaar (abuse.ch)', 'url': 'https://bazaar.abuse.ch/browse/', 'description': 'Malware sample database by abuse.ch', 'domain': 'bazaar.abuse.ch', 'favicon': 'https://f.start.me/bazaar.abuse.ch'},
                {'title': 'ThreatFox (abuse.ch)', 'url': 'https://threatfox.abuse.ch/browse/', 'description': 'Indicator of Compromise (IOC) database', 'domain': 'threatfox.abuse.ch', 'favicon': 'https://f.start.me/threatfox.abuse.ch'},
                {'title': 'URLhaus (abuse.ch)', 'url': 'https://urlhaus.abuse.ch/browse/', 'description': 'Malicious URL database', 'domain': 'urlhaus.abuse.ch', 'favicon': 'https://f.start.me/urlhaus.abuse.ch'},
                {'title': 'FeodoTracker (abuse.ch)', 'url': 'https://feodotracker.abuse.ch/browse/', 'description': 'Botnet Command&Control server list', 'domain': 'feodotracker.abuse.ch', 'favicon': 'https://f.start.me/feodotracker.abuse.ch'},
                {'title': 'SSLBL (abuse.ch)', 'url': 'https://sslbl.abuse.ch/ssl-certificates/', 'description': 'All malicious SSL certificates', 'domain': 'sslbl.abuse.ch', 'favicon': 'https://f.start.me/sslbl.abuse.ch'},
                {'title': 'YARAify (abuse.ch)', 'url': 'https://yaraify.abuse.ch/', 'description': 'Scan files against a large repository of YARA rules', 'domain': 'yaraify.abuse.ch', 'favicon': 'https://f.start.me/yaraify.abuse.ch'},
                {'title': 'AnyRun', 'url': 'https://app.any.run/submissions', 'description': 'Browse thousands of malware sandbox submissions', 'domain': 'app.any.run', 'favicon': 'https://f.start.me/app.any.run'},
                {'title': 'Hybrid Analysis', 'url': 'https://www.hybrid-analysis.com/', 'description': 'Free malware analysis service for the community', 'domain': 'hybrid-analysis.com', 'favicon': 'https://f.start.me/hybrid-analysis.com'},
                {'title': 'Joe Sandbox', 'url': 'https://www.joesandbox.com/', 'description': 'Threat hunting and deep malware analysis engine', 'domain': 'joesandbox.com', 'favicon': 'https://f.start.me/joesandbox.com'},
                {'title': 'tria.ge', 'url': 'https://tria.ge/s', 'description': 'Fully automated high-volume malware sandboxing', 'domain': 'tria.ge', 'favicon': 'https://f.start.me/tria.ge'},
                {'title': 'VirusShare', 'url': 'https://virusshare.com/', 'description': 'Repository of 48M+ malware samples', 'domain': 'virusshare.com', 'favicon': 'https://f.start.me/virusshare.com'},
                {'title': 'MalShare', 'url': 'https://malshare.com/', 'description': 'Community driven public malware repository', 'domain': 'malshare.com', 'favicon': 'https://f.start.me/malshare.com'},
                {'title': 'PhishTank', 'url': 'https://phishtank.org/', 'description': 'Collaborative clearinghouse for phishing URLs', 'domain': 'phishtank.org', 'favicon': 'https://f.start.me/phishtank.org'},
                {'title': 'OpenPhish', 'url': 'https://openphish.com/', 'description': 'Actionable intelligence on active phishing threats', 'domain': 'openphish.com', 'favicon': 'https://f.start.me/openphish.com'},
                {'title': 'urlquery', 'url': 'https://urlquery.net/', 'description': 'Service for detecting and analyzing web-based malware', 'domain': 'urlquery.net', 'favicon': 'https://f.start.me/urlquery.net'},
                {'title': 'Sucuri SiteCheck', 'url': 'https://sitecheck.sucuri.net/', 'description': 'Check websites for malware and blacklisting status', 'domain': 'sitecheck.sucuri.net', 'favicon': 'https://f.start.me/sitecheck.sucuri.net'},
                {'title': 'AbuseIPDB', 'url': 'https://www.abuseipdb.com/', 'description': 'Check the report history of any IP address', 'domain': 'abuseipdb.com', 'favicon': 'https://f.start.me/abuseipdb.com'},
                {'title': 'Spamhaus', 'url': 'https://spamhaus.com/', 'description': 'Protect and investigate using IP and domain reputation data', 'domain': 'spamhaus.com', 'favicon': 'https://f.start.me/spamhaus.com'},
                {'title': 'IBM X-Force Exchange', 'url': 'https://exchange.xforce.ibmcloud.com/', 'description': 'Threat intelligence sharing and research platform', 'domain': 'exchange.xforce.ibmcloud.com', 'favicon': 'https://f.start.me/exchange.xforce.ibmcloud.com'},
                {'title': 'InQuest Labs', 'url': 'https://labs.inquest.net/', 'description': 'Threat intel and forensic signature research', 'domain': 'labs.inquest.net', 'favicon': 'https://f.start.me/labs.inquest.net'},
                {'title': 'Zone-H Archive', 'url': 'https://www.zone-h.org/archive/', 'description': 'Archive collecting records of defaced websites', 'domain': 'zone-h.org', 'favicon': 'https://f.start.me/zone-h.org'},
                {'title': 'ransomlook.io', 'url': 'https://www.ransomlook.io/', 'description': 'Open-source real-time ransomware intelligence', 'domain': 'ransomlook.io', 'favicon': 'https://f.start.me/ransomlook.io'},
                {'title': 'Kaspersky OpenTIP', 'url': 'https://opentip.kaspersky.com/requests', 'description': 'Scan files, domains, IP addresses and URLs for threats', 'domain': 'opentip.kaspersky.com', 'favicon': 'https://f.start.me/opentip.kaspersky.com'}
            ]
        }
    ]

    # Insert AI and Australian widgets cleanly into columns
    columns[0]['widgets'].insert(0, ai_widgets[0]) # AI Assistants
    columns[0]['widgets'].insert(1, ai_widgets[3]) # Local AI
    columns[0]['widgets'].insert(2, aus_widgets[1]) # [AUS] Government & Data
    columns[0]['widgets'].insert(3, aus_widgets[4]) # [AUS] Public Records
    columns[0]['widgets'].insert(4, aus_widgets[7]) # [AUS] Gov Services & myGov

    columns[1]['widgets'].insert(0, ai_widgets[1]) # AI Search
    columns[1]['widgets'].insert(1, aus_widgets[2]) # [AUS] Police & Courts
    columns[1]['widgets'].insert(2, aus_widgets[6]) # [AUS] News & Media
    columns[1]['widgets'].insert(3, visual_widgets[0]) # Interactive Visual Toolkit

    columns[2]['widgets'].insert(0, ai_widgets[2]) # AI Code & Agents
    columns[2]['widgets'].insert(1, aus_widgets[5]) # [AUS] Transport & Rego
    columns[2]['widgets'].insert(2, aus_widgets[9]) # [AUS] Emergency & Weather
    columns[2]['widgets'].insert(3, aus_widgets[10]) # [AUS] Defence & Security
    columns[2]['widgets'].insert(4, aus_widgets[11]) # [AUS] Sport, Arts & Culture

    columns[3]['widgets'].insert(0, ai_widgets[4]) # AI Image & Video
    columns[3]['widgets'].insert(1, ai_widgets[5]) # AI Voice & Audio
    columns[3]['widgets'].insert(2, aus_widgets[0]) # [AUS] Corporations & ABN
    columns[3]['widgets'].insert(3, aus_widgets[3]) # [AUS] Real Estate & Cadastre
    columns[3]['widgets'].insert(4, aus_widgets[8]) # [AUS] Telco, Postal & Address

    # Hacker search engine modules (curated from edoardottt/awesome-hacker-search-engines)
    columns[0]['widgets'].insert(6, hacker_widgets[0]) # HACKER SEARCH: Servers & Attack Surface
    columns[1]['widgets'].insert(5, hacker_widgets[1]) # HACKER SEARCH: Vulnerabilities & Exploits
    columns[2]['widgets'].insert(6, hacker_widgets[2]) # HACKER SEARCH: Leaks, Credentials & Hashes
    columns[3]['widgets'].insert(6, hacker_widgets[3]) # HACKER SEARCH: DNS, Certs & Infra
    columns[3]['widgets'].insert(7, hacker_widgets[4]) # HACKER SEARCH: Threat Intel & Malware

    # Expanded [AUS] Australian modules and global fallback modules.
    # Distributed round-robin so the four columns stay balanced in height.
    for i, widget in enumerate(AUS_EXTRA_WIDGETS):
        columns[i % len(columns)]['widgets'].append(widget)
    for i, widget in enumerate(GLOBAL_EXTRA_WIDGETS):
        columns[i % len(columns)]['widgets'].append(widget)

    # Australian-first: tag AU links, float them to the top of every module,
    # and float every [AUS] module to the top of its column.
    au_link_total = apply_au_priority(columns)

    # Recalculate totals
    total_widgets = sum(len(col.get('widgets', [])) for col in columns)
    total_links = sum(sum(len(w.get('links', [])) for w in col.get('widgets', [])) for col in columns)

    # Evergreen search engines without outdated model parentheticals
    search_engines = [
        {'id': 'filter', 'name': 'Filter Bookmarks', 'type': 'filter', 'placeholder': f'Fuzzy search {total_links}+ tools, Australian databases, and AI models...'},
        {'id': 'chatgpt', 'name': 'ChatGPT', 'type': 'web', 'url': 'https://chatgpt.com/?q=%s'},
        {'id': 'claude', 'name': 'Claude', 'type': 'web', 'url': 'https://claude.ai/new?q=%s'},
        {'id': 'aistudio', 'name': 'Google AI Studio', 'type': 'web', 'url': 'https://aistudio.google.com/prompts/new_chat?prompt=%s'},
        {'id': 'perplexity', 'name': 'Perplexity', 'type': 'web', 'url': 'https://www.perplexity.ai/search/new?q=%s'},
        {'id': 'deepseek', 'name': 'DeepSeek', 'type': 'web', 'url': 'https://chat.deepseek.com/?q=%s'},
        {'id': 'genspark', 'name': 'Genspark', 'type': 'web', 'url': 'https://www.genspark.ai/search?query=%s'},
        {'id': 'phind', 'name': 'Phind', 'type': 'web', 'url': 'https://www.phind.com/search?q=%s'},
        {'id': 'trove', 'name': 'Trove (NLA)', 'type': 'web', 'url': 'https://trove.nla.gov.au/search/category/newspapers?keyword=%s'},
        {'id': 'abn', 'name': 'ABN Lookup', 'type': 'web', 'url': 'https://abr.business.gov.au/Search/ResultsActive?SearchText=%s'},
        {'id': 'austlii', 'name': 'AusLII Law', 'type': 'web', 'url': 'http://www.austlii.edu.au/cgi-bin/sinosrch.cgi?query=%s'},
        {'id': 'google', 'name': 'Google Dorking', 'type': 'web', 'url': 'https://www.google.com/search?q=%s'},
        {'id': 'duckduckgo', 'name': 'DuckDuckGo', 'type': 'web', 'url': 'https://duckduckgo.com/?q=%s'},
        {'id': 'shodan', 'name': 'Shodan', 'type': 'web', 'url': 'https://www.shodan.io/search?query=%s'},
        {'id': 'virustotal', 'name': 'VirusTotal', 'type': 'web', 'url': 'https://www.virustotal.com/gui/search/%s'},
        {'id': 'github', 'name': 'GitHub Code', 'type': 'web', 'url': 'https://github.com/search?q=%s&type=code'}
    ]

    output_data = {
        'title': 'Bubbsy Start Page',
        'subtitle': 'Local OSINT & AI Intelligence Command Center',
        'version': '2.5.0',
        'total_widgets': total_widgets,
        'total_links': total_links,
        'au_link_total': au_link_total,
        'world_clocks': world_clocks,
        'rss_feeds': rss_feeds,
        'search_engines': search_engines,
        'columns': columns
    }

    # Save to JSON
    with open('data/osint_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    # Save JS bundle
    with open('data/osint_data.js', 'w', encoding='utf-8') as f:
        f.write("window.BUBBSY_DATA = " + json.dumps(output_data, indent=2) + ";\n")

    print(f"Successfully generated clean evergreen dataset:")
    print(f"Total Widgets: {total_widgets}")
    print(f"Total Links: {total_links}")
    print(f"Australian-priority links: {au_link_total}")

    # Refresh first-added dates for the "Newest" catalogue order. Needs git history; skip quietly
    # when building from an export without it.
    try:
        import build_link_dates
        build_link_dates.build()
    except Exception as e:
        print(f"link_dates not refreshed ({e}); run build_link_dates.py from a git checkout")

if __name__ == '__main__':
    build_data()
