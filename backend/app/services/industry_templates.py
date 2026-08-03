INDUSTRY_TEMPLATES = {
    "transport": {
        "label": "Transport & Logistics",
        "groups": [
            {
                "name": "Fleet",
                "description": "Vehicle-related inspections, documents and maintenance.",
                "workflows": [
                    {
                        "title": "Annual vehicle inspection",
                        "category": "Fleet",
                        "recurrence_months": 12,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Vehicle insurance",
                        "category": "Fleet",
                        "recurrence_months": 12,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Tachograph calibration",
                        "category": "Fleet",
                        "recurrence_months": 24,
                        "advance_days": [60, 30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Vehicle maintenance",
                        "category": "Fleet",
                        "recurrence_months": 0,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Leasing or rental expiry",
                        "category": "Fleet",
                        "recurrence_months": 0,
                        "advance_days": [60, 30, 14, 7, 3, 1],
                    },
                ],
            },
            {
                "name": "Drivers",
                "description": "Driver licences, qualifications and medical requirements.",
                "workflows": [
                    {
                        "title": "Driving licence expiry",
                        "category": "Drivers",
                        "recurrence_months": 0,
                        "advance_days": [90, 60, 30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Code 95 qualification",
                        "category": "Drivers",
                        "recurrence_months": 0,
                        "advance_days": [90, 60, 30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Driver medical examination",
                        "category": "Drivers",
                        "recurrence_months": 0,
                        "advance_days": [60, 30, 14, 7, 3, 1],
                    },
                    {
                        "title": "ADR certificate",
                        "category": "Drivers",
                        "recurrence_months": 0,
                        "advance_days": [90, 60, 30, 14, 7, 3, 1],
                    },
                ],
            },
            {
                "name": "Warehouse",
                "description": "Warehouse equipment, inspections and operational safety.",
                "workflows": [
                    {
                        "title": "Forklift inspection",
                        "category": "Warehouse",
                        "recurrence_months": 12,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Forklift operator certificate",
                        "category": "Warehouse",
                        "recurrence_months": 0,
                        "advance_days": [60, 30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Racking inspection",
                        "category": "Warehouse",
                        "recurrence_months": 12,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Loading equipment inspection",
                        "category": "Warehouse",
                        "recurrence_months": 12,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                ],
            },
            {
                "name": "Safety & Compliance",
                "description": "Company-wide safety and compliance obligations.",
                "workflows": [
                    {
                        "title": "Fire extinguisher inspection",
                        "category": "Safety",
                        "recurrence_months": 12,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                    {
                        "title": "First aid kit inspection",
                        "category": "Safety",
                        "recurrence_months": 12,
                        "advance_days": [30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Safety training renewal",
                        "category": "Safety",
                        "recurrence_months": 0,
                        "advance_days": [60, 30, 14, 7, 3, 1],
                    },
                ],
            },
            {
                "name": "Contracts & Documents",
                "description": "Business contracts, permits and company documentation.",
                "workflows": [
                    {
                        "title": "Supplier contract expiry",
                        "category": "Contracts",
                        "recurrence_months": 0,
                        "advance_days": [90, 60, 30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Service contract expiry",
                        "category": "Contracts",
                        "recurrence_months": 0,
                        "advance_days": [90, 60, 30, 14, 7, 3, 1],
                    },
                    {
                        "title": "Operating permit expiry",
                        "category": "Documents",
                        "recurrence_months": 0,
                        "advance_days": [90, 60, 30, 14, 7, 3, 1],
                    },
                ],
            },
        ],
    },
}