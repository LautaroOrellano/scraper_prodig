# scraper/stealth_context.py
import random
import time
from typing import Optional, Dict
from playwright.sync_api import Playwright, sync_playwright, BrowserContext
import json

COMMON_USER_AGENTS = [
    # algunas UA modernas (edge/chrome/firefox) — extendé si querés
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/120.0.0.0"
]

STEALTH_SCRIPT = r"""
// Stealth-ish init script: patch navigator and some fingerprint surfaces
(() => {
  try {
    // navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', { get: () => false, configurable: true });

    // languages
    if (navigator.languages === undefined) {
      Object.defineProperty(navigator, 'languages', { get: () => ['es-ES','es'] });
    }

    // permissions: ensure query('notifications') behaves normally
    const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
    if (originalQuery) {
      window.navigator.permissions.__proto__.query = function(parameters) {
        if (parameters && parameters.name === 'notifications') {
          return Promise.resolve({ state: Notification.permission });
        }
        return originalQuery(parameters);
      };
    }

    // plugins + mimeTypes spoof (small realistic set)
    const fakePlugins = [
      { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }
    ];
    const fakeMimeTypes = [
      { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format', enabledPlugin: fakePlugins[0] }
    ];

    try {
      Object.defineProperty(navigator, 'plugins', { get: () => fakePlugins });
      Object.defineProperty(navigator, 'mimeTypes', { get: () => fakeMimeTypes });
    } catch (e) {}

    // hardwareConcurrency & deviceMemory
    try { Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 }); } catch(e) {}
    try { Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 }); } catch(e) {}

    // platform
    try { Object.defineProperty(navigator, 'platform', { get: () => 'Win32' }); } catch(e) {}

    // WebGL / canvas fuzz: override to reduce perfect fingerprinting
    const toBlobOrig = HTMLCanvasElement.prototype.toBlob;
    HTMLCanvasElement.prototype.toBlob = function() {
      // small noise injected into canvas rendering data by drawing a transparent line
      try {
        const ctx = this.getContext('2d');
        if (ctx) {
          ctx.globalAlpha = 0.0001;
          ctx.fillRect(0, 0, 1, 1);
        }
      } catch (e) {}
      return toBlobOrig.apply(this, arguments);
    };

    // minor navigator.userAgent patch handled by context option usually
  } catch (e) {
    // silence
  }
})();
"""

def random_user_agent():
    return random.choice(COMMON_USER_AGENTS)

def coherent_locale_for_ua(ua: str):
    # Simplificado: devolvemos locale acorde a UA
    if "Macintosh" in ua:
        return ("en-US", "America/Los_Angeles")
    if "Firefox" in ua:
        return ("en-US", "America/Chicago")
    if "Edg" in ua or "Chrome" in ua:
        return ("es-AR", "America/Argentina/Buenos_Aires")
    return ("es-ES", "Europe/Madrid")

def create_stealth_persistent_context(
    playwright: Playwright,
    user_data_dir: str,
    channel: str = "msedge",
    headless: bool = False,
    proxy: Optional[Dict] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    viewport: Optional[Dict] = None
) -> BrowserContext:
    """
    Crea un contexto persistente stealth-ready para scraping masivo.
    user_data_dir: ruta de perfil (persistencia de cookies)
    channel: "msedge" o "chrome"
    proxy: dict como {"server":"http://ip:port","username":...,"password":...} opcional
    extra_headers: headers adicionales a setear
    viewport: si querés forzar viewport, por defecto None -> maximized via args
    """
    ua = random_user_agent()
    accept_language, timezone = coherent_locale_for_ua(ua)

    launch_args = [
        '--start-maximized',
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage',
    ]

    # Proxy en launch args si se suministra (opcional)
    browser_type = playwright.chromium

    # Usamos launch_persistent_context para mantener cookies
    context = browser_type.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel=channel,
        headless=headless,
        args=launch_args,
        viewport=viewport or None,
        user_agent=ua,
        locale=accept_language,
        # podrías pasar timezone_id si quisieras, lo seteo después
    )

    # Extra HTTP headers
    headers = {
        "Accept-Language": accept_language,
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate"
    }
    if extra_headers:
        headers.update(extra_headers)
    context.set_extra_http_headers(headers)

    # Inyectamos script de stealth
    context.add_init_script(STEALTH_SCRIPT)

    # Set timezone (Playwright tiene method - use evaluate on page when created)
    # También podemos inyectar un pequeño script para sincronizar timezone+language en cada page
    context.add_init_script(
        "(() => { try { Intl.DateTimeFormat = Intl.DateTimeFormat; } catch(e){} })();"
    )

    return context

# --- helpers para uso común ---
def safe_sleep_between_profiles(min_s=1.2, max_s=2.6):
    time.sleep(random.uniform(min_s, max_s))

def politely_visit_profile(page, url):
    """
    Visitá un perfil con small backoffs y scrolls controlados.
    """
    page.goto(url, timeout=30000)
    # Esperar contenido básico
    page.wait_for_timeout(600)  # 0.6s
    # scrolls controlados (rápidos a nivel HTTP)
    for _ in range(5):
        page.mouse.wheel(0, 1200)
        page.wait_for_timeout(200)  # 0.2s
    page.wait_for_timeout(300)

# Ejemplo de uso rápido:
if __name__ == "__main__":
    with sync_playwright() as pw:
        ctx = create_stealth_persistent_context(pw, user_data_dir="./profile", headless=False)
        page = ctx.new_page()
        page.goto("https://www.instagram.com/")
        print("URL actual:", page.url)
        time.sleep(3)
        ctx.close()
