// STALWART - Statistics Data
// يستخدم نفس المتغيرات الموجودة من مشروع CAVORA

const { createClient } = require('@supabase/supabase-js');

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Supabase credentials not configured');
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    // Get bridge count
    const { count: totalBridges, error: countError } = await supabase
      .from('bridge_systems')
      .select('*', { count: 'exact', head: true });

    if (countError) throw countError;

    // Get alerts count
    const { count: activeAlerts, error: alertsError } = await supabase
      .from('alerts')
      .select('*', { count: 'exact', head: true })
      .eq('is_active', true);

    if (alertsError) throw alertsError;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: {
          totalBridges: totalBridges || 0,
          activeAlerts: activeAlerts || 0,
          timestamp: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      })
    };
  } catch (error) {
    console.error('❌ Error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
