import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import api from "../../lib/api";
import { getIndustryById } from "../../data/industries";


export default function IndustryTemplateSetup() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const industry = searchParams.get("industry");
    const industryData = industry
        ? getIndustryById(industry)
        : null;

    const [template, setTemplate] = useState(null);
    const [selections, setSelections] = useState({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);


    useEffect(() => {
        if (!industry) {
            setError("Industry is missing.");
            setLoading(false);
            return;
        }

        loadTemplate();
    }, [industry]);


    const loadTemplate = async () => {
        try {
            setLoading(true);
            setError(null);

            const res = await api.get(
                `/industry-templates/${industry}`
            );

            setTemplate(res.data);

        } catch (e) {
            console.error(
                "LOAD INDUSTRY TEMPLATE ERROR:",
                e
            );

            setError(
                "Could not load industry templates."
            );

        } finally {
            setLoading(false);
        }
    };


    const getKey = (groupName, workflowTitle) =>
        `${groupName}|||${workflowTitle}`;


    const toggleWorkflow = (
        groupName,
        workflowTitle
    ) => {
        const key = getKey(
            groupName,
            workflowTitle
        );

        setSelections((current) => ({
            ...current,
            [key]: {
                selected:
                    !current[key]?.selected,
                due_date:
                    current[key]?.due_date || "",
                group_name: groupName,
                workflow_title: workflowTitle,
            },
        }));
    };


    const setDueDate = (
        groupName,
        workflowTitle,
        value
    ) => {
        const key = getKey(
            groupName,
            workflowTitle
        );

        setSelections((current) => ({
            ...current,
            [key]: {
                ...current[key],
                selected: true,
                due_date: value,
                group_name: groupName,
                workflow_title: workflowTitle,
            },
        }));
    };


    const applyTemplates = async () => {
        const selected = Object.values(
            selections
        ).filter((item) => item.selected);

        if (selected.length === 0) {
            alert(
                "Choose at least one workflow."
            );
            return;
        }

        const missingDate = selected.find(
            (item) => !item.due_date
        );

        if (missingDate) {
            alert(
                `Missing deadline for "${missingDate.workflow_title}".\n\n` +
                `Please enter a due date before creating your workflows. ` +
                `ExpireHeros needs this date to protect you from missing the deadline.`
            );
            return;
        }

        try {
            setSaving(true);

            const res = await api.post(
                `/industry-templates/${industry}/apply`,
                {
                    workflows: selected.map(
                        (item) => ({
                            group_name:
                                item.group_name,
                            workflow_title:
                                item.workflow_title,
                            due_date:
                                item.due_date,
                        })
                    ),
                }
            );

            navigate("/");


        } catch (e) {
            console.error(
                "APPLY INDUSTRY TEMPLATE ERROR:",
                e
            );

            alert(
                e.response?.data?.detail ||
                "Could not create workflows."
            );

        } finally {
            setSaving(false);
        }
    };


    if (loading) {
        return (
            <div style={page}>
                <div style={card}>
                    Loading templates...
                </div>
            </div>
        );
    }


    if (error || !template) {
        return (
            <div style={page}>
                <div style={card}>
                    <h2>
                        Something went wrong
                    </h2>

                    <p>{error}</p>

                    <button
                        style={primaryButton}
                        onClick={() =>
                            navigate("/dashboard")
                        }
                    >
                        Go to dashboard
                    </button>
                </div>
            </div>
        );
    }


    return (
        <div style={page}>
            <div style={container}>

                <div style={header}>
                    <div
                        style={{
                            fontSize: 44,
                            marginBottom: 10,
                        }}
                    >
                        {industryData?.emoji || "🛡️"}
                    </div>

                    <h1 style={title}>
                        Set up your{" "}
                        {template.label ||
                            industryData?.name ||
                            "company"}{" "}
                        workflows
                    </h1>

                    <p style={subtitle}>
                        Choose the deadlines you want
                        ExpireHeros to protect.
                        Everything can be edited later.
                    </p>
                </div>


                <div style={groups}>
                    {template.groups.map(
                        (group) => (
                            <div
                                key={group.name}
                                style={groupCard}
                            >
                                <div
                                    style={
                                        groupHeader
                                    }
                                >
                                    <div>
                                        <h2
                                            style={
                                                groupTitle
                                            }
                                        >
                                            {group.name}
                                        </h2>

                                        <p
                                            style={
                                                groupDescription
                                            }
                                        >
                                            {
                                                group.description
                                            }
                                        </p>
                                    </div>
                                </div>


                                <div
                                    style={
                                        workflowList
                                    }
                                >
                                    {group.workflows.map(
                                        (workflow) => {
                                            const key =
                                                getKey(
                                                    group.name,
                                                    workflow.title
                                                );

                                            const selection =
                                                selections[
                                                key
                                                ];

                                            const checked =
                                                Boolean(
                                                    selection?.selected
                                                );

                                            return (
                                                <div
                                                    key={
                                                        workflow.title
                                                    }
                                                    style={{
                                                        ...workflowRow,
                                                        ...(checked
                                                            ? workflowRowSelected
                                                            : {}),
                                                    }}
                                                >
                                                    <label
                                                        style={
                                                            workflowMain
                                                        }
                                                    >
                                                        <input
                                                            type="checkbox"
                                                            checked={
                                                                checked
                                                            }
                                                            onChange={() =>
                                                                toggleWorkflow(
                                                                    group.name,
                                                                    workflow.title
                                                                )
                                                            }
                                                            style={
                                                                checkbox
                                                            }
                                                        />

                                                        <div>
                                                            <div
                                                                style={
                                                                    workflowTitle
                                                                }
                                                            >
                                                                {
                                                                    workflow.title
                                                                }
                                                            </div>

                                                            <div
                                                                style={
                                                                    workflowMeta
                                                                }
                                                            >
                                                                {workflow.recurrence_months >
                                                                    0
                                                                    ? `Repeats every ${workflow.recurrence_months} month(s)`
                                                                    : "One-time or manually renewed"}
                                                            </div>
                                                        </div>
                                                    </label>


                                                    {checked && (
                                                        <div
                                                            style={
                                                                dateBox
                                                            }
                                                        >
                                                            <label
                                                                style={
                                                                    dateLabel
                                                                }
                                                            >
                                                                Next
                                                                due
                                                                date
                                                            </label>

                                                            <input
                                                                type="date"
                                                                value={
                                                                    selection?.due_date ||
                                                                    ""
                                                                }
                                                                onChange={(
                                                                    e
                                                                ) =>
                                                                    setDueDate(
                                                                        group.name,
                                                                        workflow.title,
                                                                        e
                                                                            .target
                                                                            .value
                                                                    )
                                                                }
                                                                style={
                                                                    dateInput
                                                                }
                                                            />
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        }
                                    )}
                                </div>
                            </div>
                        )
                    )}
                </div>


                <div style={footer}>
                    <button
                        onClick={() =>
                            navigate("/dashboard")
                        }
                        style={secondaryButton}
                        disabled={saving}
                    >
                        Skip for now
                    </button>

                    <button
                        onClick={applyTemplates}
                        style={primaryButton}
                        disabled={saving}
                    >
                        {saving
                            ? "Creating..."
                            : "Create my workflows"}
                    </button>
                </div>

            </div>
        </div>
    );
}


const page = {
    minHeight: "100vh",
    background:
        "linear-gradient(135deg, #dbeafe, #eff6ff)",
    padding: "48px 20px",
    fontFamily: "Inter, sans-serif",
    boxSizing: "border-box",
};


const container = {
    width: "100%",
    maxWidth: 980,
    margin: "0 auto",
};


const header = {
    textAlign: "center",
    marginBottom: 34,
};


const title = {
    fontSize: 36,
    color: "#0f172a",
    margin: "0 0 12px",
};


const subtitle = {
    color: "#64748b",
    fontSize: 17,
    lineHeight: 1.6,
    maxWidth: 650,
    margin: "0 auto",
};


const groups = {
    display: "flex",
    flexDirection: "column",
    gap: 20,
};


const groupCard = {
    background: "rgba(255,255,255,0.85)",
    borderRadius: 22,
    padding: 24,
    border: "1px solid #dbeafe",
    boxShadow:
        "0 12px 30px rgba(37,99,235,0.08)",
};


const groupHeader = {
    marginBottom: 18,
};


const groupTitle = {
    margin: "0 0 6px",
    fontSize: 21,
    color: "#0f172a",
};


const groupDescription = {
    margin: 0,
    color: "#64748b",
    fontSize: 14,
};


const workflowList = {
    display: "flex",
    flexDirection: "column",
    gap: 10,
};


const workflowRow = {
    border: "1px solid #e2e8f0",
    borderRadius: 16,
    padding: 16,
    background: "#ffffff",
};


const workflowRowSelected = {
    border: "1px solid #93c5fd",
    background: "#f8fbff",
};


const workflowMain = {
    display: "flex",
    alignItems: "center",
    gap: 14,
    cursor: "pointer",
};


const checkbox = {
    width: 20,
    height: 20,
    cursor: "pointer",
};


const workflowTitle = {
    fontWeight: 700,
    color: "#0f172a",
};


const workflowMeta = {
    marginTop: 4,
    fontSize: 13,
    color: "#64748b",
};


const dateBox = {
    marginTop: 14,
    marginLeft: 34,
    display: "flex",
    alignItems: "center",
    gap: 12,
};


const dateLabel = {
    fontSize: 13,
    fontWeight: 700,
    color: "#475569",
};


const dateInput = {
    border: "1px solid #dbeafe",
    borderRadius: 10,
    padding: "10px 12px",
    color: "#0f172a",
    background: "white",
};


const footer = {
    marginTop: 30,
    display: "flex",
    justifyContent: "flex-end",
    gap: 12,
};


const card = {
    width: "100%",
    maxWidth: 600,
    margin: "100px auto",
    background: "white",
    borderRadius: 22,
    padding: 40,
    textAlign: "center",
};


const primaryButton = {
    border: "none",
    borderRadius: 999,
    padding: "14px 24px",
    background:
        "linear-gradient(135deg, #3b82f6, #60a5fa)",
    color: "white",
    fontWeight: 800,
    fontSize: 15,
    cursor: "pointer",
    boxShadow:
        "0 10px 25px rgba(59,130,246,0.3)",
};


const secondaryButton = {
    border: "1px solid #cbd5e1",
    borderRadius: 999,
    padding: "14px 24px",
    background: "white",
    color: "#475569",
    fontWeight: 700,
    fontSize: 15,
    cursor: "pointer",
};