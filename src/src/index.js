import React, { useEffect } from 'react';
import { createRoot, ReactDOM } from 'react-dom/client';
import App from './App';
import {
    createBrowserRouter,
    RouterProvider,
    Route
} from 'react-router-dom'
import Statistics from './Statistics';

const router = createBrowserRouter([
    {
        path: '/',
        element: <App />,
    },
    {
        path: 'statistics',
        element: <Statistics />
    }
]);


const container = document.getElementById('root');
const root = createRoot(container)
root.render(<RouterProvider router={router}/>);


