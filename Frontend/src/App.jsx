import Router from "./app/router/router";
import { useState, useEffect } from "react";
import logo from "./assets/logo_TH.png";
import { ToastProvider } from "@shared/components/Toast";
import { LanguageProvider } from "@shared/i18n";
import { AuthProvider } from "@features/auth";

function App() {
  const [loading, setLoading] = useState(true);
  const [exit, setExit] = useState(false);

  useEffect(() => {
    setTimeout(() => setExit(true), 1500);
    setTimeout(() => setLoading(false), 2300);
  }, []);

  if (loading) {
    return (
      <div className={`bg-black flex items-center justify-center h-screen ${exit ? "animate-exit" : ""}`}>
        <img src={logo} alt="THERS Logo" className="w-40 animate-logo" />
      </div>
    );
  }

  return (
    <LanguageProvider>
      <AuthProvider>
        <ToastProvider>
          <Router />
        </ToastProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;