import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function Cart() {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [updatingId, setUpdatingId] = useState(null);

    const navigate = useNavigate();

    const getAuthConfig = () => {
        const token = localStorage.getItem("access");

        return {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        };
    };

    const fetchCart = async () => {
        try {
            setLoading(true);
            setError("");

            const token = localStorage.getItem("access");

            if (!token) {
                navigate("/");
                return;
            }

            const response = await API.get(
                "cart/",
                getAuthConfig()
            );

            console.log("Cart API response:", response.data);

            setCart(response.data);
        } catch (err) {
            console.error(
                "Cart loading error:",
                err.response?.data || err.message
            );

            setError("Unable to load your cart.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCart();
    }, []);

    const updateQuantity = async (itemId, quantity) => {
        try {
            setUpdatingId(itemId);
            setError("");

            const response = await API.patch(
                `cart/items/${itemId}/`,
                { quantity },
                getAuthConfig()
            );

            setCart(response.data);
        } catch (err) {
            console.error(
                "Quantity update error:",
                err.response?.data || err.message
            );

            const data = err.response?.data;

            setError(
                data?.quantity ||
                data?.detail ||
                "Unable to update quantity."
            );
        } finally {
            setUpdatingId(null);
        }
    };

    const removeItem = async (itemId) => {
        try {
            setUpdatingId(itemId);
            setError("");

            const response = await API.delete(
                `cart/items/${itemId}/remove/`,
                getAuthConfig()
            );

            setCart(response.data);
        } catch (err) {
            console.error(
                "Remove item error:",
                err.response?.data || err.message
            );

            setError("Unable to remove product.");
        } finally {
            setUpdatingId(null);
        }
    };

    if (loading) {
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
                    <h1>Shopping Cart</h1>
                    <p>Loading your cart...</p>
                </div>
            </div>
        );
    }

    const items = Array.isArray(cart?.items)
        ? cart.items
        : [];

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
                <h1>Shopping Cart</h1>

                <p>Review your selected products.</p>

                {error && (
                    <p style={{ color: "red" }}>
                        {error}
                    </p>
                )}

                <div className="card">
                    {items.length === 0 ? (
                        <div>
                            <h2>Your cart is empty!</h2>

                            <p>
                                Add some products to get started.
                            </p>

                            <Link to="/products">
                                <button>
                                    Explore Products
                                </button>
                            </Link>
                        </div>
                    ) : (
                        <>
                            {items.map((item) => (
                                <div
                                    key={item.id}
                                    style={{
                                        padding: "15px 0",
                                        borderBottom:
                                            "1px solid #ddd",
                                    }}
                                >
                                    <h2>
                                        {item.product_name}
                                    </h2>

                                    <p>
                                        Price: ₹
                                        {Number(
                                            item.product_price
                                        ).toFixed(2)}
                                    </p>

                                    <p>
                                        Subtotal: ₹
                                        {Number(
                                            item.subtotal
                                        ).toFixed(2)}
                                    </p>

                                    <div
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: "12px",
                                            marginTop: "10px",
                                        }}
                                    >
                                        <button
                                            disabled={
                                                item.quantity <= 1 ||
                                                updatingId === item.id
                                            }
                                            onClick={() =>
                                                updateQuantity(
                                                    item.id,
                                                    item.quantity - 1
                                                )
                                            }
                                        >
                                            -
                                        </button>

                                        <span>
                                            {item.quantity}
                                        </span>

                                        <button
                                            disabled={
                                                updatingId === item.id
                                            }
                                            onClick={() =>
                                                updateQuantity(
                                                    item.id,
                                                    item.quantity + 1
                                                )
                                            }
                                        >
                                            +
                                        </button>

                                        <button
                                            disabled={
                                                updatingId === item.id
                                            }
                                            onClick={() =>
                                                removeItem(item.id)
                                            }
                                        >
                                            {updatingId === item.id
                                                ? "Please wait..."
                                                : "Remove"}
                                        </button>
                                    </div>
                                </div>
                            ))}

                            <h2 style={{ marginTop: "20px" }}>
                                Total: ₹
                                {Number(
                                    cart?.total || 0
                                ).toFixed(2)}
                            </h2>

                            <button
                                onClick={() =>
                                    navigate("/checkout")
                                }
                            >
                                Proceed to Checkout
                            </button>
                        </>
                    )}
                </div>

                <p style={{ marginTop: "20px" }}>
                    <Link to="/products">
                        Continue Shopping
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Cart;