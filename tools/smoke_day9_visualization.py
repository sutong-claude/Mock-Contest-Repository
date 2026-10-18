#!/usr/bin/env python3
"""Chromium smoke for the Day9 offline evidence chart. Requires playwright and /usr/bin/chromium."""
from pathlib import Path
from playwright.sync_api import sync_playwright

html = Path(__file__).resolve().parents[1] / '2026-10-12_CSP-S模拟赛day9/可视化复盘/Day9_失分链与三级分数.html'
text = html.read_text(encoding='utf-8')
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    try:
        for width, height in ((1280, 800), (390, 844)):
            page = browser.new_page(viewport={'width': width, 'height': height})
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            page.set_content(text, wait_until='load')
            assert page.title() == 'Day9 赛时失败因果图与三级得分账本'
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
            assert not errors, errors
            assert len(page.locator('body').inner_text()) > 1200
            assert page.locator('button').count() == 4
            if width == 1280:
                initial = page.locator('body').inner_text()
                for index in (1, 2, 3):
                    page.locator('button').nth(index).click()
                    updated = page.locator('body').inner_text()
                    assert updated != initial, (index, 'button inert')
                    initial = updated
            print(f'PASS chromium {width}px: no JS error, no overflow, controls present')
            page.close()
    finally:
        browser.close()
