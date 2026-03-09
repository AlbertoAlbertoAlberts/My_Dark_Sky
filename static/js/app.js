// ===== Pricing Modal =====
(function() {
    const btn = document.getElementById('pricing-btn');
    const modal = document.getElementById('pricing-modal');
    const card = document.getElementById('pricing-card');
    const close = document.getElementById('pricing-close');
    const backdrop = document.getElementById('pricing-backdrop');
    const confetti = document.getElementById('confetti-box');
    if (!btn || !modal) return;

    function spawnConfetti() {
        confetti.innerHTML = '';
        const colors = ['#34d399','#60a5fa','#fbbf24','#f472b6','#a78bfa','#fb923c'];
        for (let i = 0; i < 60; i++) {
            const c = document.createElement('div');
            const color = colors[Math.floor(Math.random()*colors.length)];
            const left = Math.random()*100;
            const delay = Math.random()*0.5;
            const size = 4 + Math.random()*6;
            const dur = 1.5 + Math.random()*1.5;
            c.style.cssText = `position:absolute;left:${left}%;top:-10px;width:${size}px;height:${size}px;background:${color};border-radius:${Math.random()>0.5?'50%':'2px'};opacity:0.9;animation:confetti-fall ${dur}s ${delay}s ease-out forwards`;
            confetti.appendChild(c);
        }
    }

    function openModal() {
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        requestAnimationFrame(() => {
            card.style.transform = 'scale(1)';
            card.style.opacity = '1';
        });
        spawnConfetti();
    }

    function closeModal() {
        card.style.transform = 'scale(0.8)';
        card.style.opacity = '0';
        setTimeout(() => { modal.classList.add('hidden'); modal.style.display = ''; }, 350);
    }

    btn.addEventListener('click', openModal);
    close.addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.classList.contains('hidden')) closeModal(); });
})();

// ===== Unit Switching (°C / °F) =====
const F_COUNTRIES = ['US','BS','KY','LR','PW','MH','FM'];
const AMPM_COUNTRIES = ['US','AU','CA','PH','MY','BD','EG','SA','CO'];

function useAMPM() {
    return typeof APP_COUNTRY === 'string' && AMPM_COUNTRIES.includes(APP_COUNTRY.toUpperCase());
}

function formatHour24(timeStr) {
    // timeStr like "14:00" — convert to 12h if needed
    if (!useAMPM()) return timeStr;
    const [h, m] = timeStr.split(':').map(Number);
    const suffix = h >= 12 ? ' PM' : ' AM';
    const h12 = h % 12 || 12;
    return h12 + ':' + String(m).padStart(2, '0') + suffix;
}

function getDefaultUnit() {
    const saved = localStorage.getItem('tempUnit');
    if (saved === 'F' || saved === 'C') return saved;
    if (typeof APP_COUNTRY === 'string' && F_COUNTRIES.includes(APP_COUNTRY.toUpperCase())) return 'F';
    return 'C';
}

let currentUnit = getDefaultUnit();

function cToF(c) { return c * 9 / 5 + 32; }
function msToMph(ms) { return ms * 2.23694; }

function applyUnits() {
    document.querySelectorAll('.tv').forEach(el => {
        const c = parseFloat(el.dataset.c);
        if (isNaN(c)) return;
        el.textContent = (currentUnit === 'F' ? Math.round(cToF(c)) : Math.round(c)) + '°';
    });
    document.querySelectorAll('.wv').forEach(el => {
        const ms = parseFloat(el.dataset.ms);
        if (isNaN(ms)) return;
        if (currentUnit === 'F') {
            el.textContent = msToMph(ms).toFixed(1) + ' mph';
        } else {
            el.textContent = ms.toFixed(1) + ' m/s';
        }
    });
    const btn = document.getElementById('unit-toggle');
    if (btn) btn.textContent = currentUnit === 'C' ? '°C' : '°F';
}

document.getElementById('unit-toggle')?.addEventListener('click', () => {
    currentUnit = currentUnit === 'C' ? 'F' : 'C';
    localStorage.setItem('tempUnit', currentUnit);
    applyUnits();
});

document.addEventListener('DOMContentLoaded', applyUnits);

// ===== Geolocation =====
function geolocate() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
    }
    // Disable buttons and show loading state
    const btns = [document.getElementById('geolocate-btn'), document.getElementById('landing-geo-btn')];
    btns.forEach(b => { if (b) { b.disabled = true; b.style.opacity = '0.5'; } });

    navigator.geolocation.getCurrentPosition(pos => {
        const { latitude, longitude } = pos.coords;
        window.location.href = `/weather?lat=${latitude}&lon=${longitude}`;
    }, err => {
        btns.forEach(b => { if (b) { b.disabled = false; b.style.opacity = '1'; } });
        alert('Location access was denied. Please search for a city instead.');
    });
}

document.getElementById('geolocate-btn')?.addEventListener('click', geolocate);
document.getElementById('landing-geo-btn')?.addEventListener('click', geolocate);


// ===== Search Autocomplete =====
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
let searchTimeout = null;

searchInput?.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    const q = searchInput.value.trim();
    if (q.length < 2) {
        searchResults.classList.add('hidden');
        return;
    }
    searchTimeout = setTimeout(async () => {
        try {
            const resp = await fetch(`/api/geocode?q=${encodeURIComponent(q)}`);
            const data = await resp.json();
            if (data.length === 0) {
                searchResults.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500 text-center">No results found</div>';
                searchResults.classList.remove('hidden');
                return;
            }
            searchResults.innerHTML = data.map(r => {
                const name = [r.name, r.state, r.country].filter(Boolean).join(', ');
                return `<a href="/weather?lat=${r.lat}&lon=${r.lon}&location=${encodeURIComponent(name)}"
                            class="block px-4 py-2.5 text-sm text-gray-300 hover:bg-dark-600 hover:text-white transition">${name}</a>`;
            }).join('');
            searchResults.classList.remove('hidden');
        } catch {
            searchResults.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500 text-center">Search unavailable</div>';
            searchResults.classList.remove('hidden');
        }
    }, 300);
});

document.addEventListener('click', e => {
    if (!searchResults?.contains(e.target) && e.target !== searchInput) {
        searchResults?.classList.add('hidden');
    }
});


// ===== Time Machine Calendar =====
const tmBtn = document.getElementById('time-machine-btn');
const tmSection = document.getElementById('time-machine-section');
const calGrid = document.getElementById('cal-grid');
const calTitle = document.getElementById('cal-title');
const calPrev = document.getElementById('cal-prev');
const calNext = document.getElementById('cal-next');
const tmResults = document.getElementById('tm-results');
const tmLoading = document.getElementById('tm-loading');
const tmData = document.getElementById('tm-data');

let calYear, calMonth;

if (tmBtn) {
    const now = new Date();
    calYear = now.getFullYear();
    calMonth = now.getMonth();

    tmBtn.addEventListener('click', () => {
        tmSection.classList.toggle('hidden');
        if (!tmSection.classList.contains('hidden')) {
            renderCalendar();
            tmSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
    calPrev?.addEventListener('click', () => { calMonth--; if (calMonth < 0) { calMonth = 11; calYear--; } renderCalendar(); });
    calNext?.addEventListener('click', () => { calMonth++; if (calMonth > 11) { calMonth = 0; calYear++; } renderCalendar(); });
}

function renderCalendar() {
    if (!calGrid) return;
    const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    calTitle.textContent = `${months[calMonth]} ${calYear}`;

    const firstDay = new Date(calYear, calMonth, 1).getDay();
    const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
    const today = new Date();

    let html = '';
    for (let i = 0; i < firstDay; i++) {
        html += '<span></span>';
    }
    for (let d = 1; d <= daysInMonth; d++) {
        const date = new Date(calYear, calMonth, d);
        const isToday = date.toDateString() === today.toDateString();
        const isFuture = date > today;
        const cls = ['cal-day'];
        if (isToday) cls.push('today');
        if (isFuture) cls.push('disabled');

        if (isFuture) {
            html += `<span class="${cls.join(' ')}">${d}</span>`;
        } else {
            const ts = Math.floor(date.getTime() / 1000);
            html += `<span class="${cls.join(' ')}" data-ts="${ts}" onclick="loadTimeMachine(${ts}, this)">${d}</span>`;
        }
    }
    calGrid.innerHTML = html;
}

async function loadTimeMachine(ts, el) {
    if (APP_LAT === null || APP_LON === null) return;

    calGrid.querySelectorAll('.cal-day').forEach(d => d.classList.remove('selected'));
    el.classList.add('selected');

    tmResults.classList.remove('hidden');
    tmLoading.classList.remove('hidden');
    tmData.innerHTML = '';

    // WMO weather code → description + icon mapping
    const wmoDesc = {0:'Clear sky',1:'Mainly clear',2:'Partly cloudy',3:'Overcast',
        45:'Fog',48:'Rime fog',51:'Light drizzle',53:'Drizzle',55:'Dense drizzle',
        61:'Slight rain',63:'Rain',65:'Heavy rain',66:'Light freezing rain',67:'Freezing rain',
        71:'Slight snow',73:'Snow',75:'Heavy snow',77:'Snow grains',
        80:'Slight showers',81:'Showers',82:'Heavy showers',
        85:'Slight snow showers',86:'Heavy snow showers',
        95:'Thunderstorm',96:'Thunderstorm with hail',99:'Heavy thunderstorm with hail'};
    const wmoIcon = code => {
        if (code <= 1) return '01d';
        if (code <= 2) return '02d';
        if (code <= 3) return '04d';
        if (code <= 48) return '50d';
        if (code <= 55) return '09d';
        if (code <= 65) return '10d';
        if (code <= 67) return '13d';
        if (code <= 77) return '13d';
        if (code <= 82) return '09d';
        if (code <= 86) return '13d';
        return '11d';
    };

    try {
        const resp = await fetch(`/api/timemachine?lat=${APP_LAT}&lon=${APP_LON}&dt=${ts}`);
        const data = await resp.json();
        tmLoading.classList.add('hidden');

        if (data.error) {
            tmData.innerHTML = `<div class="text-center py-6">
                <svg class="w-10 h-10 mx-auto mb-2 text-gray-600" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24">
                    <path d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
                </svg>
                <p class="text-gray-500 text-sm">${data.error}</p>
            </div>`;
            return;
        }

        const hourly = data.hourly;
        if (!hourly || !hourly.time) {
            tmData.innerHTML = '<div class="text-center py-6"><p class="text-gray-500 text-sm">No historical data available for this date.</p></div>';
            return;
        }

        // Summary: min, max, avg temp and dominant weather
        const temps = hourly.temperature_2m.filter(t => t !== null);
        const minT = Math.min(...temps), maxT = Math.max(...temps);
        const avgT = temps.reduce((a, b) => a + b, 0) / temps.length;
        const codes = hourly.weather_code || [];
        const dominantCode = codes.sort((a,b) => codes.filter(v=>v===b).length - codes.filter(v=>v===a).length)[0] || 0;

        let html = '<div class="space-y-4">';

        // Day summary card
        html += `<div class="flex items-center gap-4 justify-center py-4">
            <img src="https://openweathermap.org/img/wn/${wmoIcon(dominantCode)}@2x.png" class="w-16 h-16 weather-icon-lg">
            <div>
                <div class="text-4xl font-extralight tv" data-c="${avgT}">${Math.round(avgT)}°</div>
                <div class="text-gray-400 text-sm mt-1">${wmoDesc[dominantCode] || 'Unknown'}</div>
                <div class="text-gray-500 text-xs mt-0.5">
                    Low <span class="tv text-blue-300/80" data-c="${minT}">${Math.round(minT)}°</span>
                    · High <span class="tv text-orange-200" data-c="${maxT}">${Math.round(maxT)}°</span>
                </div>
            </div>
        </div>`;

        // Hourly strip
        html += '<div class="overflow-x-auto rounded-lg p-4 bg-dark-700/30"><div class="flex gap-1 min-w-max">';
        for (let i = 0; i < hourly.time.length; i++) {
            const t = hourly.temperature_2m[i];
            const wc = hourly.weather_code?.[i] ?? 0;
            const hour = formatHour24(hourly.time[i].split('T')[1].slice(0, 5));
            if (t === null) continue;
            html += `<div class="hourly-item text-xs text-gray-400">
                <span>${hour}</span>
                <img src="https://openweathermap.org/img/wn/${wmoIcon(wc)}.png" class="w-8 h-8">
                <span class="text-gray-200 font-medium tv" data-c="${t}">${Math.round(t)}°</span>
            </div>`;
        }
        html += '</div></div>';
        html += '</div>';
        tmData.innerHTML = html;
        applyUnits();
    } catch {
        tmLoading.classList.add('hidden');
        tmData.innerHTML = `<div class="text-center py-6">
            <p class="text-gray-500 text-sm">Could not load historical data.</p>
        </div>`;
    }
}
