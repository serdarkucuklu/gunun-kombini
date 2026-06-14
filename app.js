// State Variables
let appData = null;
let currentCity = 'istanbul';
let currentGender = 'female';

// DOM Elements
const lastUpdatedBadge = document.getElementById('last-updated');
const cityBtns = document.querySelectorAll('.city-tabs .tab-btn');
const genderBtns = document.querySelectorAll('.gender-tabs .gender-btn');
const weatherIcon = document.getElementById('weather-icon');
const weatherTemp = document.getElementById('weather-temp');
const weatherCondition = document.getElementById('weather-condition');
const themeTitle = document.getElementById('theme-title');
const themeDescription = document.getElementById('theme-description');
const itemsGrid = document.getElementById('items-grid');

// Fetch and load database
async function loadData() {
    try {
        const response = await fetch('data.json');
        appData = await response.json();
        
        // Format last updated timestamp
        if (appData.last_updated) {
            const date = new Date(appData.last_updated);
            const formattedDate = date.toLocaleString('tr-TR', {
                day: 'numeric',
                month: 'long',
                hour: '2-digit',
                minute: '2-digit'
            });
            lastUpdatedBadge.textContent = `Güncellendi: ${formattedDate}`;
        }
        
        render();
    } catch (err) {
        console.error('Error loading data.json:', err);
        lastUpdatedBadge.textContent = 'Veri Yüklenemedi';
    }
}

// Render active state
function render() {
    if (!appData || !appData.cities || !appData.cities[currentCity]) return;
    
    const cityData = appData.cities[currentCity];
    const genderData = cityData[currentGender];
    
    // 1. Update Weather Info
    weatherTemp.textContent = cityData.weather.temp;
    weatherCondition.textContent = cityData.weather.condition;
    weatherIcon.className = `fa-solid ${cityData.weather.icon} weather-icon`;
    
    // 2. Update Combination Theme Card
    themeTitle.textContent = genderData.theme;
    themeDescription.textContent = genderData.description;
    
    // 3. Clear and Render Items Grid
    itemsGrid.innerHTML = '';
    
    genderData.items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'clothing-card';
        
        card.innerHTML = `
            <div class="card-img-container">
                <img src="${item.image_url}" alt="${item.name}" class="card-img" loading="lazy">
            </div>
            <div class="card-details">
                <h3 class="card-name">${item.name}</h3>
                <div class="price-row">
                    <span class="price-label">Tahmini Fiyat</span>
                    <span class="price-val">${item.price}</span>
                </div>
                <a href="${item.affiliate_link}" target="_blank" class="affiliate-btn">
                    Satın Al / İncele <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            </div>
        `;
        itemsGrid.appendChild(card);
    });
}

// Event Listeners for City Tabs
cityBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        cityBtns.forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        currentCity = e.currentTarget.dataset.city;
        render();
    });
});

// Event Listeners for Gender Tabs
genderBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        genderBtns.forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        currentGender = e.currentTarget.dataset.gender;
        render();
    });
});

// Initialize
loadData();
