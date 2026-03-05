"""
Nova Smart Browser Engine — Production v2.8.0
===============================================
Advanced Playwright web automation with:
- Persistent sessions & cookies
- Login-aware navigation
- Form filling
- Screenshot capture
- JavaScript execution
- PDF download
"""

import os
import json


class SmartBrowserEngine:
    """
    Enhanced web crawler with session persistence, login support,
    and smart content extraction.
    """

    def __init__(self):
        self._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._session_dir = os.path.join(self._root, "data", "browser_sessions")
        self._screenshots_dir = os.path.join(self._root, "data", "screenshots")
        self._downloads_dir = os.path.join(self._root, "data", "downloads")
        for d in [self._session_dir, self._screenshots_dir, self._downloads_dir]:
            os.makedirs(d, exist_ok=True)
        self.headless = True

    def process(self, input_data: str, health_check: bool = False) -> dict:
        """Contrato unificado para el Orchestrator."""
        if health_check:
            try:
                from playwright.sync_api import sync_playwright
                return {"status": "success", "message": "SmartBrowserEngine listo (Playwright OK)."}
            except ImportError:
                return {"status": "error", "message": "Playwright no instalado."}

        if os.getenv("NOVA_TEST_MODE", "").strip().lower() in {"1", "true", "mock"}:
            return {
                "status": "success",
                "content": f"[MockBrowser] Contenido simulado para: {input_data}",
                "title": "Mock Browser",
                "instructions_for_llm": f"Navegación simulada para: {input_data}",
            }

        if not input_data.startswith(("http://", "https://")):
            return {
                "status": "success",
                "message": "Smart Browser activo. Envía una URL para navegar.",
                "content": "",
                "title": "N/A",
            }

        return self.crawl(input_data)

    def crawl(self, url: str, wait_for: str = None, extract_links: bool = False) -> dict:
        """Navigate to URL with smart content extraction."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"status": "error", "message": "Playwright no instalado. pip install playwright && playwright install chromium"}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self._session_dir,
                    headless=self.headless,
                    viewport={"width": 1920, "height": 1080},
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    accept_downloads=True,
                )
                page = browser.pages[0] if browser.pages else browser.new_page()

                # Block heavy resources for speed
                def route_handler(route, request):
                    if request.resource_type in ["image", "media", "font"]:
                        route.abort()
                    else:
                        route.continue_()

                if self.headless:
                    page.route("**/*", route_handler)

                page.goto(url, wait_until="domcontentloaded", timeout=30000)

                if wait_for:
                    page.wait_for_selector(wait_for, timeout=10000)
                else:
                    page.wait_for_load_state("networkidle", timeout=15000)

                title = page.title()

                # Smart content extraction
                content = page.evaluate("""() => {
                    // Remove scripts, styles, navs, footers, ads
                    const remove = ['script', 'style', 'nav', 'footer', 'header', 'aside',
                                    '.ad', '.ads', '.advertisement', '[role="banner"]',
                                    '[role="navigation"]', '[role="complementary"]'];
                    remove.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => el.remove());
                    });

                    // Get main content area or fall back to body
                    const main = document.querySelector('main, article, [role="main"], .content, #content');
                    return (main || document.body).innerText;
                }""")

                result = {
                    "status": "success",
                    "url": url,
                    "title": title,
                    "content": content.strip()[:8000],
                    "instructions_for_llm": f"Contenido de {url}:\n{content.strip()[:5000]}",
                }

                # Extract links if requested
                if extract_links:
                    links = page.evaluate("""() => {
                        return Array.from(document.querySelectorAll('a[href]'))
                            .map(a => ({text: a.innerText.trim(), href: a.href}))
                            .filter(l => l.text && l.href.startsWith('http'))
                            .slice(0, 30);
                    }""")
                    result["links"] = links

                browser.close()
                return result

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def screenshot(self, url: str, full_page: bool = False) -> dict:
        """Take a screenshot of a webpage."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"status": "error", "message": "Playwright no instalado."}

        try:
            import datetime
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self._session_dir,
                    headless=True,
                    viewport={"width": 1920, "height": 1080},
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                filepath = os.path.join(self._screenshots_dir, filename)

                page.screenshot(path=filepath, full_page=full_page)
                browser.close()

                return {
                    "status": "success",
                    "filepath": filepath,
                    "message": f"Screenshot guardado: {filepath}",
                    "instructions_for_llm": f"Screenshot de {url} guardado en {filepath}",
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fill_form(self, url: str, fields: dict, submit_selector: str = None) -> dict:
        """Navigate to a page and fill form fields."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"status": "error", "message": "Playwright no instalado."}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self._session_dir,
                    headless=False,  # Forms often need visible browser
                    viewport={"width": 1920, "height": 1080},
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)

                for selector, value in fields.items():
                    page.fill(selector, value)

                if submit_selector:
                    page.click(submit_selector)
                    page.wait_for_load_state("networkidle", timeout=10000)

                result_content = page.evaluate("() => document.body.innerText")
                browser.close()

                return {
                    "status": "success",
                    "message": "Formulario completado.",
                    "content": result_content[:3000],
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_js(self, url: str, script: str) -> dict:
        """Execute JavaScript on a page and return the result."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"status": "error", "message": "Playwright no instalado."}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=self._session_dir,
                    headless=True,
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)

                result = page.evaluate(script)
                browser.close()

                return {
                    "status": "success",
                    "result": str(result)[:5000],
                    "message": "JavaScript ejecutado.",
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
