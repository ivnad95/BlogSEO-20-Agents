# BlogSEO v3 - AI-Powered SEO Blog Generator with 20 AI Agents 🚀

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46-red)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-green)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🌟 Overview

BlogSEO v3 is a state-of-the-art, AI-powered platform that generates high-quality, SEO-optimized blog content using **20 specialized AI agents powered by Google Gemini 2.0 Flash**. Each agent handles a specific aspect of content creation, from trend analysis to final optimization.

### ✨ Key Features

- **🤖 20 Specialized AI Agents**: Each with unique expertise
- **⚡ Powered by Gemini 2.0 Flash**: Latest Google AI model
- **📊 Real-Time Data**: Pulls trends from Google, Reddit, and news
- **🔍 Comprehensive SEO**: Keywords, meta tags, schema markup
- **📦 Multiple Exports**: HTML, Markdown, JSON, WordPress, Medium
- **🆓 Open Source Tools**: Uses free APIs (except Gemini)
- **📝 Professional Content**: 2000+ word articles with citations

## 🎯 The 20 AI Agents

| Agent | Purpose |
|-------|---------|
| **TrendIdeaAgent** | Analyzes Google Trends, Reddit, and news for content opportunities |
| **UserInputAgent** | Processes and validates user requirements |
| **KeywordMiningAgent** | Discovers 80+ keywords with clustering and intent mapping |
| **CompetitorScanAgent** | Analyzes competitor content and identifies gaps |
| **OutlineGeneratorAgent** | Creates comprehensive blog structure |
| **DraftWriterAgent** | Generates main content (2000+ words) |
| **KeywordEnrichmentAgent** | Optimizes keyword density and placement |
| **ReadabilityAgent** | Improves content readability and flow |
| **HumanizationAgent** | Adds personality and engagement |
| **StyleConsistencyAgent** | Ensures consistent voice and tone |
| **ToneCheckAgent** | Verifies appropriate tone for audience |
| **InternalLinkingAgent** | Suggests internal link strategies |
| **ExternalLinkVettingAgent** | Finds authoritative external sources |
| **ImageOptimizationAgent** | Plans visual content strategy |
| **AltTextAgent** | Generates SEO-optimized alt text |
| **OnPageSEOAgent** | Optimizes meta tags, headers, URLs |
| **TechnicalSEOAgent** | Handles technical SEO requirements |
| **SchemaEnhancementAgent** | Creates structured data markup |
| **QAValidationAgent** | Performs final quality checks |
| **FinalAssemblyAgent** | Assembles and polishes final content |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key (get it [here](https://makersuite.google.com/app/apikey))
- 2GB RAM minimum

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ivnad95/BlogSEO-20-Agents.git
cd BlogSEO-20-Agents
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API keys**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Run the application**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📋 How It Works

1. **Enter Blog Topic**: Input your desired blog topic
2. **Agents Activate**: 20 AI agents process in sequence
3. **Real-Time Progress**: Watch as each agent completes
4. **View Results**: See outputs from each agent
5. **Export Content**: Download in multiple formats

### Sample Workflow

```
User Input: "Top 10 AI agents open source in 2025"
     ↓
TrendIdeaAgent: Analyzes Google Trends, Reddit discussions
     ↓
KeywordMiningAgent: Finds 80+ relevant keywords
     ↓
DraftWriterAgent: Generates 3000+ word article
     ↓
[... 16 more agents optimize content ...]
     ↓
FinalAssemblyAgent: Delivers publish-ready content
```

## 📊 Real Performance Metrics

From actual execution:
- **Total Time**: ~162 seconds for complete pipeline
- **Content Generated**: 3000+ words
- **Keywords Found**: 80+ with clustering
- **Data Sources**: Google Trends, Reddit, News RSS
- **Success Rate**: 100% (all 20 agents)

## 🛠️ Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key  # For comparison
GOOGLE_CSE_ID=your_cse_id       # For enhanced search
```

### Gemini Models Supported

- `gemini-2.0-flash` (Default - Fastest)
- `gemini-2.5-flash` (More capable)
- `gemini-2.0-flash-preview-image-generation` (With images)

## 📦 Export Formats

- **HTML**: Complete with SEO meta tags and schema
- **Markdown**: For GitHub, documentation
- **JSON**: Structured data for APIs
- **WordPress XML**: Direct import to WordPress
- **Medium**: Formatted for Medium publishing

## 🔧 Development

### Project Structure

```
BlogSEO-20-Agents/
├── agents/               # 20 AI agent implementations
│   ├── base_agent.py    # Base class with Gemini integration
│   ├── trend_idea.py    # Trend analysis agent
│   └── ...              # 18 more specialized agents
├── orchestrator/        # Agent orchestration system
├── utilities/           # Helper functions
├── app.py              # Streamlit UI
└── requirements.txt    # Dependencies
```

### Adding New Agents

```python
from agents.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def run(self, state: dict) -> dict:
        # Your agent logic here
        prompt = "Your Gemini prompt"
        response = self.execute_prompt(system_prompt, user_prompt)
        return self.parse_json_response(response)
```

## 📈 Sample Output

The system generated a comprehensive article about "Top 10 AI Agents Open Source in 2025" including:
- Detailed analysis of 10 AI frameworks
- SEO-optimized title and meta description
- 5 FAQ sections
- Internal/external link suggestions
- Schema markup
- 3000+ words of content

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### TODO List

- [ ] Add image generation with DALL-E/Stable Diffusion
- [ ] Implement A/B testing for titles
- [ ] Add multilingual support
- [ ] Create Chrome extension
- [ ] Add voice input/output

## 📜 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Google Gemini team for the amazing AI model
- LangChain for the framework
- Streamlit for the UI platform
- Open source community

## 📞 Contact

- GitHub: [@ivnad95](https://github.com/ivnad95)
- Email: ivnad95@gmail.com

---

⭐ **Star this repo if you find it useful!**

🔥 **Built with passion using 20 AI agents working in harmony**
