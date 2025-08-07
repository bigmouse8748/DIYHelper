require('dotenv').config();
const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const { OpenAI } = require('openai');

const app = express();
app.use(cors());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(__dirname));

const upload = multer({ dest: 'uploads/' });
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

app.post('/upload', upload.array('images', 4), async (req, res) => {
  try {
    const systemPrompt = req.body.prompt?.trim() ||
      'You are an assistant that identifies objects and provides brief descriptions of each object in the image.';

    const results = [];
    for (const file of req.files) {
      const dataUri = `data:${file.mimetype};base64,${fs.readFileSync(file.path, 'base64')}`;

      const response = await openai.chat.completions.create({
        model: 'gpt-4o',
        messages: [
          { role: 'system', content: systemPrompt },
          {
            role: 'user',
            content: [
              { type: 'text', text: 'Analyze this image and describe each object you see briefly:' },
              { type: 'image_url', image_url: { url: dataUri } }
            ]
          }
        ],
        max_tokens: 500
      });

      const description = response.choices[0].message.content.trim();
      results.push({ filename: file.originalname, description });
      fs.unlinkSync(file.path);
    }

    res.json({ results });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || 'Internal server error' });
  }
});

/**
 * Dynamic port binding: try initial port, then increment on conflict
 */
function startServer(port = parseInt(process.env.PORT, 10) || 3000) {
  const server = app.listen(port, () => {
    console.log(`Server running on port ${port}`);
  });
  server.on('error', err => {
    if (err.code === 'EADDRINUSE') {
      console.warn(`Port ${port} in use, trying ${port + 1}`);
      startServer(port + 1);
    } else {
      console.error(err);
      process.exit(1);
    }
  });
}

startServer();
