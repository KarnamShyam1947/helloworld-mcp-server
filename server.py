# from mcp.server.fastmcp import FastMCP

# # Create server
# mcp = FastMCP("LearningMCP")


# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Add two numbers"""
#     return a + b


# @mcp.tool()
# def greet(name: str) -> str:
#     """Greet a user"""
#     return f"Hello, {name}!"


# if __name__ == "__main__":
#     mcp.run(transport="stdio")

from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider
from fastmcp.server.auth.providers.github import GitHubProvider
import os
from starlette.routing import Route
from starlette.responses import HTMLResponse
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    print("Warning: python-dotenv not installed; .env file will not be loaded.\nInstall it with: pip install python-dotenv")

google_auth = GoogleProvider(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    base_url="http://localhost:8000",
    required_scopes=[   
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
)

github_auth = GitHubProvider(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
    base_url="http://localhost:8000",
)


mcp = FastMCP(
    "LearningMCP",
    # auth=github_auth
    auth=google_auth
)


@mcp.tool()
def add(a: int, b: int):
    return a + b


@mcp.tool()
def greet(name: str):
    return f"Hello {name}"


async def provider_picker(request):
    """Serve provider selection page at root."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP OAuth Login</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                padding: 40px;
                max-width: 400px;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .provider-buttons {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .btn {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 14px 20px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 500;
                text-decoration: none;
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .btn-google {
                background-color: #4285F4;
            }
            .btn-google:hover {
                background-color: #357ae8;
            }
            .btn-github {
                background-color: #333;
            }
            .btn-github:hover {
                background-color: #1a1a1a;
            }
            .icon {
                margin-right: 10px;
                font-size: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Sign In</h1>
            <p class="subtitle">Choose your authentication provider</p>
            <div class="provider-buttons">
                <a href="/auth/google/authorize?provider=google" class="btn btn-google">
                    <span class="icon">📧</span>
                    Sign in with Google
                </a>
                <a href="/auth/github/authorize?provider=github" class="btn btn-github">
                    <span class="icon">🐙</span>
                    Sign in with GitHub
                </a>
            </div>
        </div>
    </body>
    </html>
    """)


if __name__ == "__main__":
    # Get the FastMCP HTTP app
    mcp_app = mcp.http_app(
        path="/mcp",
        stateless_http=True,
    )
    
    # Wrap with custom root route
    app = Starlette(
        routes=[
            Route("/", provider_picker, methods=["GET"]),
            Mount("", app=mcp_app),
        ],
        lifespan=mcp_app.router.lifespan_context,
    )
    
    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)