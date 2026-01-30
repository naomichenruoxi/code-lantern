import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { Quiz, QuizSubmission, ReadinessReport } from './types';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

if (!process.env.GEMINI_API_KEY) {
  console.error('GEMINI_API_KEY is not set in environment variables');
  process.exit(1);
}

// Single model initialization
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

// Simple in-memory cache & rate limit state
const quizCache = new Map<string, any>();
interface RateBucket { count: number; resetAt: number }
const rateBucket: RateBucket = { count: 0, resetAt: Date.now() + 60_000 };
const MAX_REQUESTS_PER_MINUTE = 6; // adjust as needed

function checkRateLimit() {
  const now = Date.now();
  if (now > rateBucket.resetAt) {
    rateBucket.count = 0;
    rateBucket.resetAt = now + 60_000;
  }
  rateBucket.count++;
  return rateBucket.count <= MAX_REQUESTS_PER_MINUTE;
}

async function safeGenerate(prompt: string): Promise<string | null> {
  const MAX_ATTEMPTS = 3;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      const result = await model.generateContent(prompt);
      return result.response.text();
    } catch (err: any) {
      const status = err?.status;
      const msg = err?.message || '';
      if (status === 429) {
        console.warn(`[RATE LIMIT] attempt ${attempt} status 429. Backing off.`);
        // exponential backoff capped
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 4000);
        await new Promise(r => setTimeout(r, delay));
        continue; // retry
      }
      console.error('[GENERATION ERROR NON-RETRY]', msg);
      return null; // non retryable
    }
  }
  return null;
}

function generateFallbackQuiz(topic: string, difficulty: string) {
  const baseSummary = `This is a placeholder summary for ${topic}. The AI summary could not be generated. It covers key ideas appropriate to ${difficulty} level.`;
  const map: Record<string, string> = { easy: 'basic', medium: 'intermediate', hard: 'advanced' };
  const questions = Array.from({ length: 5 }).map((_, i) => ({
    question: `(${map[difficulty]} Q${i + 1}) Sample question about ${topic} concept ${i + 1}?`,
    options: ['Option A', 'Option B', 'Option C', 'Option D'],
    correctAnswer: 'Option A'
  }));
  return { summary: baseSummary, questions };
}

app.use(cors());
app.use(express.json());

const generatePrompt = (topic: string, difficulty: string) => `Return ONLY valid JSON: {"summary":"100-150 word summary","questions":[{"question":"","options":["A","B","C","D"],"correctAnswer":"one option"}]}. Topic: ${topic}. Difficulty: ${difficulty}. Exactly 5 MCQs.`;

function extractJson(raw: string) {
  const cleaned = raw.replace(/```json/gi, '').replace(/```/g, '').trim();
  try { return JSON.parse(cleaned); } catch {}
  const first = cleaned.indexOf('{');
  const last = cleaned.lastIndexOf('}');
  if (first !== -1 && last !== -1) {
    try { return JSON.parse(cleaned.slice(first, last + 1)); } catch {}
  }
  return null;
}

app.post('/api/generate-summary', async (req, res) => {
  try {
    const { topic, difficulty } = req.body;
    if (!topic || !difficulty) return res.status(400).json({ error: 'Topic and difficulty are required' });
    const cacheKey = `${topic.toLowerCase()}|${difficulty}`;

    // Rate limit check
    if (!checkRateLimit()) {
      const fb = generateFallbackQuiz(topic, difficulty);
      return res.status(429).json({ topic, difficulty, summary: fb.summary, questions: fb.questions, fallbackUsed: true, reason: 'rate_limit_local', retryAfterMs: rateBucket.resetAt - Date.now() });
    }

    // Serve from cache if available
    if (quizCache.has(cacheKey)) {
      return res.json({ ...quizCache.get(cacheKey), cached: true });
    }

    const prompt = generatePrompt(topic, difficulty);
    const aiText = await safeGenerate(prompt);
    if (!aiText) {
      const fb = generateFallbackQuiz(topic, difficulty);
      const response = { topic, difficulty, summary: fb.summary, questions: fb.questions, fallbackUsed: true, reason: 'generation_failed' };
      quizCache.set(cacheKey, response);
      return res.json(response);
    }

    const parsed = extractJson(aiText);
    if (!parsed || !parsed.summary || !Array.isArray(parsed.questions) || parsed.questions.length !== 5) {
      const fb = generateFallbackQuiz(topic, difficulty);
      const response = { topic, difficulty, summary: fb.summary, questions: fb.questions, fallbackUsed: true, reason: 'parse_error' };
      quizCache.set(cacheKey, response);
      return res.json(response);
    }
    const valid = parsed.questions.every((q: any) => q && typeof q.question === 'string' && Array.isArray(q.options) && q.options.length === 4 && typeof q.correctAnswer === 'string' && q.options.includes(q.correctAnswer));
    if (!valid) {
      const fb = generateFallbackQuiz(topic, difficulty);
      const response = { topic, difficulty, summary: fb.summary, questions: fb.questions, fallbackUsed: true, reason: 'validation_error' };
      quizCache.set(cacheKey, response);
      return res.json(response);
    }
    const finalResponse = { topic, difficulty, summary: parsed.summary, questions: parsed.questions, fallbackUsed: false };
    quizCache.set(cacheKey, finalResponse);
    return res.json(finalResponse);
  } catch (err) {
    console.error('[UNEXPECTED ERROR]', err);
    const fb = generateFallbackQuiz(req.body.topic || 'topic', req.body.difficulty || 'medium');
    return res.status(200).json({ topic: req.body.topic, difficulty: req.body.difficulty, summary: fb.summary, questions: fb.questions, fallbackUsed: true, reason: 'unexpected' });
  }
});

app.post('/api/submit-quiz', (req, res) => {
  try {
    const submission: QuizSubmission = req.body;
    const { answers, questions } = submission;
    const correctCount = answers.filter((a, i) => a === questions[i].correctAnswer).length;
    const score = (correctCount / questions.length) * 100;
    let feedback = '';
    let suggestedTopics: string[] = [];
    if (score >= 80) feedback = "Excellent work! You've mastered this topic!"; else if (score >= 50) { feedback = 'Good effort! Some revision recommended.'; suggestedTopics = ['Review incorrect concepts']; } else { feedback = 'Keep practicing the fundamentals.'; suggestedTopics = ['Start with easier examples', 'Revisit core definitions']; }
    const report: ReadinessReport = { score, feedback, suggestedTopics };
    res.json(report);
  } catch (e) {
    console.error('Error submitting quiz:', e);
    res.status(500).json({ error: 'Failed to process quiz submission' });
  }
});

app.listen(port, () => console.log(`Server running on port ${port}`));