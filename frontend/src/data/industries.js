export const INDUSTRIES = [
    {
        id: "construction",
        emoji: "🏗",
        name: "Construction",
        title: "Compliance reminders for construction companies",
        subtitle:
            "Track safety training, worker medical checks, equipment inspections and fire safety deadlines.",
        bullets: [
            "Health & safety training",
            "Equipment inspections",
            "Worker medical exams",
            "Fire safety checks"
        ]
    },
    {
        id: "transport",
        emoji: "🚛",
        name: "Transport",
        title: "Compliance reminders for transport companies",
        subtitle:
            "Track vehicle inspections, driver licenses, medical certificates, insurance and fleet maintenance.",
        bullets: [
            "Vehicle inspections",
            "Driver licenses",
            "Insurance renewals",
            "Fleet maintenance"
        ]
    },
    {
        id: "production",
        emoji: "🏭",
        name: "Production",
        title: "Compliance reminders for production companies",
        subtitle:
            "Track machine inspections, equipment calibration, safety training and ISO certification dates.",
        bullets: [
            "Machine inspections",
            "Equipment calibration",
            "Safety training",
            "ISO reviews"
        ]
    },
    {
        id: "healthcare",
        emoji: "🏥",
        name: "Healthcare",
        title: "Compliance reminders for healthcare organizations",
        subtitle:
            "Track staff certifications, medical equipment inspections, training and important compliance deadlines.",
        bullets: [
            "Staff certifications",
            "Equipment inspections",
            "Mandatory training",
            "Policy reviews"
        ]
    },
    {
        id: "hospitality",
        emoji: "🏨",
        name: "Hospitality",
        title: "Compliance reminders for hospitality businesses",
        subtitle:
            "Track food safety checks, employee training, equipment inspections and license renewals.",
        bullets: [
            "Food safety checks",
            "Employee training",
            "Equipment inspections",
            "License renewals"
        ]
    }
];

export function getIndustryById(industryId) {
    return INDUSTRIES.find((industry) => industry.id === industryId);
}