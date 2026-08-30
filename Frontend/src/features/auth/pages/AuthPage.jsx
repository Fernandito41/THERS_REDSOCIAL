import { useNavigate } from "react-router-dom";
import { FcGoogle } from "react-icons/fc";
import { FaApple } from "react-icons/fa";
import { IoInformationCircleOutline } from "react-icons/io5";
import { Link } from "react-router-dom";
import collage from "@/assets/collage.png";
import logo from "@/assets/logo_oficial.jpeg";
import { useOAuthNotice } from "@features/auth";
import { Footer } from "@shared/components/Footer";
import LanguageSwitcher from "@shared/components/LanguageSwitcher";
import { useLanguage } from "@shared/i18n";

export default function AuthPage() {
  const navigate = useNavigate();
  const { notice, notify } = useOAuthNotice();
  const { t } = useLanguage();

  return (
    <div className="min-h-screen flex flex-col bg-white relative">

      <div className="absolute top-5 left-5 z-10 bg-white/10 backdrop-blur-md p-2 rounded-full shadow-lg">
        <img
          src={logo}
          alt="THERS"
          className="w-12 h-12 rounded-full object-cover"
        />
      </div>

      <div className="absolute top-5 right-5 z-10">
        <LanguageSwitcher />
      </div>

      <div className="flex-1 flex">
        {/* IZQUIERDA */}
        <div className="hidden md:flex w-1/2 relative items-center justify-center bg-black overflow-hidden">

          <img
            src={collage}
            alt={t("auth.landing.heroImageAlt")}
            className="w-full h-full object-cover opacity-80"
          />

          <div className="absolute inset-0 bg-black/40"></div>

          <div className="absolute inset-0 flex items-center justify-center text-center px-6">
            <h1 className="text-white text-4xl md:text-5xl font-extrabold">
              {t("auth.landing.heroTitle")}
            </h1>
          </div>

        </div>

        {/* DERECHA */}
        <div className="w-full md:w-1/2 flex flex-col justify-center px-10 max-w-md mx-auto">

          <h1 className="text-5xl font-extrabold mb-6 leading-tight">
            {t("auth.landing.title")}
          </h1>

          <h2 className="text-2xl font-bold mb-6">
            {t("auth.landing.subtitle")}
          </h2>

          <button
            type="button"
            onClick={() => notify("google")}
            className="w-full flex items-center justify-center gap-3 border py-3 rounded-full font-semibold"
          >
            <FcGoogle size={20} />
            {t("auth.oauthGoogleRegister")}
          </button>

          <button
            type="button"
            onClick={() => notify("apple")}
            className="w-full flex items-center justify-center gap-3 bg-black text-white py-3 rounded-full font-semibold mt-3"
          >
            <FaApple size={18} />
            {t("auth.oauthAppleRegister")}
          </button>

          {notice && (
            <p className="flex items-start gap-1.5 text-xs text-muted bg-line rounded-lg px-3 py-2 mt-3">
              <IoInformationCircleOutline size={15} className="shrink-0 mt-0.5" />
              {t("auth.oauthNoticeShort", {
                provider: notice === "google" ? t("auth.providerGoogle") : t("auth.providerApple"),
              })}
            </p>
          )}

          <div className="flex items-center my-4">
            <div className="flex-1 h-px bg-line"></div>
            <span className="px-3 text-muted">{t("auth.or")}</span>
            <div className="flex-1 h-px bg-line"></div>
          </div>

          <button
            onClick={() => navigate("/register")}
            className="w-full bg-black text-white py-3 rounded-full font-bold"
          >
            {t("auth.landing.createAccount")}
          </button>

          <p className="text-xs text-muted mt-4">
            {t("auth.landing.acceptPrefix")}{" "}
            <Link to="/terms" className="text-pulse-600 hover:underline">
              {t("auth.landing.termsLink")}
            </Link>{" "}
            {t("auth.landing.acceptMiddle")}{" "}
            <Link to="/privacy" className="text-pulse-600 hover:underline">
              {t("auth.landing.privacyLink")}
            </Link>
            {t("auth.landing.acceptSuffix")}{" "}
            <Link to="/cookies" className="text-pulse-600 hover:underline">
              {t("auth.landing.cookiesLink")}
            </Link>.
          </p>

          <div className="mt-10 text-sm font-semibold flex justify-center gap-2 items-center">
            <span className="font-bold">{t("auth.landing.alreadyHaveAccount")}</span>

            <button
              onClick={() => navigate("/login")}
              className="bg-pulse-600 text-white px-4 py-2 rounded-full font-bold hover:bg-pulse-700 transition"
            >
              {t("auth.landing.login")}
            </button>
          </div>

        </div>
      </div>

      <Footer />
    </div>
  );
}
