import React, { useState, useEffect } from 'react';

const API_ROOT = 'http://localhost:8000';

function App() {
    const [endpoints, setEndpoints] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchEndpoints = async () => {
        try {
            const resp = await fetch(`${API_ROOT}/endpoints`);
            const data = await resp.json();
            setEndpoints(data);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch:', err);
        }
    };

    useEffect(() => {
        fetchEndpoints();
        const interval = setInterval(fetchEndpoints, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="dashboard">
            <header>
                <h1>API RADAR</h1>
                <div className="status-badge">Phase 2: Shadow Detection</div>
            </header>

            {loading ? (
                <div style={{ textAlign: 'center' }}>Initializing Radar...</div>
            ) : (
                <div className="radar-grid">
                    {endpoints.length === 0 ? (
                        <div className="api-card">No endpoints discovered yet.</div>
                    ) : (
                        endpoints.map((api, idx) => (
                            <div key={idx} className={`api-card ${api.is_shadow ? 'is-shadow' : ''}`}>
                                <div>
                                    <span className={`method ${api.method}`}>{api.method}</span>
                                    <span className="endpoint">{api.endpoint}</span>
                                    {api.is_shadow ? (
                                        <span className="shadow-badge">Shadow Alert</span>
                                    ) : (
                                        <span className="documented-badge">Documented</span>
                                    )}
                                </div>
                                <div className="stats">
                                    <span className="count-label">Discovery Count</span>
                                    <span className="count-value">{api.count}</span>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}

export default App;
