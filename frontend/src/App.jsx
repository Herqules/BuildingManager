import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { createTheme } from '@mui/material/styles';
import Layout from './components/layout/Layout';
import Login from './components/auth/Login';
import CreateTicket from './components/tickets/CreateTicket';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<div>Welcome to Building Manager</div>} />
            <Route path="create-ticket" element={<CreateTicket />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;