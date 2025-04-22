async function fetchQuotes() {
    const response = await fetch('/api/getQuotes');
    const quotes = await response.json();
    return quotes;
  }
  
  // Sample code to update reaction counts
  async function updateReaction(quoteId, emojiType) {
    const response = await fetch('/api/incrementReaction', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ quoteId, emojiType }),
    });
    return await response.json();
  }