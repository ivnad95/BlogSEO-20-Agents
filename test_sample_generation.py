#!/usr/bin/env python3
"""Test script for generating a sample article and verifying output."""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.orchestrator import Orchestrator
from utilities.exporters import BlogExporter

def test_sample_generation():
    """Generate a sample article and verify it saves to output directory."""
    
    print("=" * 60)
    print("SAMPLE ARTICLE GENERATION TEST")
    print("=" * 60)
    
    # Initialize orchestrator
    print("\n1. Initializing orchestrator...")
    orchestrator = Orchestrator()
    
    # Define test topic
    test_topic = "The Future of Artificial Intelligence in Healthcare"
    print(f"\n2. Generating article for topic: '{test_topic}'")
    print("   This may take a few minutes as it runs through all agents...")
    
    # Run orchestration
    print("\n3. Starting orchestration process...")
    state = orchestrator.run(topic=test_topic)
    
    # Check results
    print(f"\n4. Orchestration completed with status: {state.status}")
    print(f"   - Completed agents: {len(state.completed_agents)}")
    print(f"   - Failed agents: {len(state.failed_agents)}")
    
    if state.failed_agents:
        print(f"   - Failed agents: {', '.join(state.failed_agents)}")
    
    # Check if we have final output
    if state.final_output:
        print("\n5. Final output generated successfully!")
        
        # Initialize exporter
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        exporter = BlogExporter(output_dir=output_dir)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"sample_article_{timestamp}"
        
        # Export to different formats
        print("\n6. Exporting to output directory...")
        
        # Export as JSON
        json_path = output_dir / f"{base_filename}.json"
        with open(json_path, 'w') as f:
            json.dump(state.final_output if isinstance(state.final_output, dict) else {"content": str(state.final_output)}, f, indent=2)
        print(f"   ✓ JSON saved to: {json_path}")
        
        # Export as Markdown if we have proper structure
        if isinstance(state.final_output, dict):
            md_path = output_dir / f"{base_filename}.md"
            md_content = f"""# {state.final_output.get('title', test_topic)}

**Topic:** {test_topic}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {state.status}  

---

## Content

{state.final_output.get('content', 'No content generated')}

---

## Metadata

- **Keywords:** {state.final_output.get('keywords', 'N/A')}
- **Meta Description:** {state.final_output.get('meta_description', 'N/A')}
- **Author:** {state.final_output.get('author', 'AI Generated')}

---

## Generation Statistics

- **Total Agents:** {len(orchestrator.agents)}
- **Completed Agents:** {len(state.completed_agents)}
- **Failed Agents:** {len(state.failed_agents)}
- **Generation Time:** {(state.end_time - state.start_time).total_seconds():.2f} seconds
"""
            with open(md_path, 'w') as f:
                f.write(md_content)
            print(f"   ✓ Markdown saved to: {md_path}")
            
            # Export as HTML
            html_path = output_dir / f"{base_filename}.html"
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{state.final_output.get('meta_description', '')}">
    <meta name="keywords" content="{state.final_output.get('keywords', '')}">
    <title>{state.final_output.get('title', test_topic)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: #f9f9f9;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
        }}
        .metadata {{
            background: #e8f4f8;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
        .content {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>{state.final_output.get('title', test_topic)}</h1>
    
    <div class="metadata">
        <p><strong>Topic:</strong> {test_topic}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Author:</strong> {state.final_output.get('author', 'AI Generated')}</p>
    </div>
    
    <div class="content">
        {state.final_output.get('content', '<p>No content generated</p>')}
    </div>
    
    <div class="footer">
        <p>Generated by BlogSEO v3 - Multi-Agent Orchestration System</p>
        <p>Generation time: {(state.end_time - state.start_time).total_seconds():.2f} seconds | 
           Agents: {len(state.completed_agents)} completed, {len(state.failed_agents)} failed</p>
    </div>
</body>
</html>"""
            with open(html_path, 'w') as f:
                f.write(html_content)
            print(f"   ✓ HTML saved to: {html_path}")
        
        # Verify files exist
        print("\n7. Verifying output files...")
        output_files = list(output_dir.glob(f"{base_filename}*"))
        if output_files:
            print(f"   ✓ Found {len(output_files)} output files:")
            for file in output_files:
                file_size = file.stat().st_size
                print(f"     - {file.name} ({file_size:,} bytes)")
        else:
            print("   ✗ No output files found!")
            return False
        
        print("\n" + "=" * 60)
        print("✓ SAMPLE GENERATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Print summary
        if isinstance(state.final_output, dict):
            print("\nGenerated Article Summary:")
            print(f"  Title: {state.final_output.get('title', 'N/A')[:80]}...")
            if 'content' in state.final_output:
                content_preview = str(state.final_output['content'])[:200].replace('\n', ' ')
                print(f"  Content Preview: {content_preview}...")
            print(f"  Keywords: {state.final_output.get('keywords', 'N/A')}")
        
        return True
        
    else:
        print("\n✗ No final output was generated!")
        print("  This may be due to missing API keys or agent failures.")
        return False


if __name__ == "__main__":
    try:
        success = test_sample_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during sample generation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
