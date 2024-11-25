const express = require('express');
const cors = require('cors'); // Import CORS
const { exec } = require('child_process');
const path = require('path');

const app = express();

// Enable CORS for specific origin
app.use(cors({ origin: 'https://vidownloader-net.onrender.com' }));

app.use(express.json());

app.post('/download', (req, res) => {
  const url = req.body.url;

  if (!url) {
    return res.status(400).json({ error: 'No URL provided' });
  }

  const ytDlpPath = path.join(__dirname, 'bin', 'yt-dlp');
  const command = `"${ytDlpPath}" --get-url -f mp4 "${url}"`;

  exec(command, { maxBuffer: 1024 * 500 }, (error, stdout, stderr) => {
    if (error) {
      console.error('Error executing yt-dlp:', stderr);
      return res.status(500).json({ error: 'Failed to fetch download link.', details: stderr });
    }

    const downloadLink = stdout.trim();
    if (downloadLink) {
      res.json({ downloadLink });
    } else {
      res.status(500).json({ error: 'No download link found.' });
    }
  });
});

app.listen(3000, () => {
  console.log('Server is running on http://localhost:3000');
});
