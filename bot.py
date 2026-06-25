import os
import json
import base64
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# configuration
TMDB_API_KEY = "7dc544d9253bccc3cfecc1c677f69819"
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
    <title>Blogger Post Engine PRO v6.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --accent: #38bdf8; --bg: #0b0f1a; --card: #161e2e; }
        body { background: var(--bg); color: #e2e8f0; font-family: 'Segoe UI', sans-serif; padding-bottom: 60px; }
        .editor-card { background: var(--card); border: 1px solid #1e293b; border-radius: 15px; margin-top: 25px; padding: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.7); }
        .form-control { background: #0f172a; border: 1px solid #334155; color: #fff; margin-bottom: 12px; }
        .form-control:focus { background: #0f172a; color: #fff; border-color: var(--accent); box-shadow: none; }
        .section-header { border-left: 5px solid var(--accent); padding-left: 15px; margin: 35px 0 15px; font-weight: 900; color: var(--accent); text-transform: uppercase; letter-spacing: 1px; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        
        .season-item { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 15px; margin-bottom: 25px; }
        .episode-item { background: #0f172a; padding: 15px; border-radius: 12px; margin-top: 15px; border-left: 5px solid var(--accent); }
        
        .btn-premium { background: var(--accent); color: #000; font-weight: 900; border: none; padding: 15px; transition: 0.3s; border-radius: 10px; }
        .btn-premium:hover { background: #0ea5e9; transform: scale(1.02); }
        .code-area { background: #000; color: #10b981; padding: 20px; border-radius: 12px; font-family: 'Courier New', monospace; white-space: pre-wrap; margin-top: 15px; border: 1px solid #334155; }
        .preview-box { background: #fff; color: #000; padding: 20px; border-radius: 12px; margin-top: 15px; display: none; overflow-x: hidden; }
        .cast-edit-box { background: #0f172a; padding: 10px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 10px; }
    </style>
</head>
<body>
<div class="container">
    <div class="editor-card">
        <h2 class="text-center fw-bold mb-4">🚀 PRO BLOGGER POST ENGINE</h2>
        
        <!-- Re-Edit Section -->
        <div class="mb-5 p-3 border border-info border-dashed rounded">
            <label class="fw-bold text-info mb-2">RE-EDIT POST (Paste Old Blogger HTML)</label>
            <textarea id="import_data" class="form-control" rows="2" placeholder="Paste your generated code here to edit/add episodes..."></textarea>
            <button class="btn btn-info btn-sm w-100 fw-bold" onclick="importCode()">IMPORT OLD DATA</button>
        </div>

        <div class="row g-2 mb-4">
            <div class="col-md-7"><input type="text" id="query" class="form-control" placeholder="Search Movie or TV Series..."></div>
            <div class="col-md-3">
                <select id="type" class="form-select bg-dark text-white border-secondary">
                    <option value="movie">Movie</option><option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2"><button class="btn btn-premium w-100" onclick="searchTMDB()">SEARCH</button></div>
        </div>

        <div id="results" class="row"></div>

        <!-- Detail Form -->
        <div id="main_editor" style="display:none;">
            <div class="section-header">1. BASIC DETAILS & MAIN THUMBNAIL</div>
            <div class="row g-3">
                <div class="col-md-6"><label>Title</label><input type="text" id="f_title" class="form-control"></div>
                <div class="col-md-6"><label>Main Backdrop (Landscape)</label><input type="text" id="f_backdrop" class="form-control"></div>
                <div class="col-md-4"><label>Language</label><input type="text" id="f_lang" class="form-control"></div>
                <div class="col-md-4"><label>Release Date</label><input type="text" id="f_date" class="form-control"></div>
                <div class="col-md-4"><label>Trailer ID</label><input type="text" id="f_trailer" class="form-control"></div>
                <div class="col-md-12"><label>Storyline</label><textarea id="f_story" class="form-control" rows="4"></textarea></div>
                <div class="col-md-6"><label>Director Name</label><input type="text" id="f_dir_name" class="form-control"></div>
                <div class="col-md-6"><label>Director Image</label><input type="text" id="f_dir_img" class="form-control"></div>
            </div>

            <div class="section-header">2. CAST DETAILS (6 MEMBERS)</div>
            <div id="f_cast_area" class="row g-2"></div>

            <div class="section-header">3. SCREENSHOTS GALLERY (4 IMAGES)</div>
            <div id="f_gallery_area" class="row g-2"></div>

            <div class="section-header">4. ADVERTISEMENT CONTROL</div>
            <div class="col-md-4">
                <label>Pop-up Ads on Link Click</label>
                <select id="f_ad_count" class="form-select bg-dark text-white border-secondary">
                    <script>for(let i=1;i<=10;i++) document.write(`<option value="${i}">${i} Ads per Click</option>`)</script>
                </select>
            </div>

            <div id="movie_links_ui" style="display:none;">
                <div class="section-header">5. MOVIE DOWNLOAD LINKS</div>
                <div class="grid-4" id="m_qualities">
                    ${['8K','4K','2K','1080p','720p','480p','360p','140p'].map(q => `<div>${q}<input type="text" data-q="${q}" class="form-control mq"></div>`).join('')}
                </div>
            </div>

            <div id="series_links_ui" style="display:none;">
                <div class="section-header">5. SEASONS & EPISODES</div>
                <div id="season_wrap"></div>
                <button class="btn btn-outline-info w-100 fw-bold mt-2" onclick="addNewSeason()">+ ADD NEW SEASON</button>
            </div>

            <button class="btn btn-premium w-100 btn-lg mt-5" onclick="generateFinalHTML()">🚀 GENERATE PREMUM BLOGGER POST</button>

            <!-- Final Output -->
            <div id="final_section" class="mt-5" style="display:none;">
                <div class="d-flex gap-3 mb-3">
                    <button class="btn btn-success flex-grow-1 fw-bold py-3" onclick="copyHTML()">COPY HTML CODE</button>
                    <button class="btn btn-warning flex-grow-1 fw-bold py-3" onclick="previewToggle()">PREVIEW POST</button>
                </div>
                <div id="live_preview" class="preview-box"></div>
                <div id="html_code" class="code-area"></div>
            </div>
        </div>
    </div>
</div>

<script>
let sCount = 0;
let fetchedData = null;

async function searchTMDB() {
    const q = document.getElementById('query').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let html = '';
    data.results.forEach(i => {
        html += `<div class="col-md-4 mb-3" onclick="fetchFullDetails('${i.id}', '${t}')" style="cursor:pointer">
            <div class="card bg-dark border-secondary p-1"><img src="https://image.tmdb.org/t/p/w500${i.backdrop_path}" class="img-fluid rounded">
            <p class="text-center small mt-1 mb-0">${i.title || i.name}</p></div></div>`;
    });
    document.getElementById('results').innerHTML = html;
}

async function fetchFullDetails(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    fetchedData = await res.json();
    document.getElementById('results').innerHTML = '';
    document.getElementById('main_editor').style.display = 'block';
    
    // Set Fields
    document.getElementById('f_title').value = fetchedData.title || fetchedData.name;
    document.getElementById('f_backdrop').value = `https://image.tmdb.org/t/p/original${fetchedData.backdrop_path}`;
    document.getElementById('f_date').value = fetchedData.release_date || fetchedData.first_air_date;
    document.getElementById('f_story').value = fetchedData.overview;
    
    const d = fetchedData.credits.crew.find(c => c.job === 'Director');
    document.getElementById('f_dir_name').value = d ? d.name : '';
    document.getElementById('f_dir_img').value = d ? `https://image.tmdb.org/t/p/w185${d.profile_path}` : '';
    
    const t = fetchedData.videos.results.find(v => v.type === 'Trailer');
    document.getElementById('f_trailer').value = t ? t.key : '';

    // Cast Fields
    let castHtml = '';
    fetchedData.credits.cast.slice(0, 6).forEach(c => {
        castHtml += `<div class="col-md-4 cast-edit-box">
            <input type="text" class="form-control form-control-sm c-n" value="${c.name}">
            <input type="text" class="form-control form-control-sm c-i" value="https://image.tmdb.org/t/p/w185${c.profile_path}">
            <input type="hidden" class="c-id" value="${c.id}">
        </div>`;
    });
    document.getElementById('f_cast_area').innerHTML = castHtml;

    // Gallery Fields
    let galHtml = '';
    fetchedData.images.backdrops.slice(0, 4).forEach(img => {
        galHtml += `<div class="col-md-6"><input type="text" class="form-control form-control-sm g-i" value="https://image.tmdb.org/t/p/w500${img.file_path}"></div>`;
    });
    document.getElementById('f_gallery_area').innerHTML = galHtml;

    if(type === 'movie') {
        document.getElementById('movie_links_ui').style.display = 'block';
        document.getElementById('series_links_ui').style.display = 'none';
    } else {
        document.getElementById('movie_links_ui').style.display = 'none';
        document.getElementById('series_links_ui').style.display = 'block';
    }
}

function addNewSeason(name = "") {
    sCount++;
    const sId = `s_${sCount}`;
    const sName = name || `Season ${String(sCount).padStart(2, '0')}`;
    const div = document.createElement('div');
    div.className = 'season-item';
    div.id = sId;
    div.innerHTML = `
        <div class="d-flex gap-2 mb-2">
            <input type="text" class="form-control fw-bold s-title" value="${sName}">
            <button class="btn btn-info btn-sm fw-bold" onclick="addNewEpisode('${sId}')">+ ADD EPISODE</button>
        </div>
        <div class="ep-wrap" data-count="0"></div>`;
    document.getElementById('season_wrap').appendChild(div);
}

function addNewEpisode(sId, name = "", links = {}) {
    const cont = document.querySelector(`#${sId} .ep-wrap`);
    let count = parseInt(cont.dataset.count) + 1;
    cont.dataset.count = count;
    const eName = name || `Episode ${String(count).padStart(2, '0')}`;
    const div = document.createElement('div');
    div.className = 'episode-item';
    div.innerHTML = `
        <input type="text" class="form-control fw-bold ep-title" value="${eName}">
        <div class="grid-4">
            ${['8K','4K','2K','1080p','720p','480p','360p','140p'].map(q => `<div>${q}<input type="text" data-q="${q}" class="form-control eq" value="${links[q] || ''}"></div>`).join('')}
        </div>`;
    cont.appendChild(div);
}

async function generateFinalHTML() {
    const data = {
        title: document.getElementById('f_title').value,
        backdrop: document.getElementById('f_backdrop').value,
        lang: document.getElementById('f_lang').value,
        date: document.getElementById('f_date').value,
        story: document.getElementById('f_story').value,
        dir_name: document.getElementById('f_dir_name').value,
        dir_img: document.getElementById('f_dir_img').value,
        trailer: document.getElementById('f_trailer').value,
        ad_count: document.getElementById('f_ad_count').value,
        type: document.getElementById('type').value,
        cast: [], gallery: [], movieLinks: [], seasons: []
    };
    
    // Get cast with full bio details
    const castEls = document.querySelectorAll('.cast-edit-box');
    for(let el of castEls) {
        const id = el.querySelector('.c-id').value;
        const name = el.querySelector('.c-n').value;
        const img = el.querySelector('.c-i').value;
        const bioRes = await fetch(`/api/person?id=${id}`);
        const bioData = await bioRes.json();
        data.cast.push({
            name, img, 
            bio: bioData.biography ? bioData.biography.replace(/"/g, "'").slice(0, 500) + "..." : "No Biography Available.",
            born: bioData.birthday || "Unknown",
            place: bioData.place_of_birth || "Unknown"
        });
    }

    document.querySelectorAll('.g-i').forEach(i => data.gallery.push(i.value));
    document.querySelectorAll('.mq').forEach(i => { if(i.value) data.movieLinks.push({q: i.dataset.q, url: i.value}); });
    document.querySelectorAll('.season-item').forEach(sb => {
        const eps = [];
        sb.querySelectorAll('.episode-item').forEach(eb => {
            const el = [];
            eb.querySelectorAll('.eq').forEach(ei => { if(ei.value) el.push({q: ei.dataset.q, url: ei.value}); });
            eps.push({name: eb.querySelector('.ep-title').value, links: el});
        });
        data.seasons.push({name: sb.querySelector('.s-title').value, episodes: eps});
    });

    const res = await fetch('/api/generate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    const result = await res.json();
    document.getElementById('html_code').innerText = result.html;
    document.getElementById('live_preview').innerHTML = result.html;
    document.getElementById('final_section').style.display = 'block';
}

function importCode() {
    try {
        const html = document.getElementById('import_data').value;
        const b64 = html.match(/<!--MASTERDATA:(.*)-->/)[1];
        const data = JSON.parse(atob(b64));
        document.getElementById('main_editor').style.display = 'block';
        document.getElementById('f_title').value = data.title;
        document.getElementById('f_backdrop').value = data.backdrop;
        document.getElementById('f_lang').value = data.lang;
        document.getElementById('f_date').value = data.date;
        document.getElementById('f_story').value = data.story;
        document.getElementById('f_dir_name').value = data.dir_name;
        document.getElementById('f_dir_img').value = data.dir_img;
        document.getElementById('f_trailer').value = data.trailer;
        document.getElementById('f_ad_count').value = data.ad_count;
        document.getElementById('type').value = data.type;
        
        if(data.type === 'movie') {
            document.getElementById('movie_links_ui').style.display = 'block';
            data.movieLinks.forEach(l => { const inp = document.querySelector(`.mq[data-q="${l.q}"]`); if(inp) inp.value = l.url; });
        } else {
            document.getElementById('series_links_ui').style.display = 'block';
            document.getElementById('season_wrap').innerHTML = ''; sCount = 0;
            data.seasons.forEach(s => {
                addNewSeason(s.name); const sId = `s_${sCount}`;
                s.episodes.forEach(e => { const lo = {}; e.links.forEach(ln => lo[ln.q] = ln.url); addNewEpisode(sId, e.name, lo); });
            });
        }
        alert("Success! Post Imported and Ready to Edit.");
    } catch(e) { alert("Error! Invalid HTML Code."); }
}

function copyHTML() { navigator.clipboard.writeText(document.getElementById('html_code').innerText); alert("HTML Copied!"); }
function previewToggle() { const p = document.getElementById('live_preview'); p.style.display = p.style.display === 'none' ? 'block' : 'none'; }
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(UI_HTML)

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

@app.route('/api/person')
def person_api():
    id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/person/{id}?api_key={TMDB_API_KEY}"
    return jsonify(requests.get(url).json())

@app.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.json
    json_meta = base64.b64encode(json.dumps(data).encode()).decode()
    
    # Cast with detail triggers
    cast_h = "".join([f'<div class="c-item" onclick="shAc(\'{c["name"]}\',\'{c["img"]}\',\'{c["born"]}\',\'{c["place"]}\',`{c["bio"]}`)"><img src="{c["img"]}"><p>{c["name"]}</p></div>' for c in data['cast']])
    gal_h = "".join([f'<img src="{i}">' for i in data['gallery']])
    
    # MOVIE (2 BTNS PER ROW)
    m_btns = '<div class="btn-grid">'
    if data['type'] == 'movie':
        for l in data['movieLinks']:
            m_btns += f'<a href="javascript:void(0)" onclick="opL(\'{l["url"]}\')" class="btn-main">{l["q"]} Premium Download</a>'
    m_btns += '</div>'

    # SERIES (2 BTNS PER ROW)
    s_btns = '<div class="btn-grid">'
    for i, s in enumerate(data['seasons']):
        s_btns += f'<button class="btn-main s-btn" onclick="tS(\'s{i}\')">📂 {s["name"]}</button>'
    s_btns += '</div>'

    for i, s in enumerate(data['seasons']):
        s_btns += f'<div id="s{i}" class="ep-box" style="display:none;"><div class="btn-grid">'
        for j, ep in enumerate(s['episodes']):
            s_btns += f'<button class="btn-main e-btn" onclick="tE(\'s{i}e{j}\')">🎬 {ep["name"]}</button>'
        s_btns += '</div>'
        for j, ep in enumerate(s['episodes']):
            s_btns += f'<div id="s{i}e{j}" class="q-box" style="display:none;"><div class="btn-grid">'
            for l in ep['links']:
                s_btns += f'<a href="javascript:void(0)" onclick="opL(\'{l["url"]}\')" class="btn-main q-btn">{l["q"]} Link</a>'
            s_btns += '</div></div>'
        s_btns += '</div>'

    blogger_html = f"""
<!--BLOGGER POST START-->
<style>
    .post-card {{ background: #0b0f1a; color: #f1f5f9; padding: 25px; border-radius: 20px; font-family: sans-serif; position: relative; }}
    .post-img {{ width: 100%; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
    .post-title {{ color: #38bdf8; font-size: 30px; font-weight: 900; text-align: center; margin: 25px 0; }}
    .h-line {{ border-left: 5px solid #38bdf8; padding-left: 15px; margin: 30px 0 15px; font-weight: 800; font-size: 18px; color: #fff; }}
    .cast-scroll {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scrollbar-width: none; }}
    .c-item {{ min-width: 95px; text-align: center; cursor: pointer; transition: 0.3s; }}
    .c-item:hover {{ transform: translateY(-5px); }}
    .c-item img {{ width: 75px; height: 75px; border-radius: 50%; border: 3px solid #38bdf8; object-fit: cover; }}
    .gal-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .gal-grid img {{ width: 100%; border-radius: 12px; }}
    .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }}
    .btn-main {{ display: block; background: linear-gradient(135deg, #38bdf8, #2563eb); color: #fff !important; text-align: center; padding: 16px; border-radius: 15px; text-decoration: none !important; font-weight: 800; border: none; cursor: pointer; transition: 0.3s; font-size: 14px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }}
    .btn-main:hover {{ transform: scale(1.03); opacity: 0.9; }}
    .s-btn {{ background: #1e293b; border: 1px solid #38bdf8; }}
    .ep-box, .q-box {{ background: #111827; padding: 15px; border-radius: 15px; border: 1px solid #1e293b; margin-top: 12px; }}
    .e-btn {{ background: #334155; border: 1px solid #475569; }}
    .q-btn {{ background: #38bdf8; color: #000 !important; }}
    .u-btn {{ display: block; background: #fbbf24; color: #000 !important; text-align: center; padding: 20px; border-radius: 15px; font-weight: 900; font-size: 20px; cursor: pointer; margin: 35px 0; border: none; width: 100%; }}
    
    /* Actor Modal Style */
    .ac-modal {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #161e2e; border: 2px solid #38bdf8; width: 90%; max-width: 400px; padding: 20px; border-radius: 15px; z-index: 10000; display: none; box-shadow: 0 0 50px rgba(0,0,0,0.8); }}
    .ac-modal img {{ width: 100px; height: 100px; border-radius: 50%; border: 3px solid #38bdf8; margin: 0 auto 15px; display: block; object-fit: cover; }}
    .ac-modal h3 {{ text-align: center; color: #38bdf8; margin-bottom: 5px; }}
    .ac-modal p {{ font-size: 13px; line-height: 1.5; text-align: justify; color: #cbd5e1; max-height: 200px; overflow-y: auto; }}
    .ac-close {{ background: #38bdf8; color: #000; font-weight: bold; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 15px; }}
</style>

<div class="post-card">
    <img src="{data['backdrop']}" class="post-img">
    <h1 class="post-title">{data['title']}</h1>
    <p style="text-align:center; opacity:0.8;">📅 {data['date']} | 🌐 {data['lang']} | 🎥 {data['dir_name']}</p>
    <div class="h-line">THE STORYLINE</div>
    <p style="line-height:1.7; color:#94a3b8; text-align: justify;">{data['story']}</p>
    <div class="h-line">CAST MEMBERS (CLICK TO READ DETAILS)</div>
    <div class="cast-scroll">{cast_h}</div>
    <div class="h-line">GALLERY / SCREENSHOTS</div>
    <div class="gal-grid">{gal_h}</div>
    <div class="h-line">OFFICIAL TRAILER</div>
    <iframe width="100%" height="350" src="https://www.youtube.com/embed/{data['trailer']}" frameborder="0" allowfullscreen style="border-radius:15px; border: 2px solid #1e293b;"></iframe>
    <button class="u-btn" onclick="document.getElementById('dl-area').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</button>
    <div id="dl-area" style="display:none;">
        <div class="h-line">DOWNLOAD OPTIONS</div>
        {m_btns if data['type']=='movie' else s_btns}
    </div>
</div>

<!-- Actor Detail Modal -->
<div id="ac-modal" class="ac-modal">
    <img id="ac-img" src="">
    <h3 id="ac-name"></h3>
    <p id="ac-meta" style="text-align:center; font-weight:bold; color:#fff; font-size:11px;"></p>
    <p id="ac-bio"></p>
    <button class="ac-close" onclick="document.getElementById('ac-modal').style.display='none'">CLOSE DETAILS</button>
</div>

<script>
    const ads = {AD_LINKS}; const adC = {data['ad_count']};
    function tS(id) {{ document.querySelectorAll('.ep-box').forEach(el => {{ if(el.id !== id) el.style.display = 'none'; }}); var x = document.getElementById(id); x.style.display = x.style.display==='none'?'block':'none'; }}
    function tE(id) {{ document.querySelectorAll('.q-box').forEach(el => {{ if(el.id !== id) el.style.display = 'none'; }}); var x = document.getElementById(id); x.style.display = x.style.display==='none'?'block':'none'; }}
    function opL(u) {{ for(let i=0; i<adC; i++) {{ window.open(ads[Math.floor(Math.random()*ads.length)], '_blank'); }} window.location.href = u; }}
    function shAc(n,i,b,p,bio) {{ 
        document.getElementById('ac-name').innerText = n;
        document.getElementById('ac-img').src = i;
        document.getElementById('ac-meta').innerText = "Born: "+b+" | Place: "+p;
        document.getElementById('ac-bio').innerText = bio;
        document.getElementById('ac-modal').style.display = 'block';
    }}
</script>
<!--MASTERDATA:{json_meta}-->
"""
    return jsonify({"html": blogger_html})

if __name__ == '__main__':
    app.run(debug=True)
