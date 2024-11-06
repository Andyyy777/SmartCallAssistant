import React, { useState, useEffect } from 'react';
import { Button, Grid, Typography } from '@mui/material';
import DisplayArea from '../components/DisplayArea';

const MainScreen = () => {
    const [recordingStatus, setRecordingStatus] = useState(false);
    const [isStart, setIsStart] = useState(true);
    const [path, setPath] = useState('');
    const [timer, setTimer] = useState(0);
    const [intervalId, setIntervalId] = useState<number | NodeJS.Timeout | undefined>(undefined);
    const [displayText, setDisplayText] = useState('')

    const startTimer = () => {
        const id = setInterval(() => {
            setTimer(prevTimer => prevTimer + 1);
        }, 1000);
        setIntervalId(id);
    };

    const stopTimer = () => {
        clearInterval(intervalId);
        setIntervalId(undefined);
    };

    const toggleRecording = () => {
        if (isStart && !recordingStatus) {
            // Start recording
            fetch("http://localhost:5000/audio/start", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                response.json();
                console.log(response);
            })
            .then(data => {
                setRecordingStatus(true);
                setIsStart(false);
                startTimer();
            })
            .catch(error => {
                console.error("Error:", error);
                setRecordingStatus(false);
                setIsStart(true);
            });
        } else if (!isStart && recordingStatus) {
            // Pause recording
            fetch("http://localhost:5000/audio/pause", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                setRecordingStatus(false);
                stopTimer();
            })
            .catch(error => {
                console.error("Error:", error);
                setRecordingStatus(false);
            });
        } else if (!isStart && !recordingStatus) {
            // Resume recording
            fetch("http://localhost:5000/audio/resume", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                setRecordingStatus(true);
                startTimer();
            })
            .catch(error => {
                console.error("Error:", error);
                setRecordingStatus(false);
            });
        }
    };

    const stopRecording = () => {
        fetch("http://localhost:5000/audio/stop", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            setPath(data.path);
            setRecordingStatus(false);
            setIsStart(true);
            stopTimer();
            setTimer(0);

            fetch("http://localhost:5000/ai/process", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ path: data.path }) 
            })
            .then(response => response.json())
            .then(data => {
                console.log("Server response:", data);
                setDisplayText(data.data);
            })
            .catch(error => {
                console.error("Error about AI:", error);
            });
        })
        .catch(error => {
            console.error("Error:", error);
            setRecordingStatus(false);
            setIsStart(true);
            stopTimer();
            setTimer(0);
        });
    };

    // Clean up interval on component unmount
    useEffect(() => {
        return () => clearInterval(intervalId);
    }, [intervalId]);

    return (
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <Grid container spacing={2} justifyContent="center" alignItems="center">
                {/* Start/Pause/Resume Button */}
                <Grid item>
                    <Button variant="contained" color="primary" onClick={toggleRecording}>
                        {isStart ? "Start" : recordingStatus ? "Pause" : "Resume"}
                    </Button>
                </Grid>
        
                <Grid item>
                    <Typography variant="h6">
                        {new Date(timer * 1000).toISOString().substr(11, 8)} 
                    </Typography>
                </Grid>
        
                <Grid item>
                    <Button variant="contained" color="secondary" onClick={stopRecording}>
                        Stop
                    </Button>
                </Grid>
            </Grid>
    
            <Typography variant="body1" style={{ marginTop: '10px', visibility: isStart&&!recordingStatus&&timer==0? "visible" : "hidden"}}>
                {path}
            </Typography>
            <DisplayArea text={displayText} visibility={isStart&&!recordingStatus&&timer==0} />
        </div>
    );
}

export default MainScreen;
