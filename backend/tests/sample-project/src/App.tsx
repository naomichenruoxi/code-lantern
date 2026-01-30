// ...existing code...
const generateQuiz = async () => {
  try {
    setLoading(true);
    const response = await fetch('http://localhost:5173/api/generate-summary', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: inputText }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    if (!data) {
      throw new Error('No data received from the API');
    }

    setQuiz(data);
  } catch (error) {
    console.error('Error generating quiz:', error);
    setError(error instanceof Error ? error.message : 'An unexpected error occurred');
  } finally {
    setLoading(false);
  }
};
// ...existing code...
