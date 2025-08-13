import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def generate_pdf(html_path, pdf_path):
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()
    url = f"file://{html_path}"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.pdf(path=str(pdf_path), format="A4", print_background=True)
        await browser.close()
    print(f"PDF salvo em: {pdf_path}")

if __name__ == '__main__':
    html_path = Path(__file__).parent.parent.parent / 'reports' / 'srag_report.html'
    pdf_path = Path(__file__).parent.parent.parent / 'reports' / 'srag_report.pdf'
    asyncio.run(generate_pdf(str(html_path), str(pdf_path)))
