const API_URL = 'https://saleable-calceolate-carolyne.ngrok-free.dev/predict';

// const API_URL = 'https://ml-week-26-rrs-1.onrender.com/predict';

function formatLabel(str) {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function renderTasteBar(label, value, value_user) {
    const percentage = parseFloat(value) * 100;
    const percentage_user = parseFloat(value_user) * 100;
    return `
        <div class="mb-2">
            <div class="d-flex justify-content-between mb-1">
                <small class="text-muted">${label}</small>
                <small class="fw-bold">${Math.round(percentage)}%</small>
            </div>
            <div class="taste-bar-bg">
                <div class="taste-fill" style="width: ${percentage}%"></div>
                <div class="user_taste-fill" style="width: ${percentage_user}%"></div>
            </div>
        </div>
    `;
}

function createCoffeeCard(coffee) {
    const tagsHtml = (coffee.tags || []).map(tag =>
        `<span class="tag-pill">${formatLabel(tag)}</span>`
    ).join('');
    const equipmentHtml = (coffee.required_equipment || []).map(eq =>
        `<span class="badge bg-secondary me-1 mb-1 fw-normal">${formatLabel(eq)}</span>`
    ).join('');

    let productsHtml = '';
    if (coffee.required_products && typeof coffee.required_products === 'object') {
        productsHtml = Object.entries(coffee.required_products).map(([key, value]) =>
            `<li class="small text-muted">${formatLabel(key)}: ${value}</li>`
        ).join('');
    }

    const displayScore = coffee.score !== undefined ? parseFloat(coffee.score).toFixed(1) : 'N/A';

    return `
        <div class="card coffee-card mb-4 shadow-sm">
            <div class="card-header-custom d-flex justify-content-between align-items-start">
                <div>
                    <h3 class="h4 mb-1 fw-bold text-dark">${coffee.recipe_name}</h3>
                    <p class="text-muted mb-2">${coffee.description}</p>
                    <div class="mt-2">${tagsHtml}</div>
                </div>
                <div class="text-end">
                    <div class="display-6 fw-bold text-primary">${displayScore}</div>
                    <small class="text-muted">Score</small>
                </div>
            </div>
            
            <div class="card-body">
                <div class="row g-3 mb-4">
                    <div class="col-3">
                        <div class="metric-box">
                            <div class="metric-label">Time</div>
                            <div class="metric-value">${coffee.preparation_time_minutes} min</div>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="metric-box">
                            <div class="metric-label">Difficulty</div>
                            <div class="metric-value text-capitalize">${coffee.difficulty}</div>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="metric-box">
                            <div class="metric-label">Size</div>
                            <div class="metric-value">${coffee.portion_size_ml} ml</div>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="metric-box">
                            <div class="metric-label">Strength</div>
                            <div class="metric-value">${coffee.strength}/5</div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3 mb-md-0">
                        <h6 class="fw-bold text-uppercase small text-muted mb-3">Taste Profile</h6>
                        ${renderTasteBar('Bitterness', coffee.taste_bitterness, coffee.u_taste_bitterness)}
                        ${renderTasteBar('Sweetness', coffee.taste_sweetness, coffee.u_taste_sweetness)}
                        ${renderTasteBar('Acidity', coffee.taste_acidity, coffee.u_taste_acidity)}
                        ${renderTasteBar('Body', coffee.taste_body, coffee.u_taste_body)}
                    </div>
                    
                    <div class="col-md-6">
                        <div class="bg-light p-3 rounded h-100">
                            <h6 class="fw-bold text-uppercase small text-muted mb-2">Requirements</h6>
                            
                            <div class="mb-3">
                                <small class="d-block text-dark fw-bold mb-1">Equipment</small>
                                <div>${equipmentHtml}</div>
                            </div>
                            
                            <div>
                                <small class="d-block text-dark fw-bold mb-1">Ingredients</small>
                                <ul class="list-unstyled mb-0 ps-1">
                                    ${productsHtml}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function fetchRecommendations() {
    const userIdInput = document.getElementById('user-id-input');
    const amountInput = document.getElementById('amount-input');
    const container = document.getElementById('coffee-list');
    let userId = userIdInput.value.trim();
    let amount = amountInput.value.trim();

    if (!userId) {
        alert('Please enter a valid User ID');
        return;
    }
    if (!amount) {
        alert('Please enter a amount of recommendations');
        return;
    }

    if (/^\d+$/.test(userId)) {
        userId = `user_${userId}`;
    }

    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Calculating recommendations for ${userId}...</p>
        </div>
    `;

    try {
        const response = await axios.get(API_URL, {
            params: {user_id: userId, k: amount},
            headers: {
                "ngrok-skip-browser-warning": "69420"
            }
        });

        const responseData = response.data;
        const coffees = Array.isArray(responseData) ? responseData : (responseData.coffees || []);

        console.log("API Response:", responseData);
        container.innerHTML = '';

        if (coffees.length > 0) {
            coffees.forEach(coffee => {
                container.innerHTML += createCoffeeCard(coffee);
            });
        } else {
            container.innerHTML = `
                <div class="alert alert-info text-center">
                    No recommendations found for User ID ${userId}.
                </div>
            `;
        }
    } catch (error) {
        console.error("Fetch error:", error);

        const mockData = [
            {
                "recipe_id": "mock_latte_001",
                "recipe_name": "Recipe Classic Latte",
                "description": "Espresso with lots of steamed milk and a thin layer of foam",
                "taste_bitterness": "0.80000",
                "taste_sweetness": "0.50000",
                "taste_acidity": "0.10000",
                "taste_body": "0.50000",
                "u_taste_bitterness": "0.65000",
                "u_taste_sweetness": "0.45000",
                "u_taste_acidity": "0.15000",
                "u_taste_body": "0.40000",
                "strength": "2",
                "portion_size_ml": "230",
                "difficulty": "intermediate",
                "score": 1.95,
                "preparation_time_minutes": "4",
                "required_equipment": ["espresso_machine", "grinder"],
                "required_products": {
                    "coffee_beans": "18g",
                    "milk": "200ml"
                },
                "tags": ["hot", "classic", "milky"]
            },
            {
                "recipe_id": "mock_mocha_002",
                "recipe_name": "Recipe Peppermint Mocha",
                "description": "Chocolate mocha with refreshing peppermint.",
                "taste_bitterness": "0.3500",
                "taste_sweetness": "0.8000",
                "taste_acidity": "0.2000",
                "taste_body": "0.4000",
                "u_taste_bitterness": "0.2500",
                "u_taste_sweetness": "0.5600",
                "u_taste_acidity": "0.1000",
                "u_taste_body": "0.3000",
                "strength": "3",
                "portion_size_ml": "400",
                "difficulty": "intermediate",
                "score": 1.45,
                "preparation_time_minutes": "3",
                "required_equipment": ["espresso_machine", "grinder", "milk_frother"],
                "required_products": {
                    "coffee_beans": "18g",
                    "whole_milk": "250ml",
                    "chocolate_syrup": "30ml"
                },
                "tags": ["sweet", "flavored", "winter"]
            }
        ];

        container.innerHTML = `
            <div class="alert alert-warning mb-4">
                <strong>API Connection Failed:</strong> Showing mock data for demonstration.
            </div>
        `;
        mockData.forEach(coffee => {
            container.innerHTML += createCoffeeCard(coffee);
        });
    }
}

document.getElementById('fetch-btn').addEventListener('click', fetchRecommendations);

document.getElementById('user-id-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        fetchRecommendations();
    }
});