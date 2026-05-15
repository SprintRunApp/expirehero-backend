import { useEffect, useState } from "react";
import api from "../lib/api";

export default function Items() {

    const [items, setItems] = useState([]);

    useEffect(() => {
        api.get("/items")
            .then(r => setItems(r.data));
    }, []);

    return (

        <div className="p-8">

            <h1 className="text-2xl mb-6">Items</h1>

            {items.map(item => (

                <div
                    key={item.id}
                    className="border p-4 rounded-lg mb-3"
                >

                    <div className="font-bold">{item.title}</div>
                    <div>{item.category}</div>

                </div>

            ))}

        </div>
    );
}