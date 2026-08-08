import "./footer.css";

function Footer() {
    return (
        <footer className="footer">

            <div className="footer-container">

                <h2>🧴 Cosmetic Conflict Analyzer</h2>

                <p>
                    Analyze cosmetic products safely using AI-powered
                    ingredient conflict detection.
                </p>

                <div className="footer-links">

                    <a href="/home">Home</a>

                    <a href="/upload">Analyze</a>

                    <a href="/">Login</a>

                </div>

                <hr />

                <p className="copyright">
                    © 2026 Cosmetic Conflict Analyzer. All Rights Reserved.
                </p>

            </div>

        </footer>
    );
}

export default Footer;