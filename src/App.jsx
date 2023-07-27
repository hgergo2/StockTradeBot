import React from "react";
import { Typography } from '@mui/material';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import CssBaseline from '@mui/material/CssBaseline';
import Plot from 'react-plotly.js';
import { useState, useEffect } from 'react';
//import Stack from '@mui/material/Stack';

const App = () => {
    //var fetch_data = Fetch_chart();
    //var fetch_data = fetch('http://127.0.0.1:5000/strategy/NVDA/200ema/')
    //.then(response => {
    //  if (!response.ok) {
    //    throw new Error('Network response was not ok');
    //  }
    //  return response.json();
    //})
    //.catch(error => {
    //  console.error('Errorrrrr:', error);
    //});
    //console.log(fetch_data);
    const [chartData, setChartData] = useState(null);
    useEffect(() => {
        fetch('http://127.0.0.1:5000/strategy/NVDA/200ema/')
            .then(res => {
                return res.json();
            })
            .then(data => {
                console.log(data);
                setChartData(data)
            })
    }, [])

    return(
        
        <div>
            <Button variant="contained">Ingyen gyros gomb</Button>

            <React.Fragment>
                <CssBaseline />
                <Container maxWidth="100vh">
                    {/*<Box sx={{ bgcolor: '#cfe8fc', height: '90vh' }} />*/}
                    
                    
                    {chartData && <Plot data={[
                        {
                            type: "candlestick",
                            x: chartData["data"][0]["x"],
                            open: chartData["data"][0]["open"],
                            high: chartData["data"][0]["high"],
                            low: chartData["data"][0]["low"],
                            close: chartData["data"][0]["close"],
                            hovertext: chartData["data"][0]["hovertext"]
                        }
                    ]}
                    layout={{width: 1800, height: 880, xaxis : {fixedrange: true, rangeslider: {visible: false}}, shapes: chartData["layout"]["shapes"]}}
                    config={{scrollZoom: false}}/>}
                </Container>
            </React.Fragment>

        </div>
        
    );
}

async function Fetch_chart() {
    const response = await fetch("http://127.0.0.1:5000/strategy/NVDA/200ema/");
    const r = await response.json();
    console.log(r);
    return r;
  }

export default App;
