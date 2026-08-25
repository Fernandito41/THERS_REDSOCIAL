import { Link } from "react-router-dom";

export default function FooterLink({ to, children }) {
  return (
    <Link
      to={to}
      className="text-sm text-muted dark:text-muted-dark hover:text-ink dark:hover:text-ink-dark transition-colors rounded-sm"
    >
      {children}
    </Link>
  );
}
