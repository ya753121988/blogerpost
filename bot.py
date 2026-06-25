import os
from flask import Flask, render_template_string, request, jsonify
import requests
import random

app = Flask(__name__)

# TMDB API Key
TMDB_API_KEY = "7dc544d9253bccc3cfecc1c677f69819"

# Your Ad Direct Links
AD_LINKS = [
    "https://www.effectivecpmnetwork.com/xqmb731x1?key=0267816362fc4320de630e064b317db1",
    "https://www.effectivecpmnetwork.com/qw8kn1x7h?key=5fdb7c5ecd8aff08f9ffb43334a9d3e6",
    "https://www.effectivecpmnetwork.com/vrstnq7p2s?key=257dbfc9920ae1f06a0a7b33cbeb410d",
    "https://www.effectivecpmnetwork.com/tpxm5krbv?key=a9a3e08835e93a54ffdaad1597bfe6cb",
    "https://www.effectivecpmnetwork.com/wsck7gj1?key=2f49c16a80560c9b810503b65da32363",
    "https://www.effectivecpmnetwork.com/iqs1w6v06c?key=19b65cbb2964d6f0a3c934b5ee855f18"
]

UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Movie Post Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #0a0a0a; color: #e5e7eb; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background: #111; border: 1px solid #333; border-radius: 15px; margin-top: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        .form-control, .form-select { background: #1a1a1a; border: 1px solid #444; color: #fff; border-radius: 8px; padding: 10px; }
        .form-control:focus { background: #222; border-color: #3b82f6; color: #fff; box-shadow: none; }
        .search-item { cursor: pointer; transition: 0.3s; margin-bottom: 20px; position: relative; }
        .search-item:hover { transform: translateY(-5px); border: 1px solid #3b82f6; border-radius: 10px; }
        .section-title { background: linear-gradient(90deg, #3b82f6, transparent); padding: 10px 20px; border-radius: 8px; margin: 30px 0 15px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
        
        .quality-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px; }
        .quality-grid div { text-align: center; font-size: 11px; color: #999; }
        
        .season-box { background: #181818; padding: 20px; border-radius: 15px; margin-bottom: 25px; border: 1px solid #222; position: relative; }
        .episode-box { background: #222; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 5px solid #3b82f6; }
        
        .btn-premium { background: linear-gradient(135deg, #3b82f6, #1d4ed8); border: none; font-weight: bold; padding: 12px; border-radius: 10px; transition: 0.3s; }
        .btn-premium:hover { background: #2563eb; transform: scale(1.02); }
        .code-output { background: #000; color: #22c55e; padding: 20px; border-radius: 12px; font-family: 'Courier New', monospace; white-space: pre-wrap; display: none; margin-top: 30px; }
    </style>
</head>
<body>
<div class="container my-5">
    <div class="card p-4">
        <h2 class="text-center text-primary fw-bold mb-4">🎥 BLOGGER POST CREATOR (PRO)</h2>
        
        <!-- Search Section -->
        <div class="row g-2 mb-4">
            <div class="col-md-7"><input type="text" id="query" class="form-control" placeholder="Movie or TV Series Name..."></div>
            <div class="col-md-3">
                <select id="type" class="form-select">
                    <option value="movie">Movie</option>
                    <option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2"><button class="btn btn-primary w-100 fw-bold" onclick="search()">SEARCH</button></div>
        </div>

        <div id="results" class="row"></div>

        <!-- Detail Editor Area -->
        <div id="editor" style="display:none;">
            <div class="section-title">1. Post Basic Info & Visuals</div>
            <div class="row g-3">
                <div class="col-md-8"><label>Title</label><input type="text" id="title" class="form-control"></div>
                <div class="col-md-4"><label>Backdrop Thumbnail URL</label><input type="text" id="backdrop" class="form-control"></div>
                <div class="col-md-4"><label>Language</label><input type="text" id="lang" class="form-control" placeholder="Hindi-English"></div>
                <div class="col-md-4"><label>Release Date</label><input type="text" id="release" class="form-control"></div>
                <div class="col-md-4"><label>Trailer ID (YouTube)</label><input type="text" id="trailer" class="form-control"></div>
                <div class="col-md-12"><label>Storyline</label><textarea id="story" class="form-control" rows="3"></textarea></div>
                <div class="col-md-12"><label>Director Name</label><input type="text" id="director" class="form-control"></div>
            </div>

            <div class="section-title">2. Ad Settings</div>
            <div class="row align-items-center">
                <div class="col-md-4">
                    <label>Ads Per Click (1 - 10)</label>
                    <select id="ad_count" class="form-select">
                        <option value="1">1 Ad</option><option value="2">2 Ads</option>
                        <option value="3">3 Ads</option><option value="4">4 Ads</option>
                        <option value="5" selected>5 Ads</option><option value="6">6 Ads</option>
                        <option value="7">7 Ads</option><option value="8">8 Ads</option>
                        <option value="9">9 Ads</option><option value="10">10 Ads</option>
                    </select>
                </div>
                <div class="col-md-8 text-muted small mt-2">Selected number of ads will open as pop-ups when a user clicks any download link.</div>
            </div>

            <!-- Download Sections -->
            <div id="movie-links-section" style="display:none;">
                <div class="section-title">3. Movie Download Links (8K to 140p)</div>
                <div class="quality-grid" id="m-q-grid">
                    <div>8K<input type="text" data-q="8K" class="form-control mq" placeholder="Link"></div>
                    <div>4K<input type="text" data-q="4K" class="form-control mq" placeholder="Link"></div>
                    <div>2K<input type="text" data-q="2K" class="form-control mq" placeholder="Link"></div>
                    <div>1080p<input type="text" data-q="1080p" class="form-control mq" placeholder="Link"></div>
                    <div>720p<input type="text" data-q="720p" class="form-control mq" placeholder="Link"></div>
                    <div>480p<input type="text" data-q="480p" class="form-control mq" placeholder="Link"></div>
                    <div>360p<input type="text" data-q="360p" class="form-control mq" placeholder="Link"></div>
                    <div>140p<input type="text" data-q="140p" class="form-control mq" placeholder="Link"></div>
                </div>
            </div>

            <div id="series-links-section" style="display:none;">
                <div class="section-title">3. Seasons & Episodes Management</div>
                <div id="seasons-container"></div>
                <button class="btn btn-outline-primary w-100 fw-bold mt-2" onclick="addSeason()">+ ADD NEW SEASON</button>
            </div>

            <button class="btn btn-premium w-100 mt-5 text-white" onclick="generateHTML()">GENERATE BLOGGER HTML</button>
            
            <div id="output" class="code-output"></div>
            <button id="copy-btn" class="btn btn-success w-100 mt-2 fw-bold" style="display:none;" onclick="copyCode()">COPY HTML CODE</button>
        </div>
    </div>
</div>

<script>
let selectedItem = null;
let seasonCounter = 0;

async function search() {
    const q = document.getElementById('query').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let html = '';
    data.results.forEach(item => {
        const title = item.title || item.name;
        const img = item.backdrop_path ? `https://image.tmdb.org/t/p/w500${item.backdrop_path}` : 'https://via.placeholder.com/500x280?text=No+Thumb';
        html += `<div class="col-md-4 search-item text-center" onclick="selectItem('${item.id}', '${t}')">
            <img src="${img}" class="img-fluid rounded">
            <p class="mt-2 fw-bold">${title}</p>
        </div>`;
    });
    document.getElementById('results').innerHTML = html;
}

async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    selectedItem = await res.json();
    
    document.getElementById('title').value = selectedItem.title || selectedItem.name;
    document.getElementById('backdrop').value = `https://image.tmdb.org/t/p/original${selectedItem.backdrop_path}`;
    document.getElementById('release').value = selectedItem.release_date || selectedItem.first_air_date;
    document.getElementById('story').value = selectedItem.overview;
    
    // Director Info
    const director = selectedItem.credits.crew.find(c => c.job === 'Director');
    document.getElementById('director').value = director ? director.name : 'Unknown';

    // Trailer
    const trailer = selectedItem.videos.results.find(v => v.type === 'Trailer');
    document.getElementById('trailer').value = trailer ? trailer.key : '';

    document.getElementById('editor').style.display = 'block';
    document.getElementById('results').innerHTML = '';
    if(type === 'movie') {
        document.getElementById('movie-links-section').style.display = 'block';
        document.getElementById('series-links-section').style.display = 'none';
    } else {
        document.getElementById('movie-links-section').style.display = 'none';
        document.getElementById('series-links-section').style.display = 'block';
    }
}

function addSeason() {
    seasonCounter++;
    const sName = `S${String(seasonCounter).padStart(2, '0')}`;
    const sId = `season_${seasonCounter}`;
    const sDiv = document.createElement('div');
    sDiv.className = 'season-box';
    sDiv.id = sId;
    sDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <input type="text" class="form-control s-title-input w-50 fw-bold text-primary" value="${sName}">
            <button class="btn btn-sm btn-info fw-bold" onclick="addEpisode('${sId}')">+ ADD EPISODE</button>
        </div>
        <div class="ep-container" data-epcount="0"></div>
    `;
    document.getElementById('seasons-container').appendChild(sDiv);
}

function addEpisode(sId) {
    const epContainer = document.querySelector(`#${sId} .ep-container`);
    let epCount = parseInt(epContainer.dataset.epcount) + 1;
    epContainer.dataset.epcount = epCount;
    const epName = `E${String(epCount).padStart(2, '0')}`;
    
    const epDiv = document.createElement('div');
    epDiv.className = 'episode-box';
    epDiv.innerHTML = `
        <input type="text" class="form-control ep-title-input mb-3 fw-bold" value="${epName}">
        <div class="quality-grid">
            <div>8K<input type="text" data-q="8K" class="form-control eq" placeholder="Link"></div>
            <div>4K<input type="text" data-q="4K" class="form-control eq" placeholder="Link"></div>
            <div>2K<input type="text" data-q="2K" class="form-control eq" placeholder="Link"></div>
            <div>1080p<input type="text" data-q="1080p" class="form-control eq" placeholder="Link"></div>
            <div>720p<input type="text" data-q="720p" class="form-control eq" placeholder="Link"></div>
            <div>480p<input type="text" data-q="480p" class="form-control eq" placeholder="Link"></div>
            <div>360p<input type="text" data-q="360p" class="form-control eq" placeholder="Link"></div>
            <div>140p<input type="text" data-q="140p" class="form-control eq" placeholder="Link"></div>
        </div>
    `;
    epContainer.appendChild(epDiv);
}

async function generateHTML() {
    const ad_count = document.getElementById('ad_count').value;
    const basic = {
        title: document.getElementById('title').value,
        backdrop: document.getElementById('backdrop').value,
        lang: document.getElementById('lang').value,
        release: document.getElementById('release').value,
        trailer: document.getElementById('trailer').value,
        story: document.getElementById('story').value,
        director: document.getElementById('director').value,
        type: document.getElementById('type').value,
        ad_count: ad_count
    };

    const movieLinks = [];
    document.querySelectorAll('.mq').forEach(i => { if(i.value) movieLinks.push({ q: i.dataset.q, url: i.value }); });

    const seasons = [];
    document.querySelectorAll('.season-box').forEach(sBox => {
        const sTitle = sBox.querySelector('.s-title-input').value;
        const eps = [];
        sBox.querySelectorAll('.episode-box').forEach(eBox => {
            const eTitle = eBox.querySelector('.ep-title-input').value;
            const eLinks = [];
            eBox.querySelectorAll('.eq').forEach(ei => { if(ei.value) eLinks.push({ q: ei.dataset.q, url: ei.value }); });
            eps.push({ title: eTitle, links: eLinks });
        });
        seasons.push({ title: sTitle, episodes: eps });
    });

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ item: selectedItem, basic, movieLinks, seasons })
    });
    const result = await res.json();
    document.getElementById('output').innerText = result.html;
    document.getElementById('output').style.display = 'block';
    document.getElementById('copy-btn').style.display = 'block';
}

function copyCode() {
    navigator.clipboard.writeText(document.getElementById('output').innerText);
    alert("Blogger HTML Copied!");
}
</script>
</body>
</html>
"""

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
    b = data['basic']
    mLinks = data['movieLinks']
    seasons = data['seasons']
    
    # Cast Slider
    cast_html = ""
    for c in item.get('credits', {}).get('cast', [])[:12]:
        c_img = f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c['profile_path'] else "https://via.placeholder.com/100"
        cast_html += f'<div class="cast-card"><img src="{c_img}"><p>{c["name"]}</p></div>'

    # ScreenShots
    ss_html = ""
    for img in item.get('images', {}).get('backdrops', [])[:6]:
        ss_html += f'<img src="https://image.tmdb.org/t/p/w500{img["file_path"]}">'

    # Ads Script Generation
    ads_js = f"const ads = {AD_LINKS}; const adCount = {b['ad_count']};"
    
    # Movie Links Logic (2 in a row)
    movie_btn_html = ""
    if b['type'] == 'movie':
        movie_btn_html = '<div class="m-dl-grid">'
        for l in mLinks:
            movie_btn_html += f'<a href="javascript:void(0)" onclick="openLink(\'{l["url"]}\')" class="p-btn">{l["q"]} Download</a>'
        movie_btn_html += '</div>'

    # Series Logic (Accordion + Grid)
    series_btn_html = ""
    for i, s in enumerate(seasons):
        series_btn_html += f'<button class="s-btn" onclick="toggleS(\'s{i}\')">📂 {s["title"]} (Show Episodes)</button>'
        series_btn_html += f'<div id="s{i}" class="ep-grid" style="display:none;">'
        for ep in s['episodes']:
            # For episodes, we just create one button that contains all quality links in a simple way or a primary link
            # According to your request: S01 E01 Link (3 in a row)
            # We'll use the first available quality as the primary link
            main_url = ep['links'][0]['url'] if ep['links'] else "#"
            series_btn_html += f'<a href="javascript:void(0)" onclick="openLink(\'{main_url}\')" class="e-btn">{s["title"]} {ep["title"]} Link</a>'
        series_btn_html += '</div>'

    final_html = f"""
<!-- Premium Blogger Post -->
<style>
    .p-wrapper {{ background: #0f172a; color: #f8fafc; padding: 25px; border-radius: 20px; font-family: 'Inter', sans-serif; }}
    .p-thumb {{ width: 100%; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
    .p-title {{ color: #38bdf8; font-size: 35px; font-weight: 900; text-align: center; margin-top: 20px; }}
    .h-head {{ border-left: 5px solid #38bdf8; padding-left: 15px; margin: 35px 0 15px; font-weight: bold; font-size: 20px; color: #fff; text-transform: uppercase; }}
    
    .c-slider {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scrollbar-width: none; }}
    .cast-card {{ min-width: 90px; text-align: center; }}
    .cast-card img {{ width: 75px; height: 75px; border-radius: 50%; border: 3px solid #38bdf8; object-fit: cover; }}
    
    .ss-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .ss-grid img {{ width: 100%; border-radius: 10px; }}
    
    .m-dl-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
    .p-btn {{ background: linear-gradient(90deg, #38bdf8, #2563eb); color: #fff !important; text-align: center; padding: 15px; border-radius: 12px; font-weight: bold; text-decoration: none !important; }}
    
    .s-btn {{ width: 100%; background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 15px; border-radius: 10px; font-weight: bold; margin-bottom: 10px; text-align: left; cursor: pointer; }}
    .ep-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }}
    .e-btn {{ background: #38bdf8; color: #000 !important; font-size: 11px; font-weight: 800; padding: 10px 5px; border-radius: 6px; text-align: center; text-decoration: none !important; }}
    
    .unlock-btn {{ display: block; background: #f59e0b; color: #000 !important; text-align: center; padding: 20px; border-radius: 15px; font-size: 22px; font-weight: 900; cursor: pointer; margin: 30px 0; }}
</style>

<div class="p-wrapper">
    <img src="{b['backdrop']}" class="p-thumb">
    <h1 class="p-title">{b['title']}</h1>
    <p style="text-align:center; opacity:0.7;">📅 {b['release']} | 🌐 {b['lang']} | 🎬 {b['director']}</p>

    <div class="h-head">STORYLINE</div>
    <p style="line-height:1.7; color: #cbd5e1;">{b['story']}</p>

    <div class="h-head">CAST</div>
    <div class="c-slider">{cast_html}</div>

    <div class="h-head">SCREENSHOTS</div>
    <div class="ss-grid">{ss_html}</div>

    <div class="h-head">TRAILER</div>
    <iframe width="100%" height="350" src="https://www.youtube.com/embed/{b['trailer']}" frameborder="0" allowfullscreen style="border-radius:15px;"></iframe>

    <div class="unlock-btn" onclick="document.getElementById('dl-area').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</div>

    <div id="dl-area" style="display:none;">
        <div class="h-head">DOWNLOAD LINKS</div>
        {movie_btn_html}
        {series_btn_html}
    </div>
</div>

<script>
    {ads_js}
    function toggleS(id) {{
        var x = document.getElementById(id);
        x.style.display = (x.style.display === "none") ? "grid" : "none";
    }}
    function openLink(url) {{
        for(let i=0; i<adCount; i++) {{
            window.open(ads[Math.floor(Math.random() * ads.length)], '_blank');
        }}
        window.location.href = url;
    }}
</script>
"""
    return jsonify({"html": final_html})

if __name__ == '__main__':
    app.run(debug=True)
