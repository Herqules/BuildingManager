import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { createTheme } from '@mui/material/styles';

// Layout and Auth
import Layout from './components/layout/Layout';
import { AuthProvider } from './components/auth/AuthContext';
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Ticket Components
import CreateTicket from './components/tickets/CreateTicket';
import TicketList from './components/tickets/TicketList';
import TicketDetails from './components/tickets/TicketDetails';
import EmergencyTicket from './components/tickets/EmergencyTicket';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    error: { main: '#f44336' },
    background: {
      default: '#f5f5f5'
    }
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected Routes */}
            <Route path="/" element={<Layout />}>
              <Route index element={<TicketList />} />
              <Route path="tickets" element={<TicketList />} />
              <Route path="tickets/:id" element={<TicketDetails />} />
              <Route path="create-ticket" element={<CreateTicket />} />
              <Route path="emergency-ticket" element={<EmergencyTicket />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 