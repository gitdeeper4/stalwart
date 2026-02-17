exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const alerts = [
      {
        id: 'ALT-001',
        bridgeId: 'BR-002',
        level: 'WARNING',
        message: 'ALSA increasing by 6.4%',
        timestamp: new Date().toISOString()
      },
      {
        id: 'ALT-002',
        bridgeId: 'BR-005',
        level: 'MONITOR',
        message: 'Slight increase in FFD',
        timestamp: new Date().toISOString()
      }
    ];

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: alerts,
        timestamp: new Date().toISOString()
      })
    };
  } catch (error) {
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
