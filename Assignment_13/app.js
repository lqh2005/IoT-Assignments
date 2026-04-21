// API Configuration
// For local testing: Replace 'YOUR_OPENWEATHER_API_KEY' with your actual API key
// For Azure deployment: Set WEATHER_API_KEY in environment variables
const API_KEY = '7e1b5e3408952ce38d63380d2de6b114'; // OpenWeather API Key
const API_URL = 'https://api.openweathermap.org/data/2.5/weather';

// DOM Elements
const cityInput = document.getElementById('cityInput');
const weatherInfo = document.getElementById('weatherInfo');
const error = document.getElementById('error');
const loader = document.getElementById('loader');

// Allow search on Enter key press
cityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        getWeather();
    }
});

async function getWeather() {
    const city = cityInput.value.trim();
    
    if (!city) {
        showError('Please enter a city name');
        return;
    }
    
    // Check if API key is set
    if (API_KEY === 'YOUR_OPENWEATHER_API_KEY') {
        showError('⚠️ API key not configured. Please edit app.js and replace YOUR_OPENWEATHER_API_KEY with your actual key from openweathermap.org');
        return;
    }
    
    // Show loader, hide previous results
    loader.classList.add('active');
    weatherInfo.classList.remove('active');
    error.classList.remove('active');
    
    try {
        const response = await fetch(
            `${API_URL}?q=${city}&units=metric&appid=${API_KEY}`
        );
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('City not found');
            } else if (response.status === 401) {
                throw new Error('Invalid API key. Please check your configuration.');
            } else {
                throw new Error(`Weather service error: ${response.status}`);
            }
        }
        
        const data = await response.json();
        displayWeather(data);
        
    } catch (err) {
        showError(err.message);
    } finally {
        loader.classList.remove('active');
    }
}

function displayWeather(data) {
    // Extract weather data
    const temp = Math.round(data.main.temp);
    const feelsLike = Math.round(data.main.feels_like);
    const humidity = data.main.humidity;
    const windSpeed = Math.round(data.wind.speed * 3.6); // Convert m/s to km/h
    const pressure = data.main.pressure;
    const description = data.weather[0].main;
    const city = data.name;
    const country = data.sys.country;
    
    // Update DOM
    document.getElementById('cityName').textContent = `${city}, ${country}`;
    document.getElementById('temp').textContent = `${temp}°C`;
    document.getElementById('description').textContent = description;
    document.getElementById('feelsLike').textContent = `${feelsLike}°C`;
    document.getElementById('humidity').textContent = `${humidity}%`;
    document.getElementById('windSpeed').textContent = `${windSpeed} km/h`;
    document.getElementById('pressure').textContent = `${pressure} hPa`;
    
    // Show weather info
    weatherInfo.classList.add('active');
    error.classList.remove('active');
    
    // Clear input
    cityInput.value = '';
}

function showError(message) {
    error.textContent = message;
    error.classList.add('active');
    weatherInfo.classList.remove('active');
    loader.classList.remove('active');
}
