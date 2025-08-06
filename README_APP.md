# BlogSEO v3 - Streamlit Application

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- API Keys: OpenAI, Google Gemini, and Google Custom Search Engine

### Installation & Setup

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd "BlogSEO v3-2/BlogSEO v3-2"
   ```

2. **Run the application**
   ```bash
   ./run.sh
   ```
   
   Or manually:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. **Configure API Keys**
   - Open the application in your browser (http://localhost:8501)
   - Click on "Configure API Keys" in the sidebar
   - Enter your API keys and click "Save API Keys"

## 📱 Application Features

### Main Interface

#### Sidebar
- **🚀 Logo**: BlogSEO v3 branding
- **🔑 API Configuration**: Secure input fields for API keys that save to `.env`
- **⚙️ Generation Settings**: 
  - Enable/disable result caching
  - Auto-export options
- **ℹ️ About**: Application information and features

#### Main Area
- **📝 Blog Topic Input**: Enter your desired blog topic
- **🚀 Generate Button**: Start the blog generation process

### Generation Process
- **📊 Real-time Progress Bar**: Visual progress indicator showing completion percentage
- **🤖 Agent Status Updates**: Live updates as each agent processes
- **⏱️ Time Tracking**: Total generation time displayed upon completion

### Output Display

#### 📊 Agent Outputs Tab
- Expandable sections for each agent's output
- Timestamps for each processing step
- JSON-formatted results for detailed inspection

#### 👁️ HTML Preview Tab
- Full HTML preview of the generated blog post
- Professional styling with responsive design
- Embedded in an iframe for accurate rendering

#### 📝 Markdown Tab
- Clean markdown view of the content
- Ready for copying or editing
- Properly formatted with headers and sections

#### 📥 Export Tab
- **Download Options**:
  - 📄 HTML: Styled, ready-to-publish HTML file
  - 📝 Markdown: Clean markdown format
  - 📊 JSON: Structured data export
- **Advanced Options**:
  - 🌐 WordPress XML (coming soon)
  - 📦 Complete Bundle (coming soon)

## 🎯 Usage Tips

### For Best Results
1. **Be Specific**: Provide detailed, focused blog topics
2. **Check API Keys**: Ensure all required API keys are configured
3. **Use Caching**: Enable result caching to avoid redundant API calls
4. **Monitor Progress**: Watch the agent outputs to understand the generation process

### Troubleshooting

#### Common Issues
- **Missing API Keys**: Check the sidebar for configuration status
- **Generation Fails**: Review agent outputs for specific error messages
- **Slow Performance**: Enable caching and check your internet connection

#### Cache Management
The application uses Streamlit's built-in caching with a 1-hour TTL. To clear cache:
```bash
streamlit cache clear
```

## 🔧 Advanced Configuration

### Environment Variables
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_CSE_ID=your_google_cse_id_here
```

### Custom Agents
The application uses 20+ specialized agents for blog generation:
- Trend Analysis
- Keyword Mining
- Content Writing
- SEO Optimization
- Quality Assurance
- And more...

### Session State Management
The app maintains state for:
- Generation progress
- Agent outputs
- Final results
- User settings

## 📊 Export Formats

### HTML Export
- Complete, styled HTML document
- Responsive design
- Meta tags for SEO
- Ready for web publishing

### Markdown Export
- Clean, formatted markdown
- Compatible with most CMS platforms
- Preserves structure and formatting

### JSON Export
- Structured data format
- All metadata included
- Suitable for further processing
- API integration ready

## 🎨 UI Customization

The application includes custom CSS for:
- Progress bar styling
- Button animations
- Success/error messages
- Agent output containers
- Responsive layout

## 🔄 Updates & Maintenance

### Checking for Updates
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Clearing Cache
```bash
streamlit cache clear
rm -rf cache/
```

## 📝 Notes

- The application automatically saves API keys to `.env` for persistence
- Generated content is cached for 1 hour to optimize API usage
- All agent outputs are stored in `st.session_state` for the session duration
- Export files are timestamped to prevent overwrites

## 🤝 Support

For issues or questions:
1. Check the agent outputs for error messages
2. Verify API key configuration
3. Review the application logs in the terminal
4. Consult the main project documentation

## 📄 License

See the main project LICENSE file for details.

---

**Version**: 3.0.0  
**Last Updated**: 2024
