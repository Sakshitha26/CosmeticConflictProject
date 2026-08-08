import { Link, useLocation } from "react-router-dom";
import "./navbar.css";

function Navbar() {
    const location = useLocation();

    return (
        <nav className="navbar">

            <div className="logo">
                🧴 Cosmetic Conflict Analyzer
            </div>

            <ul className="nav-links">

                <li>
                    <Link
                        to="/home"
                        className={location.pathname === "/home" ? "active" : ""}
                    >
                        Home
                    </Link>
                </li>

                <li>
                    <Link
                        to="/upload"
                        className={location.pathname === "/upload" ? "active" : ""}
                    >
                        Analyze
                    </Link>
                </li>

                <li>
                    <Link
                        to="/result"
                        className={location.pathname === "/result" ? "active" : ""}
                    >
                        Result
                    </Link>
                </li>

                <li>
                    <Link
                        to="/"
                        className={location.pathname === "/" ? "active" : ""}
                    >
                        Logout
                    </Link>
                </li>

            </ul>

        </nav>
    );
}

export default Navbar;