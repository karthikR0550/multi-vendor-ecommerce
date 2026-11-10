
import { Link } from "react-router-dom";

function LandingPage() {
    const styles = {
        page: {
            minHeight: "100vh",
            background: "#f8fafc",
            fontFamily: "Arial, sans-serif",
            color: "#172033",
        },
        navbar: {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "22px 8%",
            background: "#ffffff",
            boxShadow: "0 2px 10px rgba(0,0,0,0.05)",
        },
        logo: {
            fontSize: "26px",
            fontWeight: "bold",
            color: "#2563eb",
        },
        links: {
            display: "flex",
            gap: "25px",
            alignItems: "center",
        },
        link: {
            textDecoration: "none",
            color: "#334155",
            fontWeight: "bold",
        },
        button: {
            background: "#2563eb",
            color: "white",
            padding: "12px 24px",
            borderRadius: "8px",
            textDecoration: "none",
            fontWeight: "bold",
        },
        hero: {
            textAlign: "center",
            padding: "100px 20px 80px",
            background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
        },
        heading: {
            fontSize: "48px",
            marginBottom: "20px",
        },
        description: {
            fontSize: "18px",
            color: "#475569",
            maxWidth: "650px",
            margin: "0 auto 30px",
            lineHeight: "1.7",
        },
        section: {
            padding: "60px 8%",
            textAlign: "center",
        },
        cards: {
            display: "flex",
            justifyContent: "center",
            flexWrap: "wrap",
            gap: "25px",
            marginTop: "35px",
        },
        card: {
            background: "white",
            padding: "30px",
            borderRadius: "12px",
            width: "250px",
            boxShadow: "0 4px 15px rgba(0,0,0,0.06)",
        },
    };

    return (
        <div style={styles.page}>
            <nav style={styles.navbar}>
                <div style={styles.logo}>ShopSmart</div>

                <div style={styles.links}>
                    <Link to="/login" style={styles.link}>Login</Link>
                    <Link to="/register" style={styles.button}>
                        Get Started
                    </Link>
                </div>
            </nav>

            <section style={styles.hero}>
                <h1 style={styles.heading}>
                    Welcome to ShopSmart
                </h1>

                <p style={styles.description}>
                    Your one-stop multi-vendor shopping platform.
                    Discover products, explore different shops,
                    and enjoy a simple and convenient shopping experience.
                </p>

                <Link to="/register" style={styles.button}>
                    Create Your Account
                </Link>
            </section>

            <section style={styles.section}>
                <h2>What Makes ShopSmart Special?</h2>

                <div style={styles.cards}>
                    <div style={styles.card}>
                        <h3>🛍️ Explore Products</h3>
                        <p>
                            Discover products from different sellers
                            in one convenient marketplace.
                        </p>
                    </div>

                    <div style={styles.card}>
                        <h3>🏪 Become a Seller</h3>
                        <p>
                            Register your shop and apply to sell
                            your products on ShopSmart.
                        </p>
                    </div>

                    <div style={styles.card}>
                        <h3>🤖 Smart Shopping</h3>
                        <p>
                            Explore a smarter shopping experience
                            with our platform's features.
                        </p>
                    </div>
                </div>
            </section>

            <section style={{
                ...styles.section,
                background: "#172554",
                color: "white"
            }}>
                <h2>Start Your ShopSmart Journey</h2>
                <p>Join as a customer or apply to become a seller.</p>

                <Link to="/register" style={styles.button}>
                    Join ShopSmart
                </Link>
            </section>

            <footer style={{
                textAlign: "center",
                padding: "20px",
                color: "#64748b"
            }}>
                © 2026 ShopSmart. All rights reserved.
            </footer>
        </div>
    );
}

export default LandingPage;
