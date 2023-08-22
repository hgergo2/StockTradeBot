import React from "react";
import Container from '@mui/material/Container';
import CssBaseline from '@mui/material/CssBaseline';
import Plot from 'react-plotly.js';
import { useState, useEffect, Component } from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import Grid from '@mui/material/Unstable_Grid2';
import { DataGrid } from '@mui/x-data-grid';
import Button from '@mui/material/Button';

import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';
import MenuIcon from '@mui/icons-material/Menu';


const symbolList = [
    {label: 'NVDA', symbol: 'NVDA', id: 1},
    {label: 'TSLA ', symbol: 'TSLA', id: 2},
    {label: 'TQQQ ', symbol: 'TQQQ', id: 3},
    {label: '(NEM JO) AMZN ', symbol: 'AMZN', id: 4},
    {label: 'AMD ', symbol: 'AMD', id: 5},
    {label: 'INTC ', symbol: 'INTC', id: 6},
    {label: 'AMC ', symbol: 'AMC', id: 7},
    {label: 'SHOP ', symbol: 'SHOP', id: 8},
    {label: 'ENVX ', symbol: 'ENVX', id: 9},
    {label: 'GOOG ', symbol: 'GOOG', id: 10},
];

const strategyList = [
    {label: '200 ema', id: 1, strategy: '200ema_strategy'},
    {label: 'random', id: 2, strategy: 'random_strategy'}
];

var current = symbolList[0];
var current_strategy = strategyList[0];
var apiAddress = 'http://127.0.0.1:5000';


const App = () => {

    //const chartData = Fetch_chart('NVDA', '200ema');
    //console.log(chartData);
    return(

        <div>
            
            
            <React.Fragment>
                <CssBaseline />
                <Container maxWidth="100vh">
                


                    {/*<Get_chart symbol={value['label']} strat_name={'200ema'}/>*/}
                    <Grid container spacing={1}>

                        <Grid xs={0.5}>
                            <TemporaryDrawer />
                        </Grid>

                        <Grid xs={2}>
                            <>
                            <Autocomplete
                            disablePortal
                            id="symbol-selector"
                            options={symbolList}
                            sx={{ width: 300 }}
                            onChange={(event, v) =>  {
                                current = v;
                            }}
                            renderInput={(params) => <TextField {...params} label={current['label']} />}
                            />
                        </>
                        </Grid>

                        <Grid xs={2}>
                            <>
                                <Autocomplete
                                disablePortal
                                id="strategy-selector"
                                options={strategyList}
                                sx={{ width: 300 }}
                                onChange={(event, v) =>  {
                                    current_strategy = v;
                                }}
                                renderInput={(params) => <TextField {...params} label={current_strategy['label']} />}
                                />
                            </>
                        </Grid>

                        <Grid xs={12}>
                            <Get_chart />
                        </Grid>
                    </Grid>
                    <GetPositions />
                </Container>
            </React.Fragment>
        </div>
        
    );
    
}


const delay = ms => new Promise(res => setTimeout(res, ms));
// http://127.0.0.1:5000/positions/?symbol=NVDA&strat_name=all&active=true
function GetPositions(){

    //console.log('Symbol: ' + current['symbol'] + ' Strategy: ' + current_strategy['strategy']);
    const [position, setPosition] = useState(null);
    const refreshPositions = async () => {
        await delay(3000);
        try{
            const positions_fetch = await (await fetch(apiAddress + '/positions/?symbol='+ current['symbol'] +'&strat_name=' + current_strategy['strategy'])).json()
            setPosition(positions_fetch)
            //console.log(position);
            
        } catch (err){
            //console.log(err.message)
        }
        
    }
    
    refreshPositions();

    const columns = [
        {field: 'id', headerName: 'ID', width: 70},
        {field: 'symbol', headerName: 'Symbol', width: 100},
        {field: 'order_type', headerName: 'Order Type'},
        {field: 'is_active', headerName: 'Active', type: 'boolean'},
        {field: 'entry_price', headerName: 'Entry Price', width: 200},
        {field: 'entry_date', headerName: 'Entry Date', width: 200, type: 'Date'},
        {field: 'target_price', headerName: 'Target Price', width: 200},
        {field: 'stop_loss', headerName: 'Stop Loss', width: 200},
        {field: 'sell_price', headerName: 'Sell Price', width: 200},
        {field: 'sell_date', headerName: 'Sell Date', width: 200},
        {field: 'profit', headerName: 'P&L (%)', width: 100}
    ];

    const rows = [

    ];

    if(position != null && position.length > 0){
        for (let i = 0; i < position.length; i++){
            rows.push({id: position[i]['_id'],
                       order_type: position[i]['order_type'],
                       is_active: position[i]['is_active'],
                       entry_price: position[i]['entry_price'],
                       entry_date: position[i]['entry_date'],
                       target_price: position[i]['target_price'],
                       stop_loss: position[i]['stop_loss'],
                       symbol: position[i]['symbol'],
                       sell_price: position[i]['sell_price'],
                       sell_date: position[i]['sell_date'],
                       profit: position[i]['pnl']});
        }
    }


    return(
        <div style={{ height: 400, width: '100%' }}>
            <DataGrid
              rows={rows}
              columns={columns}
              initialState={{
                pagination: {
                  paginationModel: { page: 0, pageSize: 10 },
                },
                sorting:{
                    sortModel: [{field: 'is_active', sort: 'desc'}, {field: 'entry_date', sort: 'asc'}]
                }
              }}

              sx={{'& .over': {
                color: '#39911c'
              },
              '& .under':{
                color: '#eb442a'
              }}}
  
              getCellClassName={(params) => {
                if (params.field === 'profit'){
                  return params.value > 0 ? 'over' : 'under';
                }
              }}

              pageSizeOptions={[10, 20]}
              //checkboxSelection
            />
    </div>
    )

}


function Get_chart(){
    
    const [data, setData] = useState(null);
    const refreshChart = async () => {
        await delay(1000);
        try {
            const data = await (await fetch(apiAddress + '/strategy/'+ current['symbol'] +'/'+ current_strategy['strategy'] +'/')).json()
            setData(data)
            //console.log(data);
            
        } catch (err) {
            //console.log(err.message)
        }
    }
    
    refreshChart();
    
    return(
        <div>
            {data && <Plot data={data["data"]} layout={data["layout"]}/>}
        </div>
    );
}

function TemporaryDrawer() {
    const [state, setState] = React.useState({
      left: false,
    });
  
    const toggleDrawer = (anchor, open) => (event) => {
      if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
        return;
      }
  
      setState({ ...state, [anchor]: open });
    };
  
    const list = (anchor) => (
      <Box
        sx={{ width: anchor === 'top' || anchor === 'bottom' ? 'auto' : 250 }}
        role="presentation"
        onClick={toggleDrawer(anchor, false)}
        onKeyDown={toggleDrawer(anchor, false)}
      >
        <List>
        <ListItem key={'Chart'} disablePadding>
              <ListItemButton onClick={toggleDrawer('left', false)}>
                <ListItemText primary={'Chart'} />
              </ListItemButton>
        </ListItem>
        <ListItem key={'Statistics'} disablePadding>
              <ListItemButton href='/statistics'>
                <ListItemText primary={'Statistics'} />
              </ListItemButton>
            </ListItem>
        </List>
      </Box>
    );
  
    return (
      <div>
          <React.Fragment key={'left'}>
            <Button startIcon={<MenuIcon />} size="large" onClick={toggleDrawer('left', true)}></Button>
            <Drawer
              anchor={'left'}
              open={state['left']}
              onClose={toggleDrawer('left', false)}
            >
              {list('left')}
            </Drawer>
          </React.Fragment>
        
      </div>
    );
  }


export default App;
