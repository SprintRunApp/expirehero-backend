import api from "../lib/api";

export default function UpgradeButton() {

    const upgrade = async () => {

        const res = await api.post("/payments/create-checkout-session")

        window.location.href = res.data.checkout_url

    }

    return (

        <button
            onClick={upgrade}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg"
        >
            Upgrade to PRO
        </button>

    )

}