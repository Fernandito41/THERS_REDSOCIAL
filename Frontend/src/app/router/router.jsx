import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AuthPage, Login, Register } from "@features/auth";
import { Terms, Privacy, Cookies } from "@features/legal";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* AUTH */}
        <Route path="/" element={<AuthPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* LEGAL */}
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/cookies" element={<Cookies />} />
      </Routes>
    </BrowserRouter>
  );
}