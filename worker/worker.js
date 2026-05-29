const JOB_URL = process.env.JOB_URL || "https://api.expireheros.app/jobs/run";

async function runJob() {
    console.log("🚀 Running reminder job:", new Date().toISOString());

    try {
        const res = await fetch(JOB_URL, {
            method: "POST"
        });

        const text = await res.text();

        console.log("📬 Status:", res.status);
        console.log("📦 Response:", text);
    } catch (err) {
        console.error("❌ Worker error:", err);
    }
}

async function main() {
    await runJob();

    setInterval(runJob, 60 * 60 * 1000);
}

main();