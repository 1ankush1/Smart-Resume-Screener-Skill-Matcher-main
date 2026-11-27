/** Purpose: Renders the public app's brand header. */

import { FileSearch } from "lucide-react";

export default function Navbar() {
  return (
    <header className="topbar">
      <a className="brand" href="/">
        <span className="brand-mark small"><FileSearch size={20} /></span>
        <span>smart<span className="brand-accent">screen</span></span>
      </a>
      <span className="public-label">Free resume comparison</span>
    </header>
  );
}
