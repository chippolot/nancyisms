// api/getQuotes.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

export default async function handler(req, res) {
  const { data, error } = await supabase
    .from('quotes')
    .select('*')
  
  if (error) {
    return res.status(500).json({ error: error.message })
  }
  
  return res.status(200).json(data)
}