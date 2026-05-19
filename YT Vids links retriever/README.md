# YT VIDS LINKS RETRIEVER

Simple Python tool to fetch YouTube video URLs for a channel or playlists and export to Excel.

## Prerequisites
- Python 3.9+
- VS Code with Python extension
- Google Cloud project with YouTube Data API v3 enabled
- An API key

## Setup
1. Clone or open this folder in VS Code.
2. Create a virtual environment (recommended):
   python -m venv .venv
   .venv\Scripts\Activate  (Windows PowerShell)
3. Install dependencies:
   pip install -r requirements.txt
4. Create a `.env` file in the project root:
   YOUTUBE_API_KEY=your_api_key_here

## Usage
- Fetch channel uploads:
  python youtube_fetch.py --channel_id UC_x5XG1OV2P6uZZ5FSM9Ttw --output channel_uploads.xlsx

- Fetch one or more playlists:
  python youtube_fetch.py --playlists PLxxxxxx PLyyyyyy --output playlists.xlsx

- Combine channel and playlists:
  python youtube_fetch.py --channel_id UC_xxx --playlists PLaaa PLbbb --output combined.xlsx

Output: Excel workbook with one sheet per query and a metadata sheet.

## Notes
- The script uses API key authentication only.
- It skips private or removed videos (they will not appear in the output).
- If you need date or keyword filters later, they can be added by filtering the DataFrame before export.
