export interface QuizQuestion {
  question: string;
  options: string[];
  correctAnswer: string;
}

export interface Quiz {
  topic: string;
  difficulty: string;
  summary: string;
  questions: QuizQuestion[];
  fallbackUsed?: boolean; // indicates AI fallback was used
}

export interface QuizSubmission {
  topic: string;
  difficulty: string;
  answers: string[];
  questions: QuizQuestion[];
}

export interface ReadinessReport {
  score: number;
  feedback: string;
  suggestedTopics?: string[];
}