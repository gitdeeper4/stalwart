exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    // Sample bridge data (would connect to real database)
    const bridges = [
      { id: 'BR-001', name: 'Golden Gate Bridge', location: 'San Francisco, CA', health: 94 },
      { id: 'BR-002', name: 'Brooklyn Bridge', location: 'New York, NY', health: 78 },
      { id: 'BR-003', name: 'Tower Bridge', location: 'London, UK', health: 88 },
      { id: 'BR-004', name: 'Akashi Kaikyō Bridge', location: 'Kobe, Japan', health: 97 },
      { id: 'BR-005', name: 'Sydney Harbour Bridge', location: 'Sydney, Australia', health: 92 }
    ];

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: bridges,
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
