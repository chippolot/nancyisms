// api/toggle-reaction.js
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_API_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

    // Handle OPTIONS request (for CORS)
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    // Check if the request method is POST
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    // Get request body
    const { quote_id, emoji, add } = req.body;

    if (!quote_id || !emoji) {
        return res.status(400).json({ error: 'quote_id and emoji are required' });
    }

    try {
        // First, check if the reaction exists
        const { data: existingReaction, error: fetchError } = await supabase
            .from('reactions')
            .select('count')
            .eq('quote_id', quote_id)
            .eq('emoji', emoji)
            .single();

        if (fetchError && fetchError.code !== 'PGRST116') { // PGRST116 is "not found" which is expected
            throw fetchError;
        }

        if (existingReaction) {
            // Reaction exists, update count
            const newCount = add ? existingReaction.count + 1 : Math.max(0, existingReaction.count - 1);

            const { data, error } = await supabase
                .from('reactions')
                .update({ count: newCount })
                .eq('quote_id', quote_id)
                .eq('emoji', emoji);

            if (error) throw error;

            res.status(200).json({ emoji, count: newCount });
        } else {
            // Reaction doesn't exist, create it
            // Only create if adding (not removing)
            if (add) {
                const { data, error } = await supabase
                    .from('reactions')
                    .insert([
                        { quote_id, emoji, count: 1 }
                    ]);

                if (error) throw error;

                res.status(200).json({ emoji, count: 1 });
            } else {
                // Trying to remove a reaction that doesn't exist, just return 0
                res.status(200).json({ emoji, count: 0 });
            }
        }
    } catch (error) {
        console.error('Error toggling reaction:', error);
        res.status(500).json({ error: 'Failed to toggle reaction' });
    }
}