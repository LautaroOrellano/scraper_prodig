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

// WebGL
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function (param) {
  if (param === 37446) return 'Google Inc.';
  if (param === 37447) return 'ANGLE (Intel HD Graphics)';
  return getParameter(param);
};
"""

def create_stealth_persistent_context(p, user_data_dir, channel="msedge", headless=False) -> BrowserContext:

    args = [
        "--start-maximized",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
    ]

    context = p.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel=channel,
        headless=headless,
        viewport=None,
        args=args
    )

    context.add_init_script(STEALTH_JS)
    return context
