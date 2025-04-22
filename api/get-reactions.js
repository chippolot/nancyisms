// api/get-reactions.js
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

    // Check if the request method is GET
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    // Get quote_id from query params
    const { quote_id } = req.query;

    if (!quote_id) {
        return res.status(400).json({ error: 'quote_id is required' });
    }

    try {
        // Get all reactions for this quote
        const { data, error } = await supabase
            .from('reactions')
            .select('emoji, count')
            .eq('quote_id', quote_id);

        if (error) {
            throw error;
        }

        // Transform data into a more usable format
        const reactionCounts = {};
        const emojis = ['😂', '❤️', '👍', '🙏', '💯'];

        // Initialize all emojis with 0 count
        emojis.forEach(emoji => {
            reactionCounts[emoji] = 0;
        });

        // Update with actual counts
        data.forEach(reaction => {
            reactionCounts[reaction.emoji] = reaction.count;
        });

        res.status(200).json(reactionCounts);
    } catch (error) {
        console.error('Error fetching reactions:', error);
        res.status(500).json({ error: 'Failed to fetch reactions' });
    }
}