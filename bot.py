import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# TMDB API Key
TMDB_API_KEY = "7dc544d9253bccc3cfecc1c677f69819"

# --- Generator UI ---
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Blogger Post Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #0f172a; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .container { max-width: 1000px; padding-top: 40px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 16px; color: #fff; }
        .search-res { cursor: pointer; transition: 0.3s; margin-bottom: 15px; }
        .search-res:hover { transform: translateY(-5px); }
        .search-res img { border-radius: 12px; border: 2px solid #334155; }
        .form-control, .form-select { background: #0f172a; border: 1px solid #334155; color: #fff; }
        .form-control:focus { background: #0f172a; color: #fff; border-color: #38bdf8; }
        .code-output { background: #000; color: #10b981; padding: 20px; border-radius: 10px; font-family: monospace; max-height: 400px; overflow-y: auto; white-space: pre-wrap; display: none; }
        .btn-sky { background: #38bdf8; color: #000; font-weight: bold; }
        .btn-sky:hover { background: #0ea5e9; }
        .ep-box { background: #334155; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
</head>
<body>
<div class="container pb-5">
    <div class="card p-4">
        <h2 class="text-center mb-4">🚀 Ultimate Movie/Series Post Creator</h2>
        
        <div class="row g-2">
            <div class="col-md-8">
                <input type="text" id="query" class="form-control" placeholder="Search Movie or Web Series...">
            </div>
            <div class="col-md-2">
                <select id="type" class="form-select">
                    <option value="movie">Movie</option>
                    <option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2">
                <button class="btn btn-sky w-100" onclick="search()">Search</button>
            </div>
        </div>

        <div id="results" class="row mt-4"></div>

        <div id="editor" class="mt-5" style="display:none;">
            <hr border="1">
            <h4>Post Details</h4>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label>Language</label>
                    <input type="text" id="lang" class="form-control" placeholder="e.g. Dual Audio (Hindi-English)">
                </div>
            </div>

            <!-- Links for Movies -->
            <div id="movie-links-input">
                <h5>Download Links (Resolution|Link)</h5>
                <textarea id="m_links" class="form-control" rows="3" placeholder="4K|https://link1.com, 1080p|https://link2.com"></textarea>
            </div>

            <!-- Advanced Series Links -->
            <div id="series-links-input" style="display:none;">
                <h5>Series Seasons & Episodes</h5>
                <div id="seasons-container"></div>
                <button class="btn btn-sm btn-outline-info mt-2" onclick="addSeason()">+ Add Season</button>
            </div>

            <button class="btn btn-sky btn-lg w-100 mt-4" onclick="generateHTML()">GENERATE BLOGGER HTML</button>
        </div>

        <div id="output-wrapper" class="mt-5" style="display:none;">
            <div class="d-flex justify-content-between mb-2">
                <h5>Blogger HTML (Copy This)</h5>
                <button class="btn btn-sm btn-success" onclick="copyCode()">Copy Code</button>
            </div>
            <div id="output" class="code-output"></div>
        </div>
    </div>
</div>

<script>
let selectedItem = null;
let seasonCount = 0;

async function search() {
    const q = document.getElementById('query').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let html = '';
    data.results.forEach(item => {
        const title = item.title || item.name;
        const img = item.backdrop_path ? `https://image.tmdb.org/t/p/w500${item.backdrop_path}` : 'https://via.placeholder.com/500x280';
        html += `<div class="col-md-4 search-res" onclick="selectItem('${item.id}', '${t}')">
            <img src="${img}" class="img-fluid">
            <p class="text-center mt-2 small">${title}</p>
        </div>`;
    });
    document.getElementById('results').innerHTML = html;
}

async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    selectedItem = await res.json();
    document.getElementById('editor').style.display = 'block';
    if(type === 'tv') {
        document.getElementById('series-links-input').style.display = 'block';
        document.getElementById('movie-links-input').style.display = 'none';
    } else {
        document.getElementById('series-links-input').style.display = 'none';
        document.getElementById('movie-links-input').style.display = 'block';
    }
}

function addSeason() {
    seasonCount++;
    const div = document.createElement('div');
    div.className = 'ep-box mt-3';
    div.innerHTML = `<h6>Season ${seasonCount}</h6>
        <textarea class="form-control s-data" placeholder="Ep 01: 1080p|link1, 720p|link2\\nEp 02: 1080p|link1"></textarea>`;
    document.getElementById('seasons-container').appendChild(div);
}

async function generateHTML() {
    const lang = document.getElementById('lang').value;
    const m_links = document.getElementById('m_links').value;
    const s_elements = document.querySelectorAll('.s-data');
    const s_links = Array.from(s_elements).map(el => el.value);

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({item: selectedItem, lang, m_links, s_links})
    });
    const data = await res.json();
    document.getElementById('output').innerText = data.html;
    document.getElementById('output').style.display = 'block';
    document.getElementById('output-wrapper').style.display = 'block';
}

function copyCode() {
    navigator.clipboard.writeText(document.getElementById('output').innerText);
    alert("Copied!");
}
</script>
</body>
</html>
"""

# --- Backend Routes ---

@app.route('/')
def index():
    return render_template_string(UI_HTML)

@app.route('/api/search')
def search_api():
    q = request.args.get('q')
    t = request.args.get('type')
    url = f"https://api.themoviedb.org/3/search/{t}?api_key={TMDB_API_KEY}&query={q}"
    return jsonify(requests.get(url).json())

@app.route('/api/details')
def details_api():
    id = request.args.get('id')
    t = request.args.get('type')
    url = f"https://api.themoviedb.org/3/{t}/{id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos,images"
    return jsonify(requests.get(url).json())

@app.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.json
    item = data['item']
    lang = data['lang']
    m_links = data['m_links']
    s_links = data['s_links']

    title = item.get('title') or item.get('name')
    overview = item.get('overview')
    backdrop = f"https://image.tmdb.org/t/p/original{item['backdrop_path']}"
    date = item.get('release_date') or item.get('first_air_date')
    
    # Auto Trailer
    trailer_id = ""
    for v in item.get('videos', {}).get('results', []):
        if v['type'] == 'Trailer' and v['site'] == 'YouTube':
            trailer_id = v['key']
            break

    # Auto Gallery (Backdrops)
    gallery_html = ""
    for img in item.get('images', {}).get('backdrops', [])[:6]:
        gallery_html += f'<img src="https://image.tmdb.org/t/p/w500{img["file_path"]}" alt="Gallery">'

    # Auto Cast Slider
    cast_html = ""
    for c in item.get('credits', {}).get('cast', [])[:12]:
        c_img = f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c['profile_path'] else "https://via.placeholder.com/100"
        cast_html += f'<div class="c-item"><img src="{c_img}"><p>{c["name"]}</p></div>'

    # Download Buttons Logic (Movie)
    movie_dl_html = ""
    if m_links:
        movie_dl_html = '<div class="dl-grid">'
        for l in m_links.split(','):
            if '|' in l:
                q, url = l.split('|')
                movie_dl_html += f'<a href="{url.strip()}" class="dl-btn">Download {q.strip()}</a>'
        movie_dl_html += '</div>'

    # Web Series Accordion Logic
    series_dl_html = ""
    for i, s_data in enumerate(s_links):
        series_dl_html += f'<details class="s-acc"><summary>Season {i+1} (Click to Expand)</summary><div class="s-content">'
        lines = s_data.split('\\n')
        for line in lines:
            if ':' in line:
                ep_name, links = line.split(':', 1)
                series_dl_html += f'<div class="ep-row"><span>{ep_name.strip()}</span><div class="ep-links">'
                for l in links.split(','):
                    if '|' in l:
                        q, url = l.split('|')
                        series_dl_html += f'<a href="{url.strip()}">{q.strip()}</a>'
                series_dl_html += '</div></div>'
        series_dl_html += '</div></details>'

    # --- THE ULTIMATE BLOGGER HTML TEMPLATE ---
    final_html = f"""
<style>
    :root {{ --primary: #38bdf8; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }}
    .p-container {{ background: var(--bg); color: var(--text); padding: 20px; border-radius: 20px; font-family: 'Segoe UI', sans-serif; }}
    .p-thumb {{ width: 100%; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .p-title {{ font-size: 32px; font-weight: 800; text-align: center; margin: 20px 0 5px; color: var(--primary); }}
    .p-info {{ text-align: center; font-size: 14px; opacity: 0.8; margin-bottom: 25px; }}
    .p-head {{ border-left: 4px solid var(--primary); padding-left: 15px; margin: 30px 0 15px; font-size: 20px; font-weight: bold; text-transform: uppercase; }}
    .p-story {{ line-height: 1.7; color: #cbd5e1; text-align: justify; }}
    
    /* Gallery Grid */
    .p-gallery {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 15px; }}
    .p-gallery img {{ width: 100%; border-radius: 8px; transition: 0.3s; }}
    .p-gallery img:hover {{ transform: scale(1.05); }}

    /* Cast Slider */
    .c-slider {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; }}
    .c-slider::-webkit-scrollbar {{ display: none; }}
    .c-item {{ min-width: 90px; text-align: center; }}
    .c-item img {{ width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary); }}
    .c-item p {{ font-size: 11px; margin-top: 5px; color: #94a3b8; font-weight: bold; }}

    /* Download Buttons */
    .dl-section {{ background: var(--card); padding: 20px; border-radius: 15px; margin-top: 30px; }}
    .dl-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
    .dl-btn {{ background: linear-gradient(135deg, #0ea5e9, #2563eb); color: #fff !important; text-align: center; padding: 12px; border-radius: 10px; font-weight: bold; text-decoration: none !important; transition: 0.3s; }}
    .dl-btn:hover {{ transform: scale(1.03); box-shadow: 0 5px 15px rgba(56, 189, 248, 0.4); }}
    
    /* Season Accordion */
    .s-acc {{ background: #334155; margin-bottom: 10px; border-radius: 8px; overflow: hidden; }}
    .s-acc summary {{ padding: 15px; cursor: pointer; font-weight: bold; outline: none; background: #475569; }}
    .s-content {{ padding: 15px; background: #1e293b; }}
    .ep-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #334155; }}
    .ep-links {{ display: flex; gap: 8px; }}
    .ep-links a {{ background: var(--primary); color: #000 !important; padding: 5px 12px; border-radius: 5px; font-size: 12px; font-weight: bold; text-decoration: none !important; }}

    /* Unlock Button Layout */
    .unlock-btn {{ display: block; background: #f59e0b; color: #000 !important; text-align: center; padding: 18px; border-radius: 12px; font-size: 20px; font-weight: 800; cursor: pointer; margin: 20px 0; }}
</style>

<div class="p-container">
    <img src="{backdrop}" class="p-thumb">
    <h1 class="p-title">{title}</h1>
    <div class="p-info">📅 {date} | 🌐 {lang}</div>

    <div class="p-head">The Storyline</div>
    <p class="p-story">{overview}</p>

    <div class="p-head">Star Cast</div>
    <div class="c-slider">{cast_html}</div>

    <div class="p-head">Movie Gallery</div>
    <div class="p-gallery">{gallery_html}</div>

    <div class="p-head">Official Trailer</div>
    <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px;">
        <iframe style="position:absolute;top:0;left:0;width:100%;height:100%;" src="https://www.youtube.com/embed/{trailer_id}" frameborder="0" allowfullscreen></iframe>
    </div>

    <div class="dl-section">
        <div class="p-head" style="margin-top:0;">Download Options</div>
        <div class="unlock-btn" onclick="document.getElementById('dl-area').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</div>
        
        <div id="dl-area" style="display:none;">
            {movie_dl_html}
            {series_dl_html}
        </div>
    </div>
</div>
    """
    return jsonify({"html": final_html})

if __name__ == '__main__':
    app.run(debug=True)
