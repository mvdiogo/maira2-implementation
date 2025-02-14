import { useState, useEffect } from 'react';
import './App.css';
import Cookies from 'js-cookie';

function App() {
    const [frontalUrl, setFrontalUrl] = useState('');
    const [lateralUrl, setLateralUrl] = useState('');
    const [indication, setIndication] = useState('');
    const [comparison, setComparison] = useState('');
    const [technique, setTechnique] = useState('');
    const [frontalImage, setFrontalImage] = useState(null);
    const [lateralImage, setLateralImage] = useState(null);
    const [report, setReport] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showWarning, setShowWarning] = useState(false);
    const [darkMode, setDarkMode] = useState(() => {
        const cookieValue = Cookies.get('darkMode');
        return cookieValue === 'true';
    });
    const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT;

    useEffect(() => {
        Cookies.set('darkMode', darkMode.toString(), { sameSite: 'Lax' });
    }, [darkMode]);


    const handleSubmit = async (e) => {
        e.preventDefault();

        setShowWarning(true);
        document.body.style.cursor = 'wait';

        let isMounted = true;

        setLoading(true);
        setError('');
        setFrontalImage(null);
        setLateralImage(null);

        try {
            const formData = new FormData();
            formData.append('frontal_url', frontalUrl);
            formData.append('lateral_url', lateralUrl);
            formData.append('indication', indication);
            formData.append('comparison', comparison);
            formData.append('technique', technique);

            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                mode: 'cors',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            const processImage = (base64Data) => {
                if (!base64Data) return null;
                return base64Data.startsWith('data:image')
                    ? base64Data
                    : `data:image/jpeg;base64,${base64Data}`;
            };

            const frontal = processImage(data.frontal_image);
            const lateral = processImage(data.lateral_image);

            if (!frontal || !lateral) {
                throw new Error('Invalid image data received from server');
            }

            if (isMounted) {
                setFrontalImage(frontal);
                setLateralImage(lateral);
                setReport(data.report);
            }

        } catch (error) {
            console.error('Error:', error);
            if (isMounted) {
                setError(`Error: ${error.message}`);
                setReport('');
            }
        } finally {
            if (isMounted) {
                setLoading(false);
                setShowWarning(false);
                document.body.style.cursor = 'default';
            }
        }
    };


    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
    };

    return (
        <div className={darkMode ? 'container dark' : 'container'}>
            <div className="slider-container">
                <label htmlFor="darkModeSlider"></label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="1"
                    value={darkMode ? 1 : 0}
                    onChange={toggleDarkMode}
                    className="slider"
                />
            </div>

            <h1 className="title">MAIRA-2 CXR Report Generator v2</h1>

            <form className="form" onSubmit={handleSubmit}>
                <div className="input-row">
                    <div className="input-wrapper">
                        <label className="label" htmlFor="frontalUrl">Frontal Image URL:</label>
                        <input
                            className="input"
                            type="url"
                            id="frontalUrl"
                            value={frontalUrl}
                            onChange={(e) => setFrontalUrl(e.target.value)}
                            required
                            placeholder="https://example.com/frontal.jpg"
                        />
                    </div>
                    <div className="input-wrapper">
                        <label className="label" htmlFor="lateralUrl">Lateral Image URL:</label>
                        <input
                            className="input"
                            type="url"
                            id="lateralUrl"
                            value={lateralUrl}
                            onChange={(e) => setLateralUrl(e.target.value)}
                            required
                            placeholder="https://example.com/lateral.jpg"
                        />
                    </div>
                </div>
                <div className="input-row">
                    <div className="input-wrapper">
                        <label className="label" htmlFor="indication">Indication:</label>
                        <input
                            className="input"
                            type="text"
                            id="indication"
                            value={indication}
                            onChange={(e) => setIndication(e.target.value)}
                            placeholder="e.g., Cough, shortness of breath"
                        />
                    </div>
                    <div className="input-wrapper">
                        <label className="label" htmlFor="comparison">Comparison:</label>
                        <input
                            className="input"
                            type="text"
                            id="comparison"
                            value={comparison}
                            onChange={(e) => setComparison(e.target.value)}
                            placeholder="e.g., Prior CXR from 2022-01-15"
                        />
                    </div>
                </div>
                <label className="label" htmlFor="technique">Technique:</label>
                <input
                    className="input"
                    type="text"
                    id="technique"
                    value={technique}
                    onChange={(e) => setTechnique(e.target.value)}
                    placeholder="e.g., PA and Lateral"
                />

                <button className="button" type="submit" disabled={loading}>
                    {loading ? 'Generating...' : 'Generate Findings'}
                </button>
            </form>

            {showWarning && (
                <div className="warning-message">
                    Generating the report may take more than 20 minutes. Please be patient.
                </div>
            )}

            {error && <div className="error-message">{error}</div>}

            <div className="image-container">
                <div className="image-wrapper">
                    <h3>Frontal Image</h3>
                    {frontalImage ? (
                        <img
                            className="image"
                            src={frontalImage}
                            alt="Frontal"
                            onError={(e) => {
                                e.target.style.display = 'none';
                                setError('Failed to load frontal image');
                            }}
                        />
                    ) : (
                        <p>No frontal image available.</p>
                    )}
                </div>
                <div className="image-wrapper">
                    <h3>Lateral Image</h3>
                    {lateralImage ? (
                        <img
                            className="image"
                            src={lateralImage}
                            alt="Lateral"
                            onError={(e) => {
                                e.target.style.display = 'none';
                                setError('Failed to load lateral image');
                            }}
                        />
                    ) : (
                        <p>No lateral image available.</p>
                    )}
                </div>
            </div>

            <div className="report-container">
                <h3>Generated Findings Report</h3>
                <textarea className="textarea" value={report} readOnly />
            </div>
        </div>
    );
}

export default App;