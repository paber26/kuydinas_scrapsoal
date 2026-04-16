// node scripts/masukkan_soal_otomatis/cari_teks.js

const fs = require("fs")
const path = require("path")

// Kata kunci teks yang ingin Anda cari (bisa diubah sesuai keperluan)
const SEARCH_TEXT = "Jika seorang PNS menerima tawaran imbalan dari masyarakat"

// Daftar ekstensi file yang diizinkan untuk dicari (opsional)
const ALLOWED_EXTENSIONS = [".txt", ".json", ".js", ".py"]

function searchInFile(filePath, searchText) {
  try {
    const isiFile = fs.readFileSync(filePath, "utf8")
    const baris = isiFile.split("\n")

    baris.forEach((teksBaris, indexBaris) => {
      if (teksBaris.includes(searchText)) {
        console.log(`[Ditemukan] ${filePath}`)
        console.log(`  └─ Baris ${indexBaris + 1}: ${teksBaris.trim().substring(0, 100)}...`)
        console.log("-".repeat(40))
      }
    })
  } catch (error) {
    // Abaikan error file tidak bisa dibaca (seperti file .png atau binary archive)
  }
}

function walkDir(dir) {
  const fileDaftar = fs.readdirSync(dir)

  fileDaftar.forEach((file) => {
    const cekPath = path.join(dir, file)
    const cekStat = fs.statSync(cekPath)

    if (cekStat.isDirectory()) {
      // Lewati folder cache yang tidak relevan
      if (!file.includes("node_modules") && !file.includes(".venv") && !file.includes("__pycache__")) {
        walkDir(cekPath)
      }
    } else {
      const ekstensi = path.extname(cekPath).toLowerCase()
      // Hanya cek file yang masuk daftar ektensi teks
      if (ALLOWED_EXTENSIONS.includes(ekstensi) || ekstensi === "") {
        searchInFile(cekPath, SEARCH_TEXT)
      }
    }
  })
}

// Mulai pencarian dari parent directory folder script ini (/scrapsoal)
const startDirectory = path.join(__dirname, "../../")
console.log(`🔎 Mulai mencari teks: "${SEARCH_TEXT}" \nDi dalam folder: ${path.resolve(startDirectory)}\n`)

walkDir(startDirectory)

console.log("✅ Pencarian selesai!")
