import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';

function CreateTicket() {
  const [ticket, setTicket] = useState({
    title: '',
    description: '',
    priority: 'low',
    location: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/tickets/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(ticket)
      });

      if (response.ok) {
        setSuccess('Ticket created successfully!');
        setTicket({ title: '', description: '', priority: 'low', location: '' });
      } else {
        setError('Failed to create ticket');
      }
    } catch (err) {
      setError('Error creating ticket');
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Create New Ticket
        </Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Title"
            value={ticket.title}
            onChange={(e) => setTicket({...ticket, title: e.target.value})}
            margin="normal"
            required
          />
          
          <TextField
            fullWidth
            label="Description"
            value={ticket.description}
            onChange={(e) => setTicket({...ticket, description: e.target.value})}
            margin="normal"
            multiline
            rows={4}
            required
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Priority</InputLabel>
            <Select
              value={ticket.priority}
              onChange={(e) => setTicket({...ticket, priority: e.target.value})}
              label="Priority"
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="emergency">Emergency</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Location"
            value={ticket.location}
            onChange={(e) => setTicket({...ticket, location: e.target.value})}
            margin="normal"
            required
          />

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 3 }}
          >
            Submit Ticket
          </Button>
        </form>
      </Paper>
    </Container>
  );
}

export default CreateTicket; 