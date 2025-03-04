import re
from typing import Optional, Union

def convert_mermaid_block(text: str) -> str:
    """
    1. If the input text is wrapped in triple backticks with 'mermaid' on the opening line,
       extract the content without the markdown delimiters.
    2. Replace single backticks with actual triple double quotes.
    """
    pattern = r"```\s*mermaid\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        text = match.group(1)
    text = text.replace('`', '"""')
    return text

def render_mermaid_code(mermaid_code: str) -> Union[str, None]:
    """
    Render Mermaid code using client-side rendering with mermaid.js.
    Includes a fullscreen toggle, zoom controls, and error handling.
    Updated to add a delay for proper initialization.
    """
    try:
        # Clean up the mermaid code if it has markdown fences
        clean_code = convert_mermaid_block(mermaid_code)
        
        # Escape special characters for embedding in JavaScript if needed
        escaped_code = clean_code.replace('"', '\\"').replace('\n', '\\n')

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Delay initialization to ensure all resources are loaded
            setTimeout(function() {{
                try {{
                    mermaid.initialize({{
                        startOnLoad: true,
                        theme: 'default',
                        securityLevel: 'loose',
                        fontFamily: 'arial, sans-serif',
                        flowchart: {{
                            htmlLabels: true,
                            curve: 'linear'
                        }},
                        er: {{
                            layoutDirection: 'TB',
                            entityPadding: 15
                        }},
                        sequence: {{
                            diagramMarginX: 50,
                            diagramMarginY: 30,
                            actorMargin: 50,
                            boxMargin: 10
                        }}
                    }});
                    // Reinitialize Mermaid on all elements with the class "mermaid"
                    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                }} catch (e) {{
                    const errorDiv = document.getElementById('error-message');
                    errorDiv.style.display = 'block';
                    errorDiv.innerHTML = 'Error initializing mermaid: ' + e.message;
                }}
            }}, 300); // Delay of 300ms, adjust as needed

            window.onerror = function(msg, url, line) {{
                const errorDiv = document.getElementById('error-message');
                errorDiv.style.display = 'block';
                errorDiv.innerHTML = 'Error rendering diagram: ' + msg + ' (line ' + line + ')';
                return true;
            }};
        }});
    </script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
            font-family: Arial, sans-serif;
            overflow: hidden;
        }}
        #error-message {{
            display: none;
            color: red;
            background-color: #ffeeee;
            border: 1px solid #ffcccc;
            border-radius: 4px;
            padding: 10px;
            margin: 10px;
            font-family: 'Courier New', monospace;
        }}
        /* Main zoom controls */
        .zoom-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            z-index: 1000;
        }}
        .zoom-controls button {{
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin: 0 2px;
            cursor: pointer;
            width: 30px;
            height: 30px;
            font-size: 16px;
        }}
        /* Main mermaid container */
        #main-mermaid {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            min-height: 100px;
            font-family: 'Arial', sans-serif;
        }}
        #main-mermaid svg {{
            max-width: 100%;
            height: auto !important;
        }}
        /* Fullscreen container */
        #fullscreen-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(255, 255, 255, 0.95);
            z-index: 9999;
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
            overflow: hidden;
        }}
        #fullscreen-mermaid {{
            width: 100%;
            height: 90%;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        #fullscreen-mermaid svg {{
            width: 95% !important;
            height: 95% !important;
            max-width: none !important;
            max-height: none !important;
        }}
        .close-fullscreen {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 16px;
            z-index: 10000;
        }}
        /* Fullscreen zoom controls (only visible in fullscreen mode) */
        .fullscreen-zoom-controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            z-index: 1000;
        }}
        .fullscreen-zoom-controls button {{
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin: 0 2px;
            cursor: pointer;
            width: 30px;
            height: 30px;
            font-size: 16px;
        }}
        @media (max-width: 768px) {{
            #fullscreen-mermaid svg {{
                width: 100% !important;
                height: auto !important;
            }}
        }}
    </style>
</head>
<body>
    <div id="error-message"></div>
    <!-- Main view zoom controls -->
    <div class="zoom-controls">
        <button onclick="zoomIn()">+</button>
        <button onclick="zoomOut()">-</button>
        <button onclick="resetZoom()">↺</button>
        <button onclick="toggleFullScreen()">⛶</button>
    </div>
    <!-- Main diagram container -->
    <div id="main-mermaid" class="mermaid">
{clean_code}
    </div>
    <!-- Fullscreen container -->
    <div id="fullscreen-container">
        <button class="close-fullscreen" onclick="toggleFullScreen()">Exit Full Screen</button>
        <!-- Fullscreen zoom controls -->
        <div class="fullscreen-zoom-controls">
            <button onclick="zoomInFullscreen()">+</button>
            <button onclick="zoomOutFullscreen()">-</button>
            <button onclick="resetFullscreenZoom()">↺</button>
        </div>
        <div id="fullscreen-mermaid" class="mermaid">
            <!-- Fullscreen diagram will be populated here -->
        </div>
    </div>
    <script>
        let scale = 1;
        let fullscreenScale = 1;

        function zoomIn() {{
            scale += 0.1;
            applyZoom();
        }}
        
        function zoomOut() {{
            if (scale > 0.3) {{
                scale -= 0.1;
                applyZoom();
            }}
        }}
        
        function resetZoom() {{
            scale = 1;
            applyZoom();
        }}
        
        function applyZoom() {{
            const container = document.getElementById('main-mermaid');
            const svg = container.querySelector('svg');
            if (svg) {{
                svg.style.transform = 'scale(' + scale + ')';
                svg.style.transformOrigin = 'center center';
            }}
        }}

        // Fullscreen zoom functions
        function zoomInFullscreen() {{
            fullscreenScale += 0.1;
            applyFullscreenZoom();
        }}

        function zoomOutFullscreen() {{
            if (fullscreenScale > 0.3) {{
                fullscreenScale -= 0.1;
                applyFullscreenZoom();
            }}
        }}

        function resetFullscreenZoom() {{
            fullscreenScale = 1;
            applyFullscreenZoom();
        }}

        function applyFullscreenZoom() {{
            const container = document.getElementById('fullscreen-mermaid');
            const svg = container.querySelector('svg');
            if (svg) {{
                svg.style.transform = 'scale(' + fullscreenScale + ')';
                svg.style.transformOrigin = 'center center';
            }}
        }}

        function toggleFullScreen() {{
            const fullscreenContainer = document.getElementById('fullscreen-container');
            const fullscreenMermaid = document.getElementById('fullscreen-mermaid');
            const mainMermaid = document.getElementById('main-mermaid');

            if (fullscreenContainer.style.display !== 'flex') {{
                // Enter fullscreen mode
                fullscreenContainer.style.display = 'flex';
                fullscreenMermaid.innerHTML = mainMermaid.innerHTML;
                setTimeout(() => {{
                    mermaid.init(undefined, fullscreenMermaid);
                    const fullscreenSvg = fullscreenMermaid.querySelector('svg');
                    if (fullscreenSvg) {{
                        fullscreenSvg.setAttribute('width', '100%');
                        fullscreenSvg.setAttribute('height', '100%');
                        fullscreenSvg.style.width = '100%';
                        fullscreenSvg.style.height = '100%';
                        fullscreenSvg.style.maxWidth = 'none';
                        fullscreenSvg.style.maxHeight = 'none';
                        applyFullscreenZoom();
                    }}
                }}, 50);
                
                if (document.documentElement.requestFullscreen) {{
                    document.documentElement.requestFullscreen();
                }} else if (document.documentElement.mozRequestFullScreen) {{
                    document.documentElement.mozRequestFullScreen();
                }} else if (document.documentElement.webkitRequestFullscreen) {{
                    document.documentElement.webkitRequestFullscreen();
                }} else if (document.documentElement.msRequestFullscreen) {{
                    document.documentElement.msRequestFullscreen();
                }}
            }} else {{
                // Exit fullscreen mode
                fullscreenContainer.style.display = 'none';
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }} else if (document.mozCancelFullScreen) {{
                    document.mozCancelFullScreen();
                }} else if (document.webkitExitFullscreen) {{
                    document.webkitExitFullscreen();
                }} else if (document.msExitFullscreen) {{
                    document.msExitFullscreen();
                }}
            }}
        }}

        // Listen for browser fullscreen changes
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.addEventListener('mozfullscreenchange', handleFullscreenChange);
        document.addEventListener('MSFullscreenChange', handleFullscreenChange);
        
        function handleFullscreenChange() {{
            if (!document.fullscreenElement && 
                !document.webkitFullscreenElement && 
                !document.mozFullScreenElement && 
                !document.msFullscreenElement) {{
                const fullscreenContainer = document.getElementById('fullscreen-container');
                if (fullscreenContainer.style.display === 'flex') {{
                    fullscreenContainer.style.display = 'none';
                }}
            }}
        }}

        // Adjust SVG size on window resize
        window.addEventListener('resize', function() {{
            const fullscreenContainer = document.getElementById('fullscreen-container');
            if (fullscreenContainer.style.display === 'flex') {{
                const fullscreenSvg = document.getElementById('fullscreen-mermaid').querySelector('svg');
                if (fullscreenSvg) {{
                    fullscreenSvg.setAttribute('width', '100%');
                    fullscreenSvg.setAttribute('height', '100%');
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    except Exception as e:
        print(f"Error generating mermaid diagram: {str(e)}")
        return None

def display_mermaid(mermaid_code: str, height: int = 800) -> Optional[str]:
    """
    Returns the HTML string for the mermaid diagram, or None if it fails.
    The height parameter is used for the main view, but fullscreen will use 100% of the viewport.
    """
    return render_mermaid_code(mermaid_code)
