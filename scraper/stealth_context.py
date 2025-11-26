# scraper/stealth_context.py
import os
from playwright.sync_api import BrowserContext


STEALTH_JS = r"""
Object.defineProperty(navigator, 'webdriver', {
  get: () => undefined
});

window.chrome = {
  runtime: {},
  app: {isInstalled: false},
  loadTimes: () => {},
  csi: () => {},
};

Object.defineProperty(navigator, 'plugins', {
  get: () => [1, 2, 3, 4, 5],
});

Object.defineProperty(navigator, 'languages', {
  get: () => ['es-AR', 'es', 'en-US']
});

// WebGL fingerprint masking
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function (param) {
  if (param === 37446) return 'Google Inc.';
  if (param === 37447) return 'ANGLE (Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0)';
  return getParameter(param);
};

// Canvas fingerprint masking
const toDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function() {
  return toDataURL.apply(this, arguments);
};
"""

def create_stealth_persistent_context(
    p,
    user_data_dir: str,
    channel: str = "msedge",
    headless: bool = False
) -> BrowserContext:

    args = [
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
    ]

    context = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel=channel,
        headless=headless,
        viewport=None,
        args=args
    )

    # Inyectamos stealth ANTES de cualquier navegación
    context.add_init_script(STEALTH_JS)

    return context
