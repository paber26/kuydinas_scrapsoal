const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// ==========================================================
// PENGATURAN MODUL
// Silakan tuliskan nomor modul yang ingin diisi di dalam array ini.
// Contoh: ['584', '585', '586']
// ==========================================================
const DAFTAR_MODUL = ['584', '585', '586'];

function cleanQuestion(text) {
  if (!text) return text;
  return text.replace(/^Pertanyaan \d+\nTidak dijawab\n/i, '').trim();
}

async function run() {
  // Gunakan argumen CLI jika ada, jika tidak gunakan DAFTAR_MODUL dari pengaturan di atas
  let targetModules = process.argv.slice(2);
  if (targetModules.length === 0) {
    targetModules = DAFTAR_MODUL;
  }

  const allData = [];
  for (const argModul of targetModules) {
    const filePath = path.resolve(__dirname, '..', `hasil_pembahasan_modul_${argModul}/pembahasan_modul_${argModul}.json`);

    if (!fs.existsSync(filePath)) {
      console.error(`Error: File tidak ditemukan di ${filePath}`);
      process.exit(1);
    }

    console.log(`Membaca data dari modul ${argModul}...`);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    allData.push(...data);
  }
  const slicedData = allData;

  console.log('Membuka browser chrome (headless)...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  context.setDefaultTimeout(60000);
  const page = await context.newPage();

  console.log('Navigasi ke halaman login...');
  await page.goto('http://127.0.0.1:5173/login');

  // Fill login
  await page.fill('input[type="email"]', 'admin@gmail.com');
  await page.fill('input[type="password"]', '12345678');
  await page.click('button:has-text("Login")');

  // Tunggu login selesai
  console.log('Menunggu login selesai...');
  try {
    await page.waitForSelector('text=Dashboard', { timeout: 10000 });
    console.log('Login berhasil!');
  } catch (e) {
    console.log('Login mungkin gagal atau lambat, mencoba lanjut...');
  }

  console.log(`Mulai mengisi ${slicedData.length} soal...`);

  for (const item of slicedData) {
    try {
      console.log(`Mengisi soal ${item.nomor}: ${item.pertanyaan.substring(0, 30).replace(/\n/g, '')}...`);
      await page.goto('http://127.0.0.1:5173/banksoal/create');

      // Tunggu page load
      await page.waitForSelector('h1:has-text("Tambah Soal SKD")', { timeout: 10000 });

      // Pilih kategori (Kategori adalah select pertama)
      const category = item.sub_modul || 'TWK';
      await page.locator('select').first().selectOption(category);

      // Pertanyaan
      await page.getByPlaceholder('Masukkan pertanyaan soal...').fill(cleanQuestion(item.pertanyaan));

      // Opsi Jawaban
      const optionInputs = page.getByPlaceholder('Isi opsi jawaban');
      const radioInputs = page.locator('input[type="radio"]');
      const scoreInputs = page.getByPlaceholder('Skor');

      const isTKP = category === 'TKP';

      let correctAnswerIndex = 0;
      for (let i = 0; i < 5; i++) {
        let rawOptText = (item.pilihan && item.pilihan[i]) || '-';
        let optText = rawOptText;
        let score = null;

        // Jika TKP, ekstrak score dari text (Nilai X)
        if (isTKP) {
          const scoreMatch = rawOptText.match(/\(Nilai (\d+)\)/);
          if (scoreMatch) {
            score = scoreMatch[1];
            // Bersihkan text dari (Nilai X)
            optText = rawOptText.replace(/\(Nilai \d+\)/, '').trim();
          }
        }

        await optionInputs.nth(i).fill(optText);

        if (isTKP) {
          if (score !== null) {
            await scoreInputs.nth(i).fill(score.toString());
          }
        } else {
          if (item.jawaban_benar && item.pilihan[i] && rawOptText.trim().startsWith(item.jawaban_benar.trim())) {
            correctAnswerIndex = i;
          }
        }
      }

      // Klik radio button jawaban yang benar jika bukan TKP
      if (!isTKP) {
        await radioInputs.nth(correctAnswerIndex).click();
      }

      // Pembahasan
      if (item.pembahasan) {
        await page.getByPlaceholder('Masukkan pembahasan soal...').fill(item.pembahasan);
      }

      // Tunggu sebentar biar mantap
      await page.waitForTimeout(500);

      // Click Simpan Soal
      await page.getByRole('button', { name: /Simpan Soal/i }).click();

      // Tunggu sampai redirect ke halaman banksoal
      console.log(`Berhasil menyimpan soal ${item.nomor}. Menunggu navigasi...`);
      await page.waitForURL('**/banksoal', { timeout: 10000 });
      await page.waitForTimeout(500);
    } catch (err) {
      console.error(`Gagal mengisi soal ${item.nomor}:`, err.message);
      try {
        await page.screenshot({ path: `error_soal_${item.nomor}.png` });
      } catch (screenshotErr) {
        console.error('Gagal mengambil screenshot:', screenshotErr.message);
      }
      continue;
    }
  }

  console.log(`Pengisian ${slicedData.length} soal selesai. Menutup browser...`);
  await browser.close();
}

process.on('SIGINT', () => {
  console.log('SIGINT received, exiting gracefully...');
  process.exit(130);
});

run().catch(console.error);
