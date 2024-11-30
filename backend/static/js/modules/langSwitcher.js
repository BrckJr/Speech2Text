const languageFiles = {
  en: "/static/lang/en.json",
  de: "/static/lang/de.json",
  es: "/static/lang/es.json"
};

let currentLanguage = 'en'; // Default language

// Function to load the language data and update text
export function loadLanguage(lang) {
  currentLanguage = lang;
  console.log("Current Language: " + currentLanguage);
  fetch(languageFiles[lang])
    .then(response => response.json())
    .then(data => {
      updateText(data);
    });
}

// Function to set up language switcher buttons
export function setupLangSwitcherButtons(enButton, deButton, esButton) {
  // Event listener for the German button
  deButton.addEventListener('click', () => {
    loadLanguage('de'); // Load German language file
  });

  // Event listener for the English button
  enButton.addEventListener('click', () => {
    loadLanguage('en'); // Load English language file
  });

  // Event listener for the Spanish button
  esButton.addEventListener('click', () => {
    loadLanguage('es'); // Load English language file
  });

  // Optionally, load the default language on initial load (e.g., English)
  loadLanguage(currentLanguage);
}

// Function to update text content based on the loaded language data
function updateText(translations) {
  // Loop through all elements with a `data-i18n` attribute
  document.querySelectorAll('[data-i18n]').forEach(element => {
    const key = element.getAttribute('data-i18n');
    if (translations[key]) {
      element.textContent = translations[key];
    }
  });
}
