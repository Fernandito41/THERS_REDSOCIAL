import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AuthPage, Login, Register } from "@features/auth";
import { Terms, Privacy, Cookies } from "@features/legal";
import { Home, Discover, Messages, Notifications, Profile, Settings } from "@features/feed";
import AppShell from "@/app/layout/AppShell";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* AUTH */}
        <Route path="/" element={<AuthPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* THERS -- shell con navegación propia (rail/FAB) + páginas anidadas */}
        <Route element={<AppShell />}>
          <Route path="/feed" element={<Home />} />
          <Route path="/discover" element={<Discover />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* LEGAL */}
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/cookies" element={<Cookies />} />
      </Routes>
    </BrowserRouter>
  );
}