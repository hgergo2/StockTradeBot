import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import MenuIcon from '@mui/icons-material/Menu';
import Grid from '@mui/material/Unstable_Grid2';
import { DataGrid } from '@mui/x-data-grid';
import { useState, useEffect, Component } from 'react';
import Paper from '@mui/material/Paper';
import { createTheme, ThemeProvider, styled } from '@mui/material/styles';

import { DateRangePicker } from '@mui/x-date-pickers-pro/DateRangePicker';
import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { LocalizationProvider, SingleInputDateRangeField } from '@mui/x-date-pickers-pro';
import { AdapterDayjs } from '@mui/x-date-pickers-pro/AdapterDayjs';
import dayjs from 'dayjs';
import Plot from 'react-plotly.js';

function Statistics(){
    return(
    <div>
        <TemporaryDrawer />  
        <GetPositions />
        <DatePicker />
        <Stats />

    </div>
    );
}

const delay = ms => new Promise(res => setTimeout(res, ms));
var apiAddress = 'http://127.0.0.1:5000';

function GetPositions(){

  //console.log('Symbol: ' + current['symbol'] + ' Strategy: ' + current_strategy['strategy']);
  const [position, setPosition] = useState(null);
  const refreshPositions = async () => {
      await delay(3000);
      try{
          const positions_fetch = await (await fetch(apiAddress + '/positions/')).json()
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
      {field: 'profit', headerName: 'P&L (%)', width: 100},
      {field: 'strategy_name', headerName: 'Strategy'}
  ];

  const rows = [];

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
                     profit: position[i]['pnl'],
                     strategy_name: position[i]['strategy_name']});
      }
  }


  return(
      <div style={{ height: 800, width: '100%' }}>
          <DataGrid
            rows={rows}
            columns={columns}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 20 },
              },
              sorting:{
                  sortModel: [{field: 'is_active', sort: 'desc'}]
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

            pageSizeOptions={[20, 40]}
            //checkboxSelection
          />
  </div>
  )

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
            <ListItemButton href='/'>
              <ListItemText primary={'Chart'} />
            </ListItemButton>
          </ListItem>

          <ListItem key={'Statistics'} disablePadding>
            <ListItemButton onClick={toggleDrawer('left', false)}>
              <ListItemText primary={'Statistics'} />
            </ListItemButton>
          </ListItem>
      </List>
    </Box>
  );

  return (
    <div>
        <React.Fragment key={'left'}>
          <Button startIcon={<MenuIcon />} size='large' onClick={toggleDrawer('left', true)}></Button>
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

var dateStats = [dayjs('2023-08-16'), dayjs()];


const Item = styled(Paper)(({ theme }) => ({
  ...theme.typography.body2,
  textAlign: 'center',
  color: theme.palette.text.secondary,
  height: 120,
  lineHeight: '60px',
}));

const darkTheme = createTheme({ palette: { mode: 'dark' } });
const lightTheme = createTheme({ palette: { mode: 'light' } });
const elevation = 3;

function Stats(){

  const [stats, setStats] = useState({});
    const refreshStats = async () => {
        await delay(3000);
        try{
            if(dateStats[0] != null && dateStats[1] != null){
              const stats_fetch = await (await fetch(apiAddress + '/statistics/?start=' + dateStats[0].format('YYYY-MM-DD') + '&end=' + dateStats[1].format('YYYY-MM-DD'))).json()
              setStats(stats_fetch)
            }
            //console.log(stats);
            
        } catch (err){
            //console.log(err.message)
        }
        
    }
    
    refreshStats();


  return(
    <div>
      <Grid container spacing={1}>
        <Grid item xs={12} key={0}>
          <ThemeProvider theme={lightTheme}>
            <Box
              sx={{
                p: 2,
                bgcolor: 'background.default',
                display: 'grid',
                gridTemplateColumns: { md: '1fr 1fr 1fr 1fr' },
                gap: 2,
              }}
            >
              
            <Item key={'wins'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>Wins{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>{stats['wins']}</h1>
            </Item>
            <Item key={'losses'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>Losses{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>{stats['losses']}</h1>
            </Item>
            <Item key={'winrate'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>Winrate{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>{stats['winrate']}%</h1>
            </Item>
            <Item key={'profit'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>Realised P&L{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>{stats['pnl']}%</h1>
            </Item>
            <Item key={'active-trades'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>Active Trades{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>{stats['number_of_active']}</h1>
            </Item>
            <Item key={'active-pnl'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>Unrealised P&L{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>{stats['active_pnl']}%</h1>
            </Item>
            <Item key={'valami1'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>valami{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>1234</h1>
            </Item>
            <Item key={'valami2'} elevation={elevation}>
              <h1 style={ {fontSize: 20, marginTop: 0, marginBottom: -10} }>valami{"\n"}</h1>
              <h1 style={ {fontSize: 35, marginTop: 0} }>1234</h1>
            </Item>
              
            </Box>
          </ThemeProvider>
        </Grid>
      
    </Grid>

      <StatsChart data={stats}/>         

    </div>
  );

}

function StatsChart(data){

  return(
    <div style={ {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
      } }>

        

        <Plot 
          data={[
            {
              x: data['data']['stats_chart_x'],
              y: data['data']['stats_chart_y'],
              type: 'scatter',
              mode: 'lines'
            }
          ]}
          layout={ {height: 700, width: 1200, title: 'P&L Timeline (%)'} }
        />
    </div>
  );

}

function DatePicker(){

  return(
    <div>
    <LocalizationProvider dateAdapter={AdapterDayjs}>
        <DateRangePicker defaultValue={dateStats} onChange={(newValue) => {dateStats=newValue}} slots={{field: SingleInputDateRangeField}} />
    </LocalizationProvider>
    </div>
  );

}



export default Statistics;
