import React from 'react';
import { Box, AppBar, Toolbar, Typography, Button } from '@mui/material';
import { useNavigate, Outlet } from 'react-router-dom';

function Layout() {
  const navigate = useNavigate();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
        <Toolbar>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ flexGrow: 1, color: 'white' }}
          >
            Building Manager
          </Typography>
          <Button 
            color="inherit" 
            onClick={() => navigate('/create-ticket')}
            sx={{ color: 'white' }}
          >
            Create Ticket
          </Button>
          <Button 
            color="inherit" 
            onClick={() => navigate('/login')}
            sx={{ color: 'white' }}
          >
            Login
          </Button>
        </Toolbar>
      </AppBar>
      <Box sx={{ p: 3, flexGrow: 1 }}>
        <Typography variant="h4" sx={{ mb: 3, color: '#333' }}>
          Welcome to Building Manager
        </Typography>
        <Outlet />
      </Box>
    </Box>
  );
}

export default Layout; 