
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api/axios";

function Products() {
    const [products, setProducts] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [addingId, setAddingId] = useState(null);

    const fetchProducts = async (searchValue = "") => {
        try {
            setLoading(true);
            setError("");

            const response = await API.get("products/", {
                params: searchValue
                    ? { search: searchValue }
                    : {},
            });

            setProducts(response.data);
        } catch (err) {
            console.error("Product loading error:", err);
            setError("Unable to load products.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    const handleSearch = (e) => {
        e.preventDefault();
        fetchProducts(search);
    };

    const handleAddToCart = async (productId) => {
        try {
            setAddingId(productId);
            setMessage("");
            setError("");

            const token = localStorage.getItem("access");

            if (!token) {
                setError("Please login to add products to your cart.");
                return;
            }

            await API.post(
                "cart/add/",
                {
                    product: productId,
                    quantity: 1,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            setMessage("Product added to cart successfully!");
        } catch (err) {
            console.error(
                "Add to cart error:",
                err.response?.data || err.message
            );

            const data = err.response?.data;

            setError(
                typeof data === "string"
                    ? data
                    : data?.detail ||
                    data?.product ||
                    data?.quantity ||
                    "Unable to add product to cart."
            );
        } finally {
            setAddingId(null);
        }
    };

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart</div>

                <div className="nav-links">
                    <Link to="/home">Home</Link>
                    <Link to="/products">Products</Link>
                    <Link to="/cart">Cart</Link>
                    <Link to="/orders">My Orders</Link>
                </div>
            </nav>

            <div className="page-container">
                <h1>Explore Products</h1>
                <p>Find your favourite products at great prices.</p>

                <form onSubmit={handleSearch}>
                    <input
                        type="text"
                        placeholder="Search products..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />

                    <button type="submit">Search</button>
                </form>

                {message && (
                    <p style={{ color: "green" }}>{message}</p>
                )}

                {error && (
                    <p style={{ color: "red" }}>{error}</p>
                )}

                {loading && <p>Loading products...</p>}

                {!loading && products.length === 0 && !error && (
                    <p>No products found.</p>
                )}

                <div className="product-grid">
                    {products.map((product) => (
                        <div className="product-card" key={product.id}>
                            <div
                                style={{
                                    height: "150px",
                                    background: "#eaf0ff",
                                    borderRadius: "8px",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    fontSize: "45px",
                                    marginBottom: "18px",
                                }}
                            >
                                🛍️
                            </div>

                            <p>{product.category}</p>
                            <h2>{product.name}</h2>
                            <p>{product.description}</p>
                            <p>Sold by: {product.shop}</p>

                            <p className="price">
                                ₹{product.price}
                            </p>

                            <p>Stock: {product.stock}</p>

                            <button
                                onClick={() => handleAddToCart(product.id)}
                                disabled={
                                    product.stock <= 0 ||
                                    addingId === product.id
                                }
                            >
                                {addingId === product.id
                                    ? "Adding..."
                                    : product.stock > 0
                                        ? "Add to Cart"
                                        : "Out of Stock"}
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Products;
