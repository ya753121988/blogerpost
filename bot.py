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
    <title>Ultimate Blogger Engine v7.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --accent: #38bdf8; --bg: #0b0f1a; --card: #161e2e; }
        body { background: var(--bg); color: #e2e8f0; font-family: 'Inter', sans-serif; padding-bottom: 70px; }
        .editor-card { background: var(--card); border: 1px solid #1e293b; border-radius: 15px; margin-top: 25px; padding: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); }
        .form-control { background: #0f172a; border: 1px solid #334155; color: #fff; margin-bottom: 15px; }
        .form-control:focus { background: #0f172a; color: #fff; border-color: var(--accent); box-shadow: none; }
        .section-header { border-left: 6px solid var(--accent); padding-left: 15px; margin: 40px 0 20px; font-weight: 900; color: var(--accent); text-transform: uppercase; letter-spacing: 2px; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        
        .season-item { background: #1e293b; border: 2px solid #334155; padding: 25px; border-radius: 20px; margin-bottom: 30px; }
        .episode-item { background: #0f172a; padding: 20px; border-radius: 15px; margin-top: 15px; border-left: 5px solid var(--accent); }
        
        .btn-prem { background: var(--accent); color: #000; font-weight: 900; border: none; padding: 18px; border-radius: 12px; transition: 0.3s; }
        .btn-prem:hover { background: #0ea5e9; transform: translateY(-3px); }
        .code-display { background: #000; color: #10b981; padding: 20px; border-radius: 15px; font-family: 'Courier New', monospace; white-space: pre-wrap; margin-top: 20px; border: 1px solid #334155; }
        .p-box { background: #fff; color: #000; padding: 25px; border-radius: 15px; margin-top: 20px; display: none; }
    </style>
</head>
<body>
<div class="container">
    <div class="editor-card">
        <h2 class="text-center fw-bold mb-4 text-primary">🎬 PRO BLOGGER ENGINE v7.0</h2>
        
        <!-- Re-Edit Section -->
        <div class="mb-5 p-4 border border-info border-dashed rounded text-center">
            <h5 class="text-info">IMPORT & RE-EDIT PREVIOUS POST</h5>
            <textarea id="import_input" class="form-control" rows="2" placeholder="Paste your generated code here..."></textarea>
            <button class="btn btn-info btn-sm w-100 fw-bold" onclick="importFromHTML()">IMPORT OLD POST</button>
        </div>

        <div class="row g-3 mb-5">
            <div class="col-md-7"><input type="text" id="search_q" class="form-control" placeholder="Search Movie/Series Name..."></div>
            <div class="col-md-3">
                <select id="search_t" class="form-select bg-dark text-white border-secondary">
                    <option value="movie">Movie</option><option value="tv">Web Series</option>
                </select>
            </div>
            <div class="col-md-2"><button class="btn btn-prem w-100" onclick="searchTMDB()">SEARCH</button></div>
        </div>

        <div id="search_results" class="row"></div>

        <!-- Editor Form -->
        <div id="full_editor" style="display:none;">
            <div class="section-header">1. BASIC CONTENT & THUMBNAILS</div>
            <div class="row g-3">
                <div class="col-md-6"><label>Title</label><input type="text" id="e_title" class="form-control"></div>
                <div class="col-md-6"><label>Main Backdrop (Landscape)</label><input type="text" id="e_backdrop" class="form-control"></div>
                <div class="col-md-4"><label>Language</label><input type="text" id="e_lang" class="form-control"></div>
                <div class="col-md-4"><label>Release Date</label><input type="text" id="e_date" class="form-control"></div>
                <div class="col-md-4"><label>Trailer ID (Youtube)</label><input type="text" id="e_trailer" class="form-control"></div>
                <div class="col-md-12"><label>Storyline</label><textarea id="e_story" class="form-control" rows="4"></textarea></div>
                <div class="col-md-6"><label>Director Name</label><input type="text" id="e_dir_name" class="form-control"></div>
                <div class="col-md-6"><label>Director Profile Image</label><input type="text" id="e_dir_img" class="form-control"></div>
            </div>

            <div class="section-header">2. CAST (NAYOK/NAYIKA) - ALL DETAILS</div>
            <div id="e_cast_list" class="row g-3"></div>

            <div class="section-header">3. ALL LANDSCAPE GALLERY IMAGES</div>
            <div id="e_gal_list" class="row g-2"></div>

            <div class="section-header">4. ADVERTISEMENT SETTINGS</div>
            <div class="col-md-4">
                <label>Number of Ads per Click (1-10)</label>
                <select id="e_ad_count" class="form-select bg-dark text-white border-secondary">
                    <script>for(let i=1;i<=10;i++) document.write(`<option value="${i}">${i} Ads</option>`)</script>
                </select>
            </div>

            <!-- Movie UI -->
            <div id="movie_ui" style="display:none;">
                <div class="section-header">5. MOVIE DOWNLOAD QUALITIES</div>
                <div class="grid-4">
                    ${['8K','4K','2K','1080p','720p','480p','360p','140p'].map(q => `<div>${q}<input type="text" data-q="${q}" class="form-control m_q"></div>`).join('')}
                </div>
            </div>

            <!-- Series UI -->
            <div id="series_ui" style="display:none;">
                <div class="section-header">5. WEB SERIES (SEASONS & EPISODES)</div>
                <div id="season_wrap"></div>
                <button class="btn btn-outline-info w-100 fw-bold mt-4" onclick="addSeason()">+ ADD NEW SEASON</button>
            </div>

            <button class="btn btn-prem w-100 btn-lg mt-5 py-3" onclick="generateCode()">🚀 GENERATE PERFECT BLOGGER HTML</button>

            <!-- Result -->
            <div id="result_area" class="mt-5" style="display:none;">
                <div class="d-flex gap-3 mb-3">
                    <button class="btn btn-success flex-grow-1 fw-bold py-3" onclick="copyCode()">COPY CODE</button>
                    <button class="btn btn-warning flex-grow-1 fw-bold py-3" onclick="togglePreview()">PREVIEW POST</button>
                </div>
                <div id="preview_content" class="p-box"></div>
                <div id="code_content" class="code-display"></div>
            </div>
        </div>
    </div>
</div>

<script>
let seasonIdx = 0;
let apiData = null;

async function searchTMDB() {
    const q = document.getElementById('search_q').value;
    const t = document.getElementById('search_t').value;
    const res = await fetch(`/api/search?q=${q}&type=${t}`);
    const data = await res.json();
    let h = '';
    data.results.forEach(i => {
        h += `<div class="col-md-4 mb-3" onclick="selectItem('${i.id}', '${t}')" style="cursor:pointer">
            <div class="card bg-dark border-secondary p-1"><img src="https://image.tmdb.org/t/p/w500${i.backdrop_path}" class="img-fluid rounded">
            <p class="text-center small mt-1 mb-0">${i.title || i.name}</p></div></div>`;
    });
    document.getElementById('search_results').innerHTML = h;
}

async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    apiData = await res.json();
    document.getElementById('search_results').innerHTML = '';
    document.getElementById('full_editor').style.display = 'block';
    
    document.getElementById('e_title').value = apiData.title || apiData.name;
    document.getElementById('e_backdrop').value = `https://image.tmdb.org/t/p/original${apiData.backdrop_path}`;
    document.getElementById('e_date').value = apiData.release_date || apiData.first_air_date;
    document.getElementById('e_story').value = apiData.overview;
    
    const d = apiData.credits.crew.find(c => c.job === 'Director');
    document.getElementById('e_dir_name').value = d ? d.name : '';
    document.getElementById('e_dir_img').value = d ? `https://image.tmdb.org/t/p/w185${d.profile_path}` : '';
    
    const t = apiData.videos.results.find(v => v.type === 'Trailer');
    document.getElementById('e_trailer').value = t ? t.key : '';

    // Cast 
    let cH = '';
    apiData.credits.cast.slice(0, 6).forEach(c => {
        cH += `<div class="col-md-4"><div class="p-2 border border-secondary rounded">
            <input type="text" class="form-control form-control-sm cn" value="${c.name}">
            <input type="text" class="form-control form-control-sm ci" value="https://image.tmdb.org/t/p/w185${c.profile_path}">
            <input type="hidden" class="cid" value="${c.id}">
        </div></div>`;
    });
    document.getElementById('e_cast_list').innerHTML = cH;

    // Gallery (All backdrops)
    let gH = '';
    apiData.images.backdrops.slice(0, 8).forEach(img => {
        gH += `<div class="col-md-6"><input type="text" class="form-control form-control-sm gi" value="https://image.tmdb.org/t/p/original${img.file_path}"></div>`;
    });
    document.getElementById('e_gal_list').innerHTML = gH;

    if(type === 'movie') {
        document.getElementById('movie_ui').style.display = 'block';
        document.getElementById('series_ui').style.display = 'none';
    } else {
        document.getElementById('movie_ui').style.display = 'none';
        document.getElementById('series_ui').style.display = 'block';
    }
}

function addSeason(name = "") {
    seasonIdx++;
    const sId = `s_${seasonIdx}`;
    const sName = name || `Season ${String(seasonIdx).padStart(2, '0')}`;
    const d = document.createElement('div');
    d.className = 'season-item';
    d.id = sId;
    d.innerHTML = `<div class="d-flex gap-3 mb-3"><input type="text" class="form-control fw-bold st" value="${sName}">
        <button class="btn btn-info fw-bold" onclick="addEpisode('${sId}')">+ ADD EPISODE</button></div><div class="ep-wrap" data-count="0"></div>`;
    document.getElementById('season_wrap').appendChild(d);
}

function addEpisode(sId, name = "", links = {}) {
    const wrap = document.querySelector(`#${sId} .ep-wrap`);
    let count = parseInt(wrap.dataset.count) + 1;
    wrap.dataset.count = count;
    const eName = name || `Episode ${String(count).padStart(2, '0')}`;
    const d = document.createElement('div');
    d.className = 'episode-item';
    d.innerHTML = `<input type="text" class="form-control fw-bold et mb-2" value="${eName}">
        <div class="grid-4">${['8K','4K','2K','1080p','720p','480p','360p','140p'].map(q => `<div>${q}<input type="text" data-q="${q}" class="form-control eq" value="${links[q] || ''}"></div>`).join('')}</div>`;
    wrap.appendChild(d);
}

async function generateCode() {
    const castData = [];
    const castEls = document.querySelectorAll('.cid');
    for(let i=0; i<castEls.length; i++){
        const res = await fetch(`/api/person?id=${castEls[i].value}`);
        const p = await res.json();
        const bestWork = p.combined_credits.cast.sort((a,b) => b.vote_count - a.vote_count).slice(0,5).map(m => m.title || m.name).join(', ');
        castData.push({
            name: document.querySelectorAll('.cn')[i].value,
            img: document.querySelectorAll('.ci')[i].value,
            born: p.birthday || 'Unknown',
            place: p.place_of_birth || 'Unknown',
            bio: p.biography ? p.biography.slice(0, 600).replace(/'/g, "") + "..." : "No bio available.",
            count: p.combined_credits.cast.length,
            best: bestWork
        });
    }

    const data = {
        title: document.getElementById('e_title').value,
        backdrop: document.getElementById('e_backdrop').value,
        lang: document.getElementById('e_lang').value,
        date: document.getElementById('e_date').value,
        story: document.getElementById('e_story').value,
        dir_name: document.getElementById('e_dir_name').value,
        dir_img: document.getElementById('e_dir_img').value,
        trailer: document.getElementById('e_trailer').value,
        ad_count: document.getElementById('e_ad_count').value,
        type: document.getElementById('search_t').value,
        cast: castData,
        gallery: Array.from(document.querySelectorAll('.gi')).map(i => i.value),
        movieLinks: Array.from(document.querySelectorAll('.m_q')).filter(i => i.value).map(i => ({q: i.dataset.q, url: i.value})),
        seasons: Array.from(document.querySelectorAll('.season-item')).map(s => ({{
            name: s.querySelector('.st').value,
            episodes: Array.from(s.querySelectorAll('.episode-item')).map(e => ({{
                name: e.querySelector('.et').value,
                links: Array.from(e.querySelectorAll('.eq')).filter(i => i.value).map(i => ({{q: i.dataset.q, url: i.value}}))
            }}))
        }}))
    };

    const finalRes = await fetch('/api/generate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    const finalData = await finalRes.json();
    document.getElementById('code_content').innerText = finalData.html;
    document.getElementById('preview_content').innerHTML = finalData.html;
    document.getElementById('result_area').style.display = 'block';
}

function importFromHTML() {
    try {
        const raw = document.getElementById('import_input').value;
        const meta = JSON.parse(atob(raw.match(/<!--MASTERMETA:(.*)-->/)[1]));
        document.getElementById('full_editor').style.display = 'block';
        document.getElementById('e_title').value = meta.title;
        document.getElementById('e_backdrop').value = meta.backdrop;
        document.getElementById('e_lang').value = meta.lang;
        document.getElementById('e_date').value = meta.date;
        document.getElementById('e_story').value = meta.story;
        document.getElementById('e_dir_name').value = meta.dir_name;
        document.getElementById('e_dir_img').value = meta.dir_img;
        document.getElementById('e_trailer').value = meta.trailer;
        document.getElementById('e_ad_count').value = meta.ad_count;
        document.getElementById('search_t').value = meta.type;
        
        if(meta.type === 'movie') {
            document.getElementById('movie_ui').style.display = 'block';
            meta.movieLinks.forEach(l => { const i = document.querySelector(`.m_q[data-q="${l.q}"]`); if(i) i.value = l.url; });
        } else {
            document.getElementById('series_ui').style.display = 'block';
            document.getElementById('season_wrap').innerHTML = ''; seasonIdx = 0;
            meta.seasons.forEach(s => {
                addSeason(s.name); const sId = `s_${seasonIdx}`;
                s.episodes.forEach(e => { const lObj = {}; e.links.forEach(ln => lObj[ln.q] = ln.url); addEpisode(sId, e.name, lObj); });
            });
        }
        alert("Imported Successfully!");
    } catch(e) { alert("Invalid Code!"); }
}

function copyCode() { navigator.clipboard.writeText(document.getElementById('code_content').innerText); alert("Copied!"); }
function togglePreview() { const p = document.getElementById('preview_content'); p.style.display = p.style.display === 'none' ? 'block' : 'none'; }
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(UI_HTML)

@app.route('/api/search')
def search_api():
    q = request.args.get('q'); t = request.args.get('type')
    url = f"https://api.themoviedb.org/3/search/{t}?api_key={TMDB_API_KEY}&query={q}"
    return jsonify(requests.get(url).json())

@app.route('/api/details')
def details_api():
    id = request.args.get('id'); t = request.args.get('type')
    url = f"https://api.themoviedb.org/3/{t}/{id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos,images"
    return jsonify(requests.get(url).json())

@app.route('/api/person')
def person_api():
    id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/person/{id}?api_key={TMDB_API_KEY}&append_to_response=combined_credits"
    return jsonify(requests.get(url).json())

@app.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.json
    meta_b64 = base64.b64encode(json.dumps(data).encode()).decode()
    
    # Cast 
    cast_h = "".join([f'<div class="c-item" onclick="opAc(\'{c["name"]}\',\'{c["img"]}\',\'{c["born"]}\',\'{c["place"]}\',\'{c["count"]}\',\'{c["best"]}\',`{c["bio"]}`)"><img src="{c["img"]}"><p>{c["name"]}</p></div>' for c in data['cast']])
    gal_h = "".join([f'<img src="{i}">' for i in data['gallery']])
    
    # Movie 2-Grid
    m_btns = '<div class="btn-grid">'
    if data['type'] == 'movie':
        for l in data['movieLinks']:
            m_btns += f'<a href="javascript:void(0)" onclick="go(\'{l["url"]}\')" class="p-btn">{l["q"]} Download</a>'
    m_btns += '</div>'

    # Series 2-Grid
    s_btns = '<div class="btn-grid">'
    for i, s in enumerate(data['seasons']):
        s_btns += f'<button class="p-btn s-btn" onclick="tS(\'s{i}\')">📂 {s["name"]}</button>'
    s_btns += '</div>'

    for i, s in enumerate(data['seasons']):
        s_btns += f'<div id="s{i}" class="ep-box" style="display:none;"><div class="btn-grid">'
        for j, e in enumerate(s['episodes']):
            s_btns += f'<button class="p-btn e-btn" onclick="tE(\'s{i}e{j}\')">🎬 {e["name"]}</button>'
        s_btns += '</div>'
        for j, e in enumerate(s['episodes']):
            s_btns += f'<div id="s{i}e{j}" class="q-box" style="display:none;"><div class="btn-grid">'
            for l in e['links']:
                s_btns += f'<a href="javascript:void(0)" onclick="go(\'{l["url"]}\')" class="p-btn q-btn">{l["q"]} Link</a>'
            s_btns += '</div></div>'
        s_btns += '</div>'

    blogger_html = f"""
<!--MASTERPOST-->
<style>
    .p-wrapper {{ background: #0b0f1a; color: #f1f5f9; padding: 25px; border-radius: 20px; font-family: sans-serif; position: relative; }}
    .p-thumb {{ width: 100%; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.7); }}
    .p-title {{ color: #38bdf8; font-size: 32px; font-weight: 900; text-align: center; margin: 25px 0; }}
    .p-head {{ border-left: 6px solid #38bdf8; padding-left: 15px; margin: 35px 0 15px; font-weight: 800; font-size: 19px; color: #fff; }}
    .c-scroll {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scrollbar-width: none; }}
    .c-item {{ min-width: 95px; text-align: center; cursor: pointer; transition: 0.3s; }}
    .c-item img {{ width: 80px; height: 80px; border-radius: 50%; border: 3px solid #38bdf8; object-fit: cover; }}
    .g-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .g-grid img {{ width: 100%; border-radius: 12px; }}
    .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }}
    .p-btn {{ display: block; background: linear-gradient(135deg, #38bdf8, #2563eb); color: #fff !important; text-align: center; padding: 16px; border-radius: 15px; text-decoration: none !important; font-weight: 800; border: none; cursor: pointer; font-size: 14px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }}
    .s-btn {{ background: #1e293b; border: 1px solid #38bdf8; }}
    .ep-box, .q-box {{ background: #111827; padding: 15px; border-radius: 15px; border: 1px solid #1e293b; margin-top: 15px; }}
    .e-btn {{ background: #334155; border: 1px solid #475569; }}
    .q-btn {{ background: #38bdf8; color: #000 !important; }}
    .un-btn {{ display: block; background: #fbbf24; color: #000 !important; text-align: center; padding: 22px; border-radius: 15px; font-weight: 900; font-size: 20px; cursor: pointer; margin: 40px 0; border: none; width: 100%; }}
    
    /* Actor Modal */
    .ac-m {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #161e2e; border: 3px solid #38bdf8; width: 90%; max-width: 450px; padding: 25px; border-radius: 20px; z-index: 99999; display: none; color: #fff; box-shadow: 0 0 100px rgba(0,0,0,0.9); }}
    .ac-m img {{ width: 120px; height: 120px; border-radius: 50%; border: 4px solid #38bdf8; margin: 0 auto 20px; display: block; object-fit: cover; }}
    .ac-m h2 {{ text-align: center; color: #38bdf8; margin-bottom: 10px; font-weight: 900; }}
    .ac-m p {{ font-size: 14px; line-height: 1.6; text-align: justify; margin-bottom: 10px; color: #cbd5e1; max-height: 200px; overflow-y: auto; }}
    .ac-close {{ background: #38bdf8; color: #000; font-weight: 900; border: none; padding: 12px; border-radius: 10px; cursor: pointer; width: 100%; }}
</style>

<div class="p-wrapper">
    <img src="{data['backdrop']}" class="p-thumb">
    <h1 class="p-title">{data['title']}</h1>
    <p style="text-align:center; opacity:0.8;">📅 {data['date']} | 🌐 {data['lang']} | 🎥 {data['dir_name']}</p>
    <div class="p-head">STORYLINE</div>
    <p style="line-height:1.7; color:#94a3b8; text-align: justify;">{data['story']}</p>
    <div class="p-head">STAR CAST (CLICK TO READ BIO)</div>
    <div class="c-scroll">{cast_h}</div>
    <div class="p-head">SCREENSHOTS GALLERY</div>
    <div class="g-grid">{gal_h}</div>
    <div class="p-head">OFFICIAL TRAILER</div>
    <iframe width="100%" height="380" src="https://www.youtube.com/embed/{data['trailer']}" frameborder="0" allowfullscreen style="border-radius:20px;"></iframe>
    <button class="un-btn" onclick="document.getElementById('dl-zone').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</button>
    <div id="dl-zone" style="display:none;">
        <div class="p-head">DOWNLOAD OPTIONS</div>
        {m_btns if data['type']=='movie' else s_btns}
    </div>
</div>

<div id="ac-modal" class="ac-m">
    <img id="ac-i" src="">
    <h2 id="ac-n"></h2>
    <div style="font-size:12px; margin-bottom:15px; color:#38bdf8; text-align:center;">
        <span id="ac-b"></span> | <span id="ac-p"></span><br>
        <b>Total Projects:</b> <span id="ac-c"></span><br>
        <b>Top Works:</b> <span id="ac-w"></span>
    </div>
    <p id="ac-bio"></p>
    <button class="ac-close" onclick="document.getElementById('ac-modal').style.display='none'">CLOSE</button>
</div>

<script>
    const ads = {AD_LINKS}; const adCount = {data['ad_count']};
    function tS(id) {{ document.querySelectorAll('.ep-box').forEach(el => {{ if(el.id !== id) el.style.display = 'none'; }}); var x = document.getElementById(id); x.style.display = (x.style.display==='none')?'block':'none'; }}
    function tE(id) {{ document.querySelectorAll('.q-box').forEach(el => {{ if(el.id !== id) el.style.display = 'none'; }}); var x = document.getElementById(id); x.style.display = (x.style.display==='none')?'block':'none'; }}
    function go(u) {{ for(let i=0; i<adCount; i++) {{ window.open(ads[Math.floor(Math.random()*ads.length)], '_blank'); }} window.location.href = u; }}
    function opAc(n,i,b,p,c,w,bio) {{
        document.getElementById('ac-n').innerText = n;
        document.getElementById('ac-i').src = i;
        document.getElementById('ac-b').innerText = "Born: "+b;
        document.getElementById('ac-p').innerText = p;
        document.getElementById('ac-c').innerText = c;
        document.getElementById('ac-w').innerText = w;
        document.getElementById('ac-bio').innerText = bio;
        document.getElementById('ac-modal').style.display = 'block';
    }}
</script>
<!--MASTERMETA:{meta_b64}-->
"""
    return jsonify({"html": blogger_html})

if __name__ == '__main__':
    app.run(debug=True)
