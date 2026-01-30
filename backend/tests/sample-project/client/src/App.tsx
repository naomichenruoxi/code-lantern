import { useState } from 'react'
import './App.css'

interface Quiz {
  topic: string;
  difficulty: string;
  summary: string;
  questions: QuizQuestion[];
  fallbackUsed?: boolean;
}

interface QuizQuestion {
  question: string;
  options: string[];
  correctAnswer: string;
}

interface ReadinessReport {
  score: number;
  feedback: string;
  suggestedTopics?: string[];
}

function App() {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [report, setReport] = useState<ReadinessReport | null>(null);

  const generateQuiz = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/generate-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, difficulty }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate quiz. Please try again.');
      }
      
      const data = await response.json();
      if (!data.summary || !data.questions) {
        throw new Error('Invalid response from server. Please try again.');
      }
      
      setQuiz(data);
    } catch (error) {
      console.error('Error generating quiz:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const submitQuiz = async () => {
    setError(null);
    try {
      const response = await fetch('/api/submit-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          topic,
          difficulty,
          answers,
          questions: quiz?.questions
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit quiz. Please try again.');
      }
      
      const report = await response.json();
      setReport(report);
    } catch (error) {
      console.error('Error submitting quiz:', error);
      setError(error instanceof Error ? error.message : 'Failed to submit quiz. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          {error && (
            <div className="mb-4 p-4 text-red-700 bg-red-100 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          {!quiz ? (
            <div className="max-w-md mx-auto">
              <div className="divide-y divide-gray-200">
                <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                  <h2 className="text-2xl font-bold mb-8">Math Topic Quiz Generator</h2>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700">Topic</label>
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      placeholder="e.g., quadratic equations"
                    />
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700">Difficulty</label>
                    <select
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>
                  <button
                    onClick={generateQuiz}
                    disabled={loading || !topic}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400"
                  >
                    {loading ? (
                      <div className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Generating...
                      </div>
                    ) : 'Generate Quiz'}
                  </button>
                </div>
              </div>
            </div>
          ) : report ? (
            <div className="max-w-md mx-auto">
              <h2 className="text-2xl font-bold mb-4">Readiness Report</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-lg mb-2">Score: {report.score}%</p>
                <p className="text-gray-700 mb-4">{report.feedback}</p>
                {report.suggestedTopics && (
                  <div>
                    <h3 className="font-semibold mb-2">Suggested Topics to Review:</h3>
                    <ul className="list-disc pl-5">
                      {report.suggestedTopics.map((topic, index) => (
                        <li key={index}>{topic}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <button
                  onClick={() => {
                    setQuiz(null);
                    setReport(null);
                    setAnswers([]);
                  }}
                  className="mt-4 w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Start New Quiz
                </button>
              </div>
            </div>
          ) : (
            <div className="max-w-md mx-auto">
              <div className="mb-6">
                <div className="flex items-start justify-between">
                  <h2 className="text-2xl font-bold mb-2">{quiz.topic}</h2>
                  {quiz.fallbackUsed && (
                    <span className="ml-2 inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-300" title="AI response failed; using generated placeholder">Fallback</span>
                  )}
                </div>
                <p className="text-gray-600 text-sm leading-relaxed">{quiz.summary}</p>
              </div>
              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs font-medium text-gray-600 mb-1">
                  <span>Question {currentQuestionIndex + 1} / {quiz.questions.length}</span>
                  <span>{Math.round(((currentQuestionIndex + 1) / quiz.questions.length) * 100)}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded">
                  <div
                    className="h-2 bg-indigo-500 rounded transition-all"
                    style={{ width: `${((currentQuestionIndex + 1) / quiz.questions.length) * 100}%` }}
                  />
                </div>
              </div>
              {/* Question */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">{quiz.questions[currentQuestionIndex].question}</h3>
                <div className="space-y-2">
                  {quiz.questions[currentQuestionIndex].options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        const newAnswers = [...answers];
                        newAnswers[currentQuestionIndex] = option;
                        setAnswers(newAnswers);
                        if (currentQuestionIndex < quiz.questions.length - 1) {
                          setCurrentQuestionIndex(currentQuestionIndex + 1);
                        }
                      }}
                      className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-colors ${
                        answers[currentQuestionIndex] === option
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-300 hover:border-indigo-300'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
              {currentQuestionIndex === quiz.questions.length - 1 && (
                <button
                  onClick={submitQuiz}
                  disabled={answers.length !== quiz.questions.length}
                  className="w-full py-3 px-4 rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-400"
                >
                  Submit Quiz
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
