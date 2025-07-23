import { useState, useEffect } from 'react';

export default function DarkModeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    // Initialize dark mode
    document.documentElement.classList.add('dark');
    setIsDark(true);
  }, []);

  const toggleDarkMode = () => {
    const newMode = !isDark;
    setIsDark(newMode);
    
    if (newMode) {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
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