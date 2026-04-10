const fs = require("fs");
const path = require("path");
const axios = require("axios");

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function getRangeFolder(id) {
  const lower = Math.floor((id - 1) / 50) * 50 + 1;
  const upper = lower + 49;
  return `${lower}-${upper}`;
}

const BASE_URL = "https://apikuy.kuydinas.id/api/admin";

async function login() {
  try {
    const res = await axios.post(`${BASE_URL}/login`, {
      email: "admin@gmail.com",
      password: "12345678",
    });
    return res.data.data ? res.data.data.token : res.data.token;
  } catch (err) {
    console.error("Login failed", err.response?.data || err.message);
    process.exit(1);
  }
}

async function addSoal(token, payload) {
  try {
    const res = await axios.post(`${BASE_URL}/soal`, payload, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    console.log(
      `Successfully added soal: ${payload.category} - ${payload.question.substring(0, 30).replace(/\n/g, " ")}...`,
    );
  } catch (err) {
    console.error(`Failed to add soal:`, err.response?.data || err.message);
  }
}

function parseTKPOption(textHtml) {
  let score = null;
  const match = textHtml.match(/\(Nilai\s*(\d+)\)/i);
  if (match) {
    score = parseInt(match[1], 10);
    textHtml = textHtml.replace(match[0], "").trim();
  }
  return { text: textHtml, score };
}

function cleanQuestion(text) {
  if (!text) return text;
  return text.replace(/^Pertanyaan \d+\nTidak dijawab\n/i, "").trim();
}

async function run() {
  console.log("Logging in...");
  const token = await login();
  console.log("Logged in successfully!");

  const modulesToProcess = [
    { id: 390, category: "TWK" },
    { id: 391, category: "TIU" },
    { id: 392, category: "TKP" },
  ];

  for (const mod of modulesToProcess) {
    console.log(`\nProcessing ${mod.category} (modul ${mod.id})...`);
    const range = getRangeFolder(mod.id);
    const filePath = `../../data/pembahasan/${range}/hasil_pembahasan_modul_${mod.id}/pembahasan_modul_${mod.id}.json`;
    const fullPath = path.resolve(__dirname, filePath);
    if (!fs.existsSync(fullPath)) {
      console.warn(`File not found: ${fullPath}, skipping...`);
      continue;
    }

    let data = JSON.parse(fs.readFileSync(fullPath, "utf8"));

    // Sort by nomor to ensure they are added in order
    data.sort((a, b) => (a.nomor || 0) - (b.nomor || 0));

    for (const item of data) {
      const options = [];
      let correctAnswer = null;
      const labels = ["A", "B", "C", "D", "E"];

      for (let i = 0; i < 5; i++) {
        let optText = item.pilihan[i] || "-";

        if (mod.category === "TKP") {
          const parsed = parseTKPOption(optText);
          options.push({
            label: labels[i],
            text: parsed.text,
            score: parsed.score || 1,
          });
        } else {
          options.push({ label: labels[i], text: optText });
          if (
            item.jawaban_benar &&
            item.pilihan[i] &&
            optText.trim() === item.jawaban_benar.trim()
          ) {
            correctAnswer = labels[i];
          }
        }
      }

      if (mod.category !== "TKP") {
        if (!correctAnswer && item.jawaban_benar) {
          for (let i = 0; i < item.pilihan.length; i++) {
            if (
              item.jawaban_benar.includes(item.pilihan[i].trim()) ||
              item.pilihan[i].includes(item.jawaban_benar.trim())
            ) {
              correctAnswer = labels[i];
              break;
            }
          }
        }
        if (!correctAnswer) correctAnswer = "A";
      }

      const payload = {
        category: mod.category,
        sub_category: null,
        difficulty: null,
        number: item.nomor,
        question: cleanQuestion(item.pertanyaan),
        options: options,
        correct_answer: mod.category === "TKP" ? null : correctAnswer,
        explanation: item.pembahasan ? item.pembahasan.trim() : null,
        status: "aktif",
      };

      console.log(`Processing Soal #${item.nomor}...`);
      await addSoal(token, payload);
      await sleep(1000); // Increased to 1000ms to ensure server-side ordering
    }
  }

  console.log("\nFinished all modules!");
}

run();
