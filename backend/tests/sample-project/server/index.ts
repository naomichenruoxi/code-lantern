import express from 'express';
import cors from 'cors';

const app = express();
const port = process.env.PORT || 5173;

app.use(cors());
app.use(express.json());

app.post('/api/generate-summary', async (req, res) => {
  try {
    const { text } = req.body;
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    // Add your summary generation logic here
    // For now, returning a mock response
    const summary = {
      summary: 'Sample summary',
      questions: [
        {
          question: 'Sample question?',
          options: ['A', 'B', 'C', 'D'],
          correctAnswer: 'A'
        }
      ]
    };

    res.json(summary);
  } catch (error) {
    console.error('Error generating summary:', error);
    res.status(500).json({ error: 'Failed to generate summary' });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
