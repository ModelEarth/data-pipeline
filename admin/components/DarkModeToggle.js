import { useState, useEffect } from 'react';

// Simple cookie helper functions
const getCookie = (name) => {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
};

const setCookie = (name, value, days = 365) => {
  if (typeof document === 'undefined') return;
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
};

export default function DarkModeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    // Check sitelook cookie for initial state
    const sitelook = getCookie('sitelook');
    const isLight = sitelook === 'light';

    setIsDark(!isLight);

    if (isLight) {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    }
  }, []);

  const toggleDarkMode = () => {
    const newMode = !isDark;
    setIsDark(newMode);

    if (newMode) {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
      setCookie('sitelook', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      setCookie('sitelook', 'light');
    }
  };

  return (
    <div 
      className="toggle-container"
      onClick={toggleDarkMode}
      role="button"
      aria-label="Toggle dark mode"
    >
      <div className={`toggle-dot ${isDark ? 'dark' : 'light'}`} />
    </div>
  );
}