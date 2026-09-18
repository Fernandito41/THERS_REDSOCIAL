import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import {
  AuthPage,
  Login,
  Register,
  ForgotPassword,
  VerifyResetCode,
  ResetPassword,
  VerifyRegistrationCode,
  CompleteProfile,
} from "@features/auth";
import { Terms, Privacy, Cookies } from "@features/legal";
import {
  Information,
  HowItWorks,
  Community,
  Security,
  Faq,
  Blog,
  Locations,
  Popular,
  ImportContacts,
} from "@features/public";
import { HelpLayout, HelpCenter, HelpCategoryPage, HelpArticlePage, HelpSearchPage } from "@features/help";
import {
  Home,
  Search,
  Videos,
  Capsules,
  Radar,
  Messages,
  Notifications,
  Profile,
  SettingsLayout,
  SettingsSectionPage,
} from "@features/feed";
import AppShell from "@/app/layout/AppShell";
import PublicLayout from "@/app/layout/PublicLayout";
import ProtectedRoute from "./ProtectedRoute";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* AUTH */}
        <Route path="/" element={<AuthPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-registration-code" element={<VerifyRegistrationCode />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/verify-reset-code" element={<VerifyResetCode />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* THERS -- shell con navegación propia (rail/FAB) + páginas anidadas.
            ProtectedRoute es la única responsable de decidir si hay sesión;
            AppShell ya no redirige por su cuenta. */}
        <Route element={<ProtectedRoute />}>
          {/* Fuera de AppShell a propósito -- ADR-012-google-sign-in.md,
              FASE 18: onboarding de una cuenta con perfil incompleto, no
              una página de la app en sí (sin rail/FAB de navegación). */}
          <Route path="/complete-profile" element={<CompleteProfile />} />
          <Route element={<AppShell />}>
            <Route path="/feed" element={<Home />} />

            {/* Los siete destinos de la sidebar de referencia
                (docs/THERS_REFERENCE_MANIFEST.md §5) tienen todos una URL
                real: el archivo maestro §6.3 prohíbe dejar un enlace de
                navegación sin destino. */}
            <Route path="/search" element={<Search />} />
            <Route path="/videos" element={<Videos />} />
            <Route path="/capsules" element={<Capsules />} />
            <Route path="/radar" element={<Radar />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/profile" element={<Profile />} />
            {/* Configuración: las 12 secciones son rutas reales, cada una
                con su URL propia para poder enlazarla y recargarla
                (archivo maestro §6.3). */}
            <Route path="/settings" element={<SettingsLayout />}>
              <Route index element={<Navigate to="/settings/profile" replace />} />
              <Route path=":section" element={<SettingsSectionPage />} />
            </Route>

            {/* /discover era la ruta anterior de esta misma superficie. Se
                redirige en vez de mantener dos rutas equivalentes (archivo
                maestro §11: "no dejes dos rutas nueva y vieja sin motivo"). */}
            <Route path="/discover" element={<Navigate to="/search" replace />} />
          </Route>
        </Route>

        {/* PÚBLICO -- páginas informativas/legales, con Footer y navegación pública propia */}
        <Route element={<PublicLayout />}>
          <Route path="/information" element={<Information />} />
          <Route path="/information/how-it-works" element={<HowItWorks />} />
          <Route path="/information/community" element={<Community />} />
          <Route path="/information/security" element={<Security />} />
          <Route path="/information/faq" element={<Faq />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/help" element={<HelpLayout />}>
            <Route index element={<HelpCenter />} />
            <Route path="category/:categoryId" element={<HelpCategoryPage />} />
            <Route path="article/:slug" element={<HelpArticlePage />} />
            <Route path="search" element={<HelpSearchPage />} />
          </Route>
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
