import os
import json
import base64
from flask import Flask, render_template_string, request, jsonify
import requests
import re

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
    <title>Master Blogger Generator PRO v9.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --accent: #38bdf8; --bg: #0b0f1a; --card: #161e2e; }
        body { background: var(--bg); color: #e2e8f0; font-family: 'Inter', sans-serif; padding-bottom: 70px; }
        .editor-card { background: var(--card); border: 1px solid #1e293b; border-radius: 15px; margin-top: 25px; padding: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); }
        .form-control { background: #0f172a; border: 1px solid #334155; color: #fff; margin-bottom: 12px; }
        .form-control:focus { background: #0f172a; color: #fff; border-color: var(--accent); box-shadow: none; }
        .section-header { border-left: 6px solid var(--accent); padding-left: 15px; margin: 35px 0 15px; font-weight: 900; color: var(--accent); text-transform: uppercase; letter-spacing: 1px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        @media (max-width: 768px) { .grid-4 { grid-template-columns: 1fr 1fr; } }
        .season-item { background: #1e293b; border: 2px solid #334155; padding: 25px; border-radius: 20px; margin-bottom: 25px; position: relative; }
        .episode-item { background: #0f172a; padding: 20px; border-radius: 15px; margin-top: 15px; border-left: 5px solid var(--accent); position: relative; }
        .btn-remove { position: absolute; top: 10px; right: 10px; background: #ef4444; color: white; border: none; padding: 5px 10px; border-radius: 5px; font-size: 11px; font-weight: bold; cursor: pointer; }
        .btn-prem { background: var(--accent); color: #000; font-weight: 900; border: none; padding: 18px; border-radius: 12px; transition: 0.3s; }
        .btn-prem:hover { background: #0ea5e9; transform: translateY(-3px); }
        .code-box { background: #000; color: #10b981; padding: 20px; border-radius: 15px; font-family: monospace; white-space: pre-wrap; margin-top: 20px; border: 1px solid #334155; }
        .preview-box { background: #fff; color: #000; padding: 25px; border-radius: 15px; margin-top: 20px; display: none; }
        .system-toggle { display: flex; gap: 10px; margin-bottom: 20px; }
        .sys-btn { flex: 1; padding: 15px; border: 2px solid #334155; background: #1e293b; color: white; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .sys-btn.active { border-color: var(--accent); color: var(--accent); }
        .res-title { font-size: 14px; font-weight: bold; color: var(--accent); text-align: center; margin-top: 8px; }

        .up-ui { display: flex; gap: 5px; align-items: center; margin-bottom: 12px; }
        .up-ui input { flex: 1; margin-bottom: 0 !important; }
        .up-btn { background: #334155; color: #38bdf8; border: 1px solid #38bdf8; border-radius: 8px; padding: 0 10px; height: 45px; font-size: 11px; font-weight: bold; cursor: pointer; white-space: nowrap; }
        
        /* Backdrop Picker Styling */
        .bd-picker { display: flex; overflow-x: auto; gap: 8px; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 10px; margin-top: 5px; scrollbar-width: thin; }
        .bd-picker img { height: 70px; border-radius: 5px; cursor: pointer; border: 2px solid transparent; transition: 0.2s; }
        .bd-picker img:hover { border-color: var(--accent); transform: scale(1.05); }
    </style>
</head>
<body>
<div class="container">
    <div class="editor-card">
        <h2 class="text-center fw-bold mb-4 text-info">🚀 ULTIMATE BLOGGER POST ENGINE</h2>
        
        <div class="mb-5 p-4 border border-info border-dashed rounded text-center">
            <h5 class="text-info">IMPORT & RE-EDIT POST</h5>
            <textarea id="import_data" class="form-control" rows="2" placeholder="Paste your generated code here to edit..."></textarea>
            <button class="btn btn-info btn-sm w-100 fw-bold" onclick="importCode()">IMPORT OLD POST</button>
        </div>

        <div class="system-toggle">
            <button id="s1" class="sys-btn active" onclick="switchSys('auto')">SYSTEM 1: AUTO (TMDB/IMDB)</button>
            <button id="s2" class="sys-btn" onclick="switchSys('manual')">SYSTEM 2: MANUAL</button>
        </div>

        <div id="search_area">
            <div class="row g-2 mb-4">
                <div class="col-md-5"><input type="text" id="query" class="form-control" placeholder="Search Movie Name..."></div>
                <div class="col-md-3"><input type="text" id="imdb_link" class="form-control" placeholder="IMDB Link or ID (tt1234567)"></div>
                <div class="col-md-2">
                    <select id="type" class="form-select bg-dark text-white border-secondary" style="height:50px">
                        <option value="movie">Movie</option><option value="tv">Web Series</option>
                    </select>
                </div>
                <div class="col-md-2"><button class="btn btn-prem w-100" onclick="searchTMDB()">SEARCH</button></div>
            </div>
        </div>

        <div id="results" class="row"></div>

        <div id="editor_form" style="display:block;">
            <div class="section-header">1. BASIC DETAILS & MAIN THUMBNAIL</div>
            <div class="row g-3">
                <div class="col-md-6"><label>Title</label><input type="text" id="e_title" class="form-control"></div>
                <div class="col-md-6">
                    <label>Main Backdrop (Landscape)</label>
                    <div class="up-ui">
                        <input type="text" id="e_backdrop" class="form-control">
                        <button class="up-btn" onclick="triggerUp('main_f')">Upload My Server</button>
                        <input type="file" id="main_f" style="display:none" onchange="handleUp(this, 'e_backdrop')">
                    </div>
                    <label class="text-info small">Pick a Backdrop (with or without name):</label>
                    <div id="bd_list" class="bd-picker"></div>
                </div>
                <div class="col-md-4"><label>Language</label><input type="text" id="e_lang" class="form-control"></div>
                <div class="col-md-4"><label>Release Date</label><input type="text" id="e_date" class="form-control"></div>
                <div class="col-md-4"><label>Trailer ID</label><input type="text" id="e_trailer" class="form-control"></div>
                <div class="col-md-12"><label>Storyline</label><textarea id="e_story" class="form-control" rows="4"></textarea></div>
                <div class="col-md-6"><label>Director Name</label><input type="text" id="e_dir_name" class="form-control"></div>
                <div class="col-md-6">
                    <label>Director Profile Image</label>
                    <div class="up-ui">
                        <input type="text" id="e_dir_img" class="form-control">
                        <button class="up-btn" onclick="triggerUp('dir_f')">Upload My Server</button>
                        <input type="file" id="dir_f" style="display:none" onchange="handleUp(this, 'e_dir_img')">
                    </div>
                </div>
            </div>

            <div class="section-header">2. CAST MEMBERS <button class="btn btn-sm btn-outline-info float-end" onclick="addManCast()">+ Add Cast</button></div>
            <div id="e_cast_list" class="row g-3"></div>

            <div class="section-header">3. GALLERY IMAGES <button class="btn btn-sm btn-outline-info float-end" onclick="addManGal()">+ Add Gallery</button></div>
            <div id="e_gallery_list" class="row g-2"></div>

            <div class="section-header">4. ADVERTISEMENT SETTINGS</div>
            <div class="col-md-4">
                <label>Ads Per Click (1-10)</label>
                <select id="e_ad_count" class="form-select bg-dark text-white border-secondary">
                    <script>for(let i=1;i<=10;i++) document.write(`<option value="${i}">${i} Ads per Click</option>`)</script>
                </select>
            </div>

            <div class="mt-4"><label class="text-info fw-bold">Select Post Type:</label>
                <select id="link_type" class="form-select bg-dark text-white" onchange="toggleMode(this.value)">
                    <option value="movie">Movie Mode</option><option value="tv">Web Series Mode</option>
                </select>
            </div>

            <div id="movie_ui" style="display:none;">
                <div class="section-header">5. MOVIE DOWNLOAD LINKS (8K TO 140P)</div>
                <div class="grid-4">
                    <div>8K<input type="text" data-q="8K" class="form-control mq"></div>
                    <div>4K<input type="text" data-q="4K" class="form-control mq"></div>
                    <div>2K<input type="text" data-q="2K" class="form-control mq"></div>
                    <div>1080p<input type="text" data-q="1080p" class="form-control mq"></div>
                    <div>720p<input type="text" data-q="720p" class="form-control mq"></div>
                    <div>480p<input type="text" data-q="480p" class="form-control mq"></div>
                    <div>360p<input type="text" data-q="360p" class="form-control mq"></div>
                    <div>140p<input type="text" data-q="140p" class="form-control mq"></div>
                </div>
            </div>

            <div id="series_ui" style="display:none;">
                <div class="section-header">5. SEASONS & EPISODES</div>
                <div id="season_container"></div>
                <button class="btn btn-outline-info w-100 fw-bold mt-2" onclick="addSeason()">+ ADD NEW SEASON</button>
            </div>

            <button class="btn btn-prem w-100 btn-lg mt-5" onclick="generateFinalHTML()">🚀 GENERATE PREMIUM BLOGGER POST</button>

            <div id="final_section" class="mt-5" style="display:none;">
                <div class="d-flex gap-3 mb-3">
                    <button class="btn btn-success flex-grow-1 fw-bold py-3" onclick="copyHTML()">COPY HTML CODE</button>
                    <button class="btn btn-warning flex-grow-1 fw-bold py-3" onclick="previewToggle()">PREVIEW POST</button>
                </div>
                <div id="preview_area" class="preview-box"></div>
                <div id="html_box" class="code-box"></div>
            </div>
        </div>
    </div>
</div>

<script>
let sCount = 0;
let fIdx = 0;

function triggerUp(id) { document.getElementById(id).click(); }

async function handleUp(input, targetId) {
    if(!input.files[0]) return;
    const formData = new FormData();
    formData.append('file', input.files[0]);
    const target = document.getElementById(targetId);
    target.value = "Saving to Server...";
    try {
        const res = await fetch('/api/upload', { method:'POST', body:formData });
        const data = await res.json();
        target.value = data.url;
    } catch(e) { alert("Server Error!"); }
}

function switchSys(m) {
    document.getElementById('s1').classList.toggle('active', m==='auto');
    document.getElementById('s2').classList.toggle('active', m==='manual');
    document.getElementById('search_area').style.display = m==='auto' ? 'block' : 'none';
    if(m==='manual') { toggleMode(document.getElementById('link_type').value); }
}

function toggleMode(t) {
    document.getElementById('movie_ui').style.display = t==='movie' ? 'block' : 'none';
    document.getElementById('series_ui').style.display = t==='tv' ? 'block' : 'none';
}

async function searchTMDB() {
    const q = document.getElementById('query').value;
    const im = document.getElementById('imdb_link').value;
    const t = document.getElementById('type').value;
    const res = await fetch(`/api/search?q=${q}&imdb=${im}&type=${t}`);
    const data = await res.json();
    let h = '';
    data.results.forEach(i => {
        let title = i.title || i.name;
        let year = (i.release_date || i.first_air_date || "").split('-')[0];
        h += `<div class="col-md-4 mb-3" onclick="selectItem('${i.id}', '${t}')" style="cursor:pointer">
            <div class="card bg-dark p-1">
                <img src="https://image.tmdb.org/t/p/w500${i.backdrop_path}" class="img-fluid rounded">
                <div class="res-title">${title} (${year || 'N/A'})</div>
            </div></div>`;
    });
    document.getElementById('results').innerHTML = h;
}
async function selectItem(id, type) {
    const res = await fetch(`/api/details?id=${id}&type=${type}`);
    const raw = await res.json();
    document.getElementById('results').innerHTML = '';
    document.getElementById('editor_form').style.display = 'block';
    document.getElementById('link_type').value = type;
    document.getElementById('e_title').value = raw.title || raw.name;
    document.getElementById('e_backdrop').value = `https://image.tmdb.org/t/p/original${raw.backdrop_path}`;
    document.getElementById('e_date').value = raw.release_date || raw.first_air_date;
    document.getElementById('e_story').value = raw.overview;
    
    // Backdrop Picker Logic
    let bHtml = '';
    if(raw.images && raw.images.backdrops){
        raw.images.backdrops.forEach(img => {
            bHtml += `<img src="https://image.tmdb.org/t/p/w300${img.file_path}" onclick="document.getElementById('e_backdrop').value='https://image.tmdb.org/t/p/original${img.file_path}'">`;
        });
    }
    document.getElementById('bd_list').innerHTML = bHtml;

    const d = raw.credits.crew.find(c => c.job === 'Director');
    document.getElementById('e_dir_name').value = d ? d.name : '';
    document.getElementById('e_dir_img').value = d ? `https://image.tmdb.org/t/p/w185${d.profile_path}` : '';
    const trailer = raw.videos.results.find(v => v.type === 'Trailer');
    document.getElementById('e_trailer').value = trailer ? trailer.key : '';
    let cH = '';
    raw.credits.cast.slice(0, 6).forEach(c => {
        fIdx++; let fId = 'f_c_'+fIdx; let iId = 'i_c_'+fIdx;
        cH += `<div class="col-md-4 mb-2 p-2 border border-secondary rounded position-relative">
            <button class="btn-remove" onclick="this.parentElement.remove()">X</button>
            <input type="text" class="form-control form-control-sm cn" value="${c.name}">
            <div class="up-ui">
                <input type="text" id="${iId}" class="form-control form-control-sm ci" value="https://image.tmdb.org/t/p/w185${c.profile_path}">
                <button class="up-btn" style="height:31px; font-size:10px" onclick="triggerUp('${fId}')">Up</button>
                <input type="file" id="${fId}" style="display:none" onchange="handleUp(this, '${iId}')">
            </div>
            <input type="hidden" class="cid" value="${c.id}"></div>`;
    });
    document.getElementById('e_cast_list').innerHTML = cH;
    let gH = '';
    raw.images.backdrops.slice(0, 8).forEach(img => {
        fIdx++; let fId = 'f_g_'+fIdx; let iId = 'i_g_'+fIdx;
        gH += `<div class="col-md-6 position-relative">
            <button class="btn-remove" onclick="this.parentElement.remove()">X</button>
            <div class="up-ui">
                <input type="text" id="${iId}" class="form-control form-control-sm gi" value="https://image.tmdb.org/t/p/original${img.file_path}">
                <button class="up-btn" style="height:31px; font-size:10px" onclick="triggerUp('${fId}')">Up</button>
                <input type="file" id="${fId}" style="display:none" onchange="handleUp(this, '${iId}')">
            </div></div>`;
    });
    document.getElementById('e_gallery_list').innerHTML = gH;
    toggleMode(type);
}

function addManCast(name="", img="", cid="0") {
    fIdx++; let fId = 'f_c_'+fIdx; let iId = 'i_c_'+fIdx;
    const d = document.createElement('div'); d.className='col-md-4 mb-2 p-2 border border-secondary rounded position-relative';
    d.innerHTML=`<button class="btn-remove" onclick="this.parentElement.remove()">X</button>
        <input type="text" class="form-control form-control-sm cn" placeholder="Name" value="${name}">
        <div class="up-ui">
            <input type="text" id="${iId}" class="form-control form-control-sm ci" placeholder="Img URL" value="${img}">
            <button class="up-btn" style="height:31px; font-size:10px" onclick="triggerUp('${fId}')">Up</button>
            <input type="file" id="${fId}" style="display:none" onchange="handleUp(this, '${iId}')">
        </div><input type="hidden" class="cid" value="${cid}">`;
    document.getElementById('e_cast_list').appendChild(d);
}

function addManGal(img="") {
    fIdx++; let fId = 'f_g_'+fIdx; let iId = 'i_g_'+fIdx;
    const d = document.createElement('div'); d.className='col-md-6 position-relative';
    d.innerHTML=`<button class="btn-remove" onclick="this.parentElement.remove()">X</button>
        <div class="up-ui">
            <input type="text" id="${iId}" class="form-control form-control-sm gi" placeholder="Screenshot URL" value="${img}">
            <button class="up-btn" style="height:31px; font-size:10px" onclick="triggerUp('${fId}')">Up</button>
            <input type="file" id="${fId}" style="display:none" onchange="handleUp(this, '${iId}')">
        </div>`;
    document.getElementById('e_gallery_list').appendChild(d);
}

function addSeason(name="") {
    sCount++; const sId = `s_${sCount}`; const d = document.createElement('div'); d.className='season-item'; d.id=sId;
    let sFormat = "S" + String(sCount).padStart(2, '0');
    d.innerHTML = `<button class="btn-remove" onclick="this.parentElement.remove()">REMOVE</button>
        <div class="d-flex gap-3 mb-3"><input type="text" class="form-control fw-bold st" value="${name||'Season '+sCount}" data-sformat="${sFormat}">
        <button class="btn btn-info fw-bold" onclick="addEpisode('${sId}')">+ ADD EPISODE</button></div><div class="ep-wrap" data-count="0"></div>`;
    document.getElementById('season_container').appendChild(d);
}
function addEpisode(sId, name="", links={}) {
    const w = document.querySelector(`#${sId} .ep-wrap`);
    let c = parseInt(w.dataset.count)+1; w.dataset.count=c;
    const sFormat = document.querySelector(`#${sId} .st`).dataset.sformat;
    const eFormat = sFormat + " EP" + String(c).padStart(2, '0');
    const d = document.createElement('div'); d.className='episode-item';
    d.innerHTML = `<button class="btn-remove" onclick="this.parentElement.remove()">REMOVE</button>
        <input type="text" class="form-control fw-bold et mb-2" value="${name||eFormat}">
        <div class="grid-4">
            <div>8K<input type="text" data-q="8K" class="form-control eq" value="${links['8K']||''}"></div>
            <div>4K<input type="text" data-q="4K" class="form-control eq" value="${links['4K']||''}"></div>
            <div>2K<input type="text" data-q="2K" class="form-control eq" value="${links['2K']||''}"></div>
            <div>1080p<input type="text" data-q="1080p" class="form-control eq" value="${links['1080p']||''}"></div>
            <div>720p<input type="text" data-q="720p" class="form-control eq" value="${links['720p']||''}"></div>
            <div>480p<input type="text" data-q="480p" class="form-control eq" value="${links['480p']||''}"></div>
            <div>360p<input type="text" data-q="360p" class="form-control eq" value="${links['360p']||''}"></div>
            <div>140p<input type="text" data-q="140p" class="form-control eq" value="${links['140p']||''}"></div>
        </div>`;
    w.appendChild(d);
}

async function generateFinalHTML() {
    const castData = []; const cNs = document.querySelectorAll('.cn'); const cIs = document.querySelectorAll('.ci'); const cIDs = document.querySelectorAll('.cid');
    for(let i=0; i<cNs.length; i++){
        let p = { birthday:'Unknown', place_of_birth:'Unknown', biography:'Manual Cast', combined_credits:{cast:[]} };
        if(cIDs[i].value !== "0") { const res = await fetch(`/api/person?id=${cIDs[i].value}`); p = await res.json(); }
        castData.push({ name: cNs[i].value, img: cIs[i].value, born: p.birthday||'N/A', place: p.place_of_birth||'N/A', bio: (p.biography||'No Bio').slice(0, 600).replace(/'/g, "").replace(/"/g, "") + "...", count: p.combined_credits.cast.length, best: p.combined_credits.cast.sort((a,b)=>b.vote_count-a.vote_count).slice(0,5).map(m=>m.title||m.name).join(', '), id: cIDs[i].value });
    }
    const data = {
        title: document.getElementById('e_title').value, backdrop: document.getElementById('e_backdrop').value,
        lang: document.getElementById('e_lang').value, date: document.getElementById('e_date').value,
        story: document.getElementById('e_story').value, dir_name: document.getElementById('e_dir_name').value,
        dir_img: document.getElementById('e_dir_img').value, trailer: document.getElementById('e_trailer').value,
        ad_count: document.getElementById('e_ad_count').value, type: document.getElementById('link_type').value,
        cast: castData, gallery: Array.from(document.querySelectorAll('.gi')).map(i=>i.value),
        movieLinks: Array.from(document.querySelectorAll('.mq')).filter(i=>i.value).map(i=>({q:i.dataset.q, url:i.value})),
        seasons: Array.from(document.querySelectorAll('.season-item')).map(s=>({ name: s.querySelector('.st').value, episodes: Array.from(s.querySelectorAll('.episode-item')).map(e=>({ name: e.querySelector('.et').value, links: Array.from(e.querySelectorAll('.eq')).filter(i=>i.value).map(i=>({q:i.dataset.q, url:i.value})) })) }))
    };
    const res = await fetch('/api/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    const resJ = await res.json(); document.getElementById('html_box').innerText = resJ.html; document.getElementById('preview_area').innerHTML = resJ.html; document.getElementById('final_section').style.display='block';
}

function importCode() {
    try {
        const raw = document.getElementById('import_data').value;
        const meta = JSON.parse(atob(raw.match(/<!--MASTERDATA:(.*)-->/)[1]));
        document.getElementById('editor_form').style.display='block';
        document.getElementById('e_title').value=meta.title; document.getElementById('e_backdrop').value=meta.backdrop;
        document.getElementById('e_lang').value=meta.lang; document.getElementById('e_date').value=meta.date;
        document.getElementById('e_story').value=meta.story; document.getElementById('e_dir_name').value=meta.dir_name;
        document.getElementById('e_dir_img').value=meta.dir_img; document.getElementById('e_trailer').value=meta.trailer;
        document.getElementById('e_ad_count').value=meta.ad_count; document.getElementById('link_type').value=meta.type;
        
        // Re-import Cast
        document.getElementById('e_cast_list').innerHTML = '';
        meta.cast.forEach(c => addManCast(c.name, c.img, c.id || "0"));

        // Re-import Gallery
        document.getElementById('e_gallery_list').innerHTML = '';
        meta.gallery.forEach(img => addManGal(img));

        if(meta.type === 'movie') { 
            toggleMode('movie'); 
            document.querySelectorAll('.mq').forEach(i => i.value = ''); 
            meta.movieLinks.forEach(l => { const i = document.querySelector(`.mq[data-q="${l.q}"]`); if(i) i.value = l.url; }); 
        } else { 
            toggleMode('tv'); 
            document.getElementById('season_container').innerHTML = ''; 
            sCount = 0; 
            meta.seasons.forEach(s => { 
                addSeason(s.name); 
                const sId=`s_${sCount}`; 
                s.episodes.forEach(e => { 
                    const lObj={}; 
                    e.links.forEach(ln=>lObj[ln.q]=ln.url); 
                    addEpisode(sId, e.name, lObj); 
                }); 
            }); 
        }
        alert("Post Data Re-imported Successfully!");
    } catch(e) { alert("Invalid Code! Make sure you copied the whole code."); console.log(e); }
}

function copyHTML() { navigator.clipboard.writeText(document.getElementById('html_box').innerText); alert("HTML Copied!"); }
function previewToggle() { const p = document.getElementById('preview_area'); p.style.display = p.style.display==='none'?'block':'none'; }

window.onload = function() { toggleMode('movie'); };
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(UI_HTML)

@app.route('/api/upload', methods=['POST'])
def upload_api():
    try:
        file = request.files['file']
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
        mime_type = file.mimetype
        base64_url = f"data:{mime_type};base64,{encoded_string}"
        return jsonify({"url": base64_url})
    except Exception as e:
        return jsonify({"url": "", "error": str(e)}), 500

@app.route('/api/search')
def search_api():
    q = request.args.get('q'); im = request.args.get('imdb'); t = request.args.get('type')
    if im:
        imdb_id = re.search(r'tt\d+', im)
        if imdb_id:
            find_res = requests.get(f"https://api.themoviedb.org/3/find/{imdb_id.group()}?api_key={TMDB_API_KEY}&external_source=imdb_id").json()
            results = find_res.get('movie_results', []) if t == 'movie' else find_res.get('tv_results', [])
            return jsonify({"results": results})
    return jsonify(requests.get(f"https://api.themoviedb.org/3/search/{t}?api_key={TMDB_API_KEY}&query={q}").json())

@app.route('/api/details')
def details_api():
    id = request.args.get('id'); t = request.args.get('type')
    return jsonify(requests.get(f"https://api.themoviedb.org/3/{t}/{id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos,images").json())

@app.route('/api/person')
def person_api():
    id = request.args.get('id')
    return jsonify(requests.get(f"https://api.themoviedb.org/3/person/{id}?api_key={TMDB_API_KEY}&append_to_response=combined_credits").json())

@app.route('/api/generate', methods=['POST'])
def generate_api():
    try:
        data = request.json
        meta_b64 = base64.b64encode(json.dumps(data).encode()).decode()
        m_year = data['date'][:4] if data['date'] else "N/A"
        cast_h = "".join([f'<div class="c-item" onclick="shAc(\'{c["name"]}\',\'{c["img"]}\',\'{c["born"]}\',\'{c["place"]}\',\'{c["count"]}\',\'{c["best"]}\',`{c["bio"]}`, \'{data["title"]}\', \'{m_year}\')"><img src="{c["img"]}"><p>{c["name"]}</p></div>' for c in data['cast']])
        gal_h = "".join([f'<img src="{i}">' for i in data['gallery']])
        
        m_btns = '<div class="premium-box"><h3 class="box-title">Quality List</h3><div class="btn-grid">' + "".join([f'<a href="javascript:void(0)" onclick="opLk(\'{l["url"]}\')" class="btn-pre m-btn">Watch & Download {l["q"]}</a>' for l in data['movieLinks']]) + '</div></div>'
        
        s_btns = '<div class="premium-box s-box"><h3 class="box-title">Season List</h3><div class="btn-grid">'
        for i, s in enumerate(data['seasons']):
            s_btns += f'<button class="btn-pre s-btn" onclick="tgS(\'s{i}\')">📂 {s["name"]}</button>'
        s_btns += '</div></div>'

        s_btns += '<div id="ep-list-container" class="premium-box ep-box" style="display:none;"><h3 class="box-title">Episode List</h3>'
        for i, s in enumerate(data['seasons']):
            s_btns += f'<div id="s{i}" class="ep-group" style="display:none;"><div class="btn-grid">'
            for j, ep in enumerate(s['episodes']): 
                s_btns += f'<button class="btn-pre ep-btn" onclick="tgE(\'s{i}e{j}\', \'{ep["name"]}\')">🎬 {ep["name"]}</button>'
            s_btns += '</div></div>'
        s_btns += '</div>'

        s_btns += '<div id="q-list-container" class="premium-box q-box" style="display:none;"><h3 id="q-title" class="box-title">Quality List</h3>'
        for i, s in enumerate(data['seasons']):
            for j, ep in enumerate(s['episodes']):
                s_btns += f'<div id="s{i}e{j}" class="q-group" style="display:none;"><div class="btn-grid">'
                for l in ep['links']: 
                    s_btns += f'<a href="javascript:void(0)" onclick="opLk(\'{l["url"]}\')" class="btn-pre q-btn">{ep["name"]} {l["q"]}</a>'
                s_btns += '</div></div>'
        s_btns += '</div>'

        tg_box_html = """<div class="tg-main-box"><h4>🚀 JOIN OUR TELEGRAM CHANNELS</h4><div class="tg-btn-grid"><a href="https://t.me/FlixBoxsOfficial" target="_blank">Official Channel</a><a href="http://t.me/FlixBoxs" target="_blank">Backup Channel</a><a href="https://t.me/FlixBoxsNew" target="_blank">Movie Channel</a><a href="https://t.me/+bYeiFHL2OgM3NWZl" target="_blank">Chat Group</a></div></div>"""
        
        blogger_html = f"""
<!--BLOGGER POST START-->
<style>
    .p-box {{ background: #0b0f1a; color: #f1f5f9; padding: 25px; border-radius: 20px; font-family: sans-serif; position: relative; }}
    .m-tm {{ width: 100%; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
    .m-tl {{ color: #38bdf8; font-size: 32px; font-weight: 900; text-align: center; margin: 25px 0; }}
    .h-ln {{ border-left: 5px solid #38bdf8; padding-left: 15px; margin: 30px 0 15px; font-weight: 800; font-size: 18px; color: #fff; }}
    .c-sl {{ display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px; scrollbar-width: none; }}
    .c-item {{ min-width: 90px; text-align: center; cursor: pointer; }}
    .c-item img {{ width: 75px; height: 75px; border-radius: 50%; border: 3px solid #38bdf8; object-fit: cover; }}
    .g-gr {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .g-gr img {{ width: 100%; border-radius: 12px; }}
    .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }}
    .btn-pre {{ display: block; text-align: center; padding: 15px; border-radius: 12px; text-decoration: none !important; font-weight: 800; border: none; cursor: pointer; font-size: 14px; transition: 0.3s; color: #fff !important; }}
    .un-btn {{ display: block; background: #fbbf24; color: #000 !important; text-align: center; padding: 18px; border-radius: 15px; font-weight: 900; font-size: 20px; cursor: pointer; margin: 30px 0 40px 0; border: none; width: 100%; }}
    .premium-box {{ padding: 20px; border-radius: 18px; margin-top: 20px; background: #161e2e; }}
    .box-title {{ color: #fff; font-size: 18px; font-weight: 900; margin-bottom: 15px; text-align: center; text-transform: uppercase; }}
    /* বাটনের কালার সেকশন */
    .m-btn {{ background: linear-gradient(135deg, #6366f1, #a855f7); box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4); }}
    .s-box {{ border: 2px solid #38bdf8; }}
    .s-btn {{ background: linear-gradient(135deg, #38bdf8, #2563eb); box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }}
    .ep-box {{ border: 2px solid #10b981; }}
    .ep-btn {{ background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }}
    .q-box {{ border: 2px solid #f43f5e; }}
    .q-btn {{ background: linear-gradient(135deg, #f43f5e, #e11d48); box-shadow: 0 4px 15px rgba(244, 63, 94, 0.4); }}
    /* মডাল এবং অন্যান্য */
    .ac-m {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #161e2e; border: 3px solid #38bdf8; width: 90%; max-width: 450px; padding: 25px; border-radius: 20px; z-index: 10000; display: none; color: #fff; box-shadow: 0 0 100px rgba(0,0,0,0.9); }}
    .ac-m img {{ width: 100px; height: 100px; border-radius: 50%; border: 4px solid #38bdf8; margin: 0 auto 15px; display: block; object-fit: cover; }}
    .tg-main-box {{ background: #161e2e; border: 2px solid #38bdf8; padding: 15px; border-radius: 15px; margin-top: 15px; text-align: center; }}
    .tg-btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .tg-btn-grid a {{ background: #0088cc; color: #fff !important; text-decoration: none !important; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: bold; }}
</style>
<div class="p-box">
    <img src="{data['backdrop']}" class="m-tm">
    <h1 class="m-tl">{data['title']}</h1>
    <p style="text-align:center; opacity:0.8;">📅 {data['date']} | 🌐 {data['lang']} | 🎥 {data['dir_name']}</p>
    <div class="h-ln">STORYLINE</div>
    <p style="line-height:1.7; color:#94a3b8; text-align: justify;">{data['story']}</p>
    <div class="h-ln">CAST MEMBERS (CLICK FOR BIO)</div>
    <div class="c-sl">{cast_h}</div>
    <div class="h-ln">SCREENSHOTS GALLERY</div>
    <div class="g-gr">{gal_h}</div>
    <div class="h-ln">OFFICIAL TRAILER</div>
    <iframe width="100%" height="350" src="https://www.youtube.com/embed/{data['trailer']}" frameborder="0" allowfullscreen style="border-radius:15px;"></iframe>
    <button class="un-btn" onclick="document.getElementById('dl-zone').style.display='block';this.style.display='none'">🔓 UNLOCK DOWNLOAD LINKS</button>
    {tg_box_html}
    <div id="dl-zone" style="display:none;">
        <div class="h-ln">DOWNLOAD OPTIONS</div>
        {m_btns if data['type']=='movie' else s_btns}
        {tg_box_html}
    </div>
</div>
<div id="ac-modal" class="ac-m">
    <div style="text-align:center; margin-bottom:15px; padding:10px; background:#0b0f1a; border-radius:10px; border:1px solid #38bdf8">
        <strong id="ac-m-title" style="color:#38bdf8;font-size:16px"></strong> <span id="ac-m-year" style="color:#fff; opacity:0.7"></span>
    </div>
    <img id="ac-i" src="">
    <h2 id="ac-n" style="text-align:center; color:#38bdf8"></h2>
    <div style="font-size:12px; margin-bottom:15px; color:#38bdf8; text-align:center;">
        <span id="ac-b"></span> | <span id="ac-p"></span><br>
        <b>Projects:</b> <span id="ac-c"></span> | <b>Top:</b> <span id="ac-w"></span>
    </div>
    <p id="ac-bio" style="font-size:13px; line-height:1.5; height:120px; overflow-y:auto; color:#cbd5e1"></p>
    <button style="background:#38bdf8;color:#000;font-weight:900;border:none;padding:12px;border-radius:10px;width:100%;cursor:pointer;" onclick="document.getElementById('ac-modal').style.display='none'">CLOSE</button>
</div>
<script>
    const ads = {AD_LINKS}; const adC = {data['ad_count']};
    function tgS(id) {{
        document.getElementById('ep-list-container').style.display = 'block';
        document.getElementById('q-list-container').style.display = 'none';
        document.querySelectorAll('.ep-group').forEach(el => el.style.display = 'none');
        document.getElementById(id).style.display = 'block';
        window.location.hash = 'ep-list-container';
    }}
    function tgE(id, name) {{
        document.getElementById('q-list-container').style.display = 'block';
        document.getElementById('q-title').innerText = "Quality for: " + name;
        document.querySelectorAll('.q-group').forEach(el => el.style.display = 'none');
        document.getElementById(id).style.display = 'block';
        window.location.hash = 'q-list-container';
    }}
    function opLk(u) {{ for(let i=0; i<adC; i++) {{ window.open(ads[Math.floor(Math.random()*ads.length)], '_blank'); }} window.location.href = u; }}
    function shAc(n,i,b,p,c,w,bio, m_title, m_year) {{
        document.getElementById('ac-n').innerText = n; document.getElementById('ac-i').src = i;
        document.getElementById('ac-b').innerText = "Born: "+b; document.getElementById('ac-p').innerText = p;
        document.getElementById('ac-c').innerText = c; document.getElementById('ac-w').innerText = w;
        document.getElementById('ac-bio').innerText = bio; document.getElementById('ac-m-title').innerText = m_title;
        document.getElementById('ac-m-year').innerText = "("+m_year+")"; document.getElementById('ac-modal').style.display = 'block';
    }}
</script>
<!--MASTERDATA:{meta_b64}-->
"""
        return jsonify({"html": blogger_html})
    except Exception as e:
        return jsonify({"html": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
