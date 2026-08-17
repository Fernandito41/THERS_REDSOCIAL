import { useEffect, useState } from "react";

const STORAGE_KEY = "theme";

// THERS nació oscura (Login/Register siguen siendo oscuros de forma fija) --
// el oscuro es el modo por defecto la primera vez que alguien entra; a partir
// de ahí, se respeta lo que la persona haya elegido (localStorage).
function getInitialTheme() {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "light" ? "light" : "dark";
}

export function useTheme() {
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return { theme, toggleTheme };
}
