exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    const bridgeId = event.queryStringParameters?.bridgeId || 'all';
    
    // Sample metrics data
    const metrics = {
      'BR-001': {
        afc: 0.42,
        alsa: 0.58,
        cpii: 0.91,
        ffd: 2.3,
        lts: 18.5,
        ccf: 34.2,
        tvr: 0.88,
        bd: 8.4,
        sed: 42.3,
        health: 94
      }
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: bridgeId === 'all' ? metrics : metrics[bridgeId],
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
