import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Blog Studio",
  description: "A blog platform powered by AI writing tools",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <nav>
            <a href="/" className="site-logo">
              AI Blog Studio
            </a>
            <div className="nav-links">
              <a href="/">Blog</a>
              <a href="/new">Write</a>
              <a href="/login">Login</a>
            </div>
          </nav>
        </header>
        <main>{children}</main>
        <footer className="site-footer">
          <p>AI Blog Studio &copy; {new Date().getFullYear()}</p>
        </footer>
      </body>
    </html>
  );
}
