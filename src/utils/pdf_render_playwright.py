import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_pdf(html_path, pdf_path):
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()
    if not html_path.exists():
        logger.error(f"HTML file not found: {html_path}")
        return False
    try:
        url = f"file://{html_path}"
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.pdf(path=str(pdf_path), format="A4", print_background=True)
            await browser.close()
        logger.info(f"PDF successfully saved at: {pdf_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return False
