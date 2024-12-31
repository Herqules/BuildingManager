import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Chip,
  Button,
  Divider,
  Grid,
  CircularProgress,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Comment as CommentIcon,
  Schedule as ScheduleIcon,
  Flag as FlagIcon,
} from '@mui/icons-material';

function TicketDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [comment, setComment] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);

  const fetchTicket = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch ticket details');

      const data = await response.json();
      setTicket(data);
      setError('');
    } catch (err) {
      setError('Error loading ticket details. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTicket();
  }, [id]);

  const handleAddComment = async () => {
    if (!comment.trim()) return;

    setUpdateLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${id}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ content: comment })
      });

      if (!response.ok) throw new Error('Failed to add comment');

      setComment('');
      fetchTicket(); // Refresh ticket data
    } catch (err) {
      setError('Error adding comment');
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      if (response.ok) {
        navigate('/tickets');
      } else {
        throw new Error('Failed to delete ticket');
      }
    } catch (err) {
      setError('Error deleting ticket');
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) throw new Error('Failed to update status');

      fetchTicket(); // Refresh ticket data
    } catch (err) {
      setError('Error updating ticket status');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!ticket) {
    return (
      <Container maxWidth="md">
        <Alert severity="error">Ticket not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            Ticket #{ticket.id}
          </Typography>
          <Box>
            <Button
              startIcon={<EditIcon />}
              onClick={() => navigate(`/tickets/${id}/edit`)}
              sx={{ mr: 1 }}
            >
              Edit
            </Button>
            <Button
              startIcon={<DeleteIcon />}
              color="error"
              onClick={() => setOpenDialog(true)}
            >
              Delete
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              {ticket.title}
            </Typography>
            <Typography variant="body1" paragraph>
              {ticket.description}
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Status
              </Typography>
              <Chip
                label={ticket.status}
                color={ticket.status === 'open' ? 'primary' : 'default'}
                sx={{ mb: 2 }}
              />
              
              <Typography variant="subtitle2" gutterBottom>
                Priority
              </Typography>
              <Chip
                label={ticket.priority}
                color={ticket.priority === 'high' ? 'error' : 'default'}
                sx={{ mb: 2 }}
              />
              
              <Typography variant="subtitle2" gutterBottom>
                Created
              </Typography>
              <Typography variant="body2">
                {new Date(ticket.created_at).toLocaleString()}
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Comments
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={3}
            placeholder="Add a comment..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            disabled={updateLoading}
          />
          <Button
            variant="contained"
            startIcon={<CommentIcon />}
            onClick={handleAddComment}
            disabled={updateLoading || !comment.trim()}
            sx={{ mt: 1 }}
          >
            Add Comment
          </Button>
        </Box>

        <Timeline>
          {ticket.comments?.map((comment, index) => (
            <TimelineItem key={index}>
              <TimelineSeparator>
                <TimelineDot color="primary" />
                {index < ticket.comments.length - 1 && <TimelineConnector />}
              </TimelineSeparator>
              <TimelineContent>
                <Typography variant="subtitle2">
                  {comment.user_name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {new Date(comment.created_at).toLocaleString()}
                </Typography>
                <Typography variant="body1" paragraph>
                  {comment.content}
                </Typography>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      </Paper>

      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
      >
        <DialogTitle>Delete Ticket</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this ticket? This action cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error">Delete</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default TicketDetails; 