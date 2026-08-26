import { BrowserRouter, Routes, Route } from "react-router-dom";

import { AuthPage, Login, Register, ForgotPassword, ResetPassword } from "@features/auth";
import { Terms, Privacy, Cookies } from "@features/legal";
import {
  Information,
  HowItWorks,
  Community,
  Security,
  Faq,
  Blog,
  HelpCenter,
  Locations,
  Popular,
  ImportContacts,
} from "@features/public";
import { Home, Discover, Messages, Notifications, Profile, Settings } from "@features/feed";
import AppShell from "@/app/layout/AppShell";
import PublicLayout from "@/app/layout/PublicLayout";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* AUTH */}
        <Route path="/" element={<AuthPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* THERS -- shell con navegación propia (rail/FAB) + páginas anidadas */}
        <Route element={<AppShell />}>
          <Route path="/feed" element={<Home />} />
          <Route path="/discover" element={<Discover />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* PÚBLICO -- páginas informativas/legales, con Footer y navegación pública propia */}
        <Route element={<PublicLayout />}>
          <Route path="/information" element={<Information />} />
          <Route path="/information/how-it-works" element={<HowItWorks />} />
          <Route path="/information/community" element={<Community />} />
          <Route path="/information/security" element={<Security />} />
          <Route path="/information/faq" element={<Faq />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/help" element={<HelpCenter />} />
          <Route path="/popular" element={<Popular />} />
          <Route path="/locations" element={<Locations />} />
          <Route path="/contacts/import" element={<ImportContacts />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/cookies" element={<Cookies />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
