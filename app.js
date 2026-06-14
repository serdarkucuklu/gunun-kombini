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
    
    const activeQuizResult = localStorage.getItem('ootd_style_vibe');

    genderData.items.forEach(item => {
        const card = document.createElement('div');
        
        let isMatch = false;
        if (activeQuizResult) {
            const lowerName = item.name.toLowerCase();
            if (activeQuizResult.includes('Sokak') && (lowerName.includes('jean') || lowerName.includes('pantolon') || lowerName.includes('ayakkabı') || lowerName.includes('gözlük') || lowerName.includes('kemer'))) {
                isMatch = true;
            } else if (activeQuizResult.includes('Ofis') && (lowerName.includes('ceket') || lowerName.includes('blazer') || lowerName.includes('gömlek') || lowerName.includes('saat'))) {
                isMatch = true;
            } else if (activeQuizResult.includes('Randevu') && (lowerName.includes('çanta') || lowerName.includes('elbise') || lowerName.includes('etek') || lowerName.includes('parfüm') || lowerName.includes('bluz'))) {
                isMatch = true;
            } else if (activeQuizResult.includes('Spor') && (lowerName.includes('tayt') || lowerName.includes('şort') || lowerName.includes('tişört') || lowerName.includes('ayakkabı'))) {
                isMatch = true;
            }
        }
        
        card.className = `clothing-card ${isMatch ? 'highlight-match' : ''}`;
        
        card.innerHTML = `
            ${isMatch ? '<span class="clothing-card-badge">✨ Önerilen</span>' : ''}
            <div class="card-img-container">
                <img src="${item.image_url}" alt="${item.name}" class="card-img" loading="lazy" onerror="this.onerror=null; this.src=getFallbackClothingImage('${item.name}')">
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

// Helper to provide beautiful fallback images if Unsplash URL fails to load
function getFallbackClothingImage(name) {
    const lowercaseName = name.toLowerCase();
    
    // Guaranteed high-quality Unsplash clothing images
    if (lowercaseName.includes('kaban') || lowercaseName.includes('mont') || lowercaseName.includes('ceket') || lowercaseName.includes('blazer') || lowercaseName.includes('outerwear')) {
        return 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600&auto=format&fit=crop';
    }
    if (lowercaseName.includes('pantolon') || lowercaseName.includes('jean') || lowercaseName.includes('trousers') || lowercaseName.includes('tayt') || lowercaseName.includes('şort') || lowercaseName.includes('etek')) {
        return 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?q=80&w=600&auto=format&fit=crop';
    }
    if (lowercaseName.includes('ayakkabı') || lowercaseName.includes('sneaker') || lowercaseName.includes('bot') || lowercaseName.includes('postal') || lowercaseName.includes('çizme')) {
        return 'https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600&auto=format&fit=crop';
    }
    if (lowercaseName.includes('gözlük') || lowercaseName.includes('kemer') || lowercaseName.includes('çanta') || lowercaseName.includes('şapka') || lowercaseName.includes('saat')) {
        return 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600&auto=format&fit=crop';
    }
    // Default to shirt/gömlek/tişört style
    return 'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?q=80&w=600&auto=format&fit=crop';
}


// Style Quiz State
let quizAnswers = { q1: null, q2: null, q3: null };

// Modal elements
const quizModal = document.getElementById('quiz-modal');
const quizTriggerBtn = document.getElementById('quiz-trigger-btn');
const quizModalClose = document.getElementById('quiz-modal-close');
const quizSteps = document.querySelectorAll('.quiz-step');
const quizOptBtns = document.querySelectorAll('.quiz-opt-btn');
const quizResultCard = document.getElementById('quiz-result-card');
const quizStepsContainer = document.querySelector('.quiz-steps-container');
const quizResultTitle = document.getElementById('quiz-result-title');
const quizResultDesc = document.getElementById('quiz-result-desc');
const quizRestartBtn = document.getElementById('quiz-restart-btn');

function openQuiz() {
    // Reset quiz state
    quizAnswers = { q1: null, q2: null, q3: null };
    quizSteps.forEach((step, idx) => {
        if (idx === 0) step.classList.add('active');
        else step.classList.remove('active');
    });
    quizStepsContainer.style.display = 'block';
    quizResultCard.style.display = 'none';
    quizModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeQuiz() {
    quizModal.classList.remove('active');
    document.body.style.overflow = '';
}

function selectQuizOption(questionNum, val) {
    quizAnswers[`q${questionNum}`] = val;
    
    const nextStepNum = questionNum + 1;
    const currentStep = document.getElementById(`quiz-step-${questionNum}`);
    const nextStep = document.getElementById(`quiz-step-${nextStepNum}`);
    
    if (currentStep) currentStep.classList.remove('active');
    
    if (nextStep) {
        nextStep.classList.add('active');
    } else {
        // Quiz finished, show result
        calculateQuizResult();
    }
}

function calculateQuizResult() {
    let title = '';
    let desc = '';
    
    const { q1, q2, q3 } = quizAnswers;
    
    // Choose dynamic response based on combinations
    if (q1 === 'office') {
        title = 'Klasik Ofis Şıklığı';
        desc = 'İş veya okul gününüz için profesyonel duruşu elden bırakmayan, aynı zamanda son derece modern ve çabasız bir ceket/blazer kombini sizin için en ideali.';
    } else if (q1 === 'date') {
        title = 'Randevu Şıklığı';
        desc = 'Özel bir akşam yemeği veya buluşma için şık aksesuarlar ve bluz/elbise detaylarıyla taçlandırılmış göz alıcı bir kombin modunuzu tamamlayacak.';
    } else if (q1 === 'active') {
        title = 'Dinamik Spor Stili';
        desc = 'Hareketli ve sportif bir gün için tayt/şort ve dinamik spor ayakkabılarla oluşturulmuş, konforu en üst düzeyde hissettiren bir sokak stili.';
    } else {
        // default casual
        if (q2 === 'street') {
            title = 'Minimalist Sokak Modası';
            desc = 'Rahat jeanler, sneakerlar ve oversize kesimlerle oluşturulmuş çabasız şehir şıklığı. Günlük rutinlerinizde tarzınızı en konforlu şekilde yansıtın.';
        } else {
            title = 'Çabasız Şehir Kombini';
            desc = 'Hafif dokular, sade renk geçişleri ve gündelik hayatın koşuşturmasına ayak uyduran son derece pratik ve modern parçaların uyumu.';
        }
    }
    
    localStorage.setItem('ootd_style_vibe', title);
    
    quizResultTitle.textContent = title;
    quizResultDesc.textContent = desc;
    
    quizStepsContainer.style.display = 'none';
    quizResultCard.style.display = 'flex';
    
    // Rerender main page to apply recommendation highlights
    render();
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

// Quiz Listeners
quizTriggerBtn.addEventListener('click', openQuiz);
quizModalClose.addEventListener('click', closeQuiz);
quizModal.addEventListener('click', (e) => {
    if (e.target === quizModal) closeQuiz();
});

quizOptBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const q = parseInt(btn.dataset.q);
        const val = btn.dataset.val;
        selectQuizOption(q, val);
    });
});

quizRestartBtn.addEventListener('click', () => {
    openQuiz();
});

// Sanal Gardırobum State & Helpers
let savedOutfits = JSON.parse(localStorage.getItem('wardrobe_outfits')) || [];

function saveActiveOutfit() {
    if (!appData || !appData.cities || !appData.cities[currentCity]) return;
    const cityData = appData.cities[currentCity];
    const genderData = cityData[currentGender];
    
    // Check if already saved
    const exists = savedOutfits.some(outfit => outfit.theme === genderData.theme && outfit.city === currentCity && outfit.gender === currentGender);
    if (exists) {
        alert('Bu kombin zaten gardırobunuzda kayıtlı.');
        return;
    }
    
    const newOutfit = {
        id: 'outfit-' + Date.now(),
        city: currentCity.charAt(0).toUpperCase() + currentCity.slice(1),
        gender: currentGender,
        theme: genderData.theme,
        temp: cityData.weather.temp,
        items: genderData.items
    };
    
    savedOutfits.push(newOutfit);
    localStorage.setItem('wardrobe_outfits', JSON.stringify(savedOutfits));
    
    sendNotificationBanner('Kombin Gardıroba Eklendi! ❤️', `"${genderData.theme}" kombini başarıyla sanal gardırobunuza kaydedildi.`);
    renderWardrobe();
}

window.deleteWardrobeOutfit = function(id) {
    savedOutfits = savedOutfits.filter(outfit => outfit.id !== id);
    localStorage.setItem('wardrobe_outfits', JSON.stringify(savedOutfits));
    renderWardrobe();
};

window.loadWardrobeOutfit = function(id) {
    const outfit = savedOutfits.find(o => o.id === id);
    if (!outfit) return;
    
    // Set active city tab
    currentCity = outfit.city.toLowerCase();
    cityBtns.forEach(btn => {
        if (btn.dataset.city === currentCity) btn.classList.add('active');
        else btn.classList.remove('active');
    });
    
    // Set active gender tab
    currentGender = outfit.gender;
    genderBtns.forEach(btn => {
        if (btn.dataset.gender === currentGender) btn.classList.add('active');
        else btn.classList.remove('active');
    });
    
    // Scroll to display
    document.getElementById('theme-card').scrollIntoView({ behavior: 'smooth' });
    
    render();
    
    sendNotificationBanner('Kombin Yüklendi! 👕', `"${outfit.theme}" kombini ekrana yüklendi.`);
};

function renderWardrobe() {
    const section = document.getElementById('wardrobe-section');
    const grid = document.getElementById('wardrobe-grid');
    if (!section || !grid) return;
    
    if (savedOutfits.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    grid.innerHTML = '';
    
    savedOutfits.forEach(outfit => {
        const card = document.createElement('div');
        card.className = 'wardrobe-card';
        
        const genderLabel = outfit.gender === 'female' ? 'Kadın' : 'Erkek';
        const genderIcon = outfit.gender === 'female' ? 'fa-venus' : 'fa-mars';
        
        const itemsHtml = outfit.items.map(item => `
            <a href="${item.affiliate_link}" target="_blank" class="wardrobe-preview-item" title="${item.name} - ${item.price}">
                <img src="${item.image_url}" alt="${item.name}">
            </a>
        `).join('');
        
        card.innerHTML = `
            <button class="wardrobe-delete-btn" onclick="deleteWardrobeOutfit('${outfit.id}')" title="Kombini Sil">
                <i class="fa-solid fa-trash"></i>
            </button>
            <div class="wardrobe-meta">
                <span class="wardrobe-tag"><i class="fa-solid fa-location-dot"></i> ${outfit.city}</span>
                <span class="wardrobe-tag"><i class="fa-solid ${genderIcon}"></i> ${genderLabel}</span>
                <span class="wardrobe-tag"><i class="fa-solid fa-temperature-half"></i> ${outfit.temp}</span>
            </div>
            <h4 class="wardrobe-title">${outfit.theme}</h4>
            <div class="wardrobe-items-preview">
                ${itemsHtml}
            </div>
            <div class="wardrobe-actions">
                <span class="wardrobe-items-count">${outfit.items.length} Parça</span>
                <button class="wardrobe-load-btn" onclick="loadWardrobeOutfit('${outfit.id}')"><i class="fa-solid fa-eye"></i> Kombini İncele</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function sendNotificationBanner(title, body) {
    // UI Banner alert
    const banner = document.createElement('div');
    banner.className = 'custom-alert-banner';
    banner.innerHTML = `<i class="fa-solid fa-bell"></i> <span><strong>${title}</strong>: ${body}</span>`;
    document.body.appendChild(banner);
    
    setTimeout(() => {
        banner.classList.add('fade-out');
        setTimeout(() => banner.remove(), 500);
    }, 6000);
}

// Initialize
const saveOutfitBtn = document.getElementById('save-outfit-btn');
if (saveOutfitBtn) {
    saveOutfitBtn.addEventListener('click', saveActiveOutfit);
}

loadData();
renderWardrobe();

