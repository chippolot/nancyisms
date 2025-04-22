// api/random-quote.js
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_API_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  // Handle OPTIONS request (for CORS)
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    // Query to get a random quote from the database
    // Using the COUNT and LIMIT approach which works well in most SQL databases
    const { data: totalCount } = await supabase
      .from('quotes')
      .select('count', { count: 'exact' });

    // Get a random row number
    const count = totalCount[0].count;
    const randomIndex = Math.floor(Math.random() * count);

    // Fetch the random quote
    const { data, error } = await supabase
      .from('quotes')
      .select('*')
      .range(randomIndex, randomIndex);

    if (error) {
      throw error;
    }

    // Return the quote as JSON
    res.status(200).json(data[0]);
  } catch (error) {
    console.error('Error fetching random quote:', error);
    res.status(500).json({ error: 'Failed to fetch a random quote' });
  }
}