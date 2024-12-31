import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  Radio,
  RadioGroup,
  FormControl,
  FormLabel,
} from '@mui/material';
import {
  Warning as WarningIcon,
  LocationOn as LocationIcon,
  Phone as PhoneIcon,
  Send as SendIcon,
} from '@mui/icons-material';

function EmergencyTicket() {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [confirmDialog, setConfirmDialog] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    contactNumber: '',
    emergencyType: 'maintenance',
    immediateAction: false,
    notifyManagement: true,
    notifySecurity: false,
  });

  const steps = ['Emergency Details', 'Location & Contact', 'Confirmation'];

  const emergencyTypes = [
    { value: 'maintenance', label: 'Maintenance Emergency' },
    { value: 'security', label: 'Security Issue' },
    { value: 'fire', label: 'Fire Related' },
    { value: 'water', label: 'Water/Flooding' },
    { value: 'electrical', label: 'Electrical Issue' },
  ];

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: e.target.type === 'checkbox' ? checked : value
    }));
  };

  const validateStep = () => {
    switch (activeStep) {
      case 0:
        if (!formData.title.trim() || !formData.description.trim() || !formData.emergencyType) {
          setError('Please fill in all required fields');
          return false;
        }
        break;
      case 1:
        if (!formData.location.trim() || !formData.contactNumber.trim()) {
          setError('Location and contact number are required');
          return false;
        }
        if (!/^\d{10}$/.test(formData.contactNumber.replace(/\D/g, ''))) {
          setError('Please enter a valid 10-digit phone number');
          return false;
        }
        break;
      default:
        break;
    }
    setError('');
    return true;
  };

  const handleNext = () => {
    if (validateStep()) {
      if (activeStep === steps.length - 1) {
        setConfirmDialog(true);
      } else {
        setActiveStep((prevStep) => prevStep + 1);
      }
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
    setError('');
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/tickets/emergency', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          ...formData,
          priority: 'emergency',
          status: 'urgent'
        })
      });

      if (!response.ok) throw new Error('Failed to create emergency ticket');

      const data = await response.json();
      
      // Send notifications if enabled
      if (formData.notifyManagement || formData.notifySecurity) {
        await sendEmergencyNotifications(data.ticketId);
      }

      navigate(`/tickets/${data.ticketId}`);
    } catch (err) {
      setError('Failed to create emergency ticket. Please try again or contact support directly.');
    } finally {
      setLoading(false);
      setConfirmDialog(false);
    }
  };

  const sendEmergencyNotifications = async (ticketId) => {
    try {
      await fetch('http://localhost:8000/api/notifications/emergency', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          ticketId,
          notifyManagement: formData.notifyManagement,
          notifySecurity: formData.notifySecurity
        })
      });
    } catch (error) {
      console.error('Failed to send notifications:', error);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Emergency Title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              margin="normal"
            />
            <TextField
              fullWidth
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={4}
              required
              margin="normal"
            />
            <FormControl component="fieldset" sx={{ mt: 2 }}>
              <FormLabel component="legend">Emergency Type</FormLabel>
              <RadioGroup
                name="emergencyType"
                value={formData.emergencyType}
                onChange={handleChange}
              >
                {emergencyTypes.map((type) => (
                  <FormControlLabel
                    key={type.value}
                    value={type.value}
                    control={<Radio />}
                    label={type.label}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </Box>
        );
      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              required
              margin="normal"
              InputProps={{
                startAdornment: <LocationIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
            <TextField
              fullWidth
              label="Contact Number"
              name="contactNumber"
              value={formData.contactNumber}
              onChange={handleChange}
              required
              margin="normal"
              InputProps={{
                startAdornment: <PhoneIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Box>
        );
      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.immediateAction}
                  onChange={handleChange}
                  name="immediateAction"
                />
              }
              label="Requires immediate action"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.notifyManagement}
                  onChange={handleChange}
                  name="notifyManagement"
                />
              }
              label="Notify building management"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.notifySecurity}
                  onChange={handleChange}
                  name="notifySecurity"
                />
              }
              label="Notify security team"
            />
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <WarningIcon color="error" sx={{ fontSize: 40, mr: 2 }} />
          <Typography variant="h4">
            Emergency Ticket
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            onClick={handleBack}
            disabled={activeStep === 0 || loading}
          >
            Back
          </Button>
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={loading}
            endIcon={activeStep === steps.length - 1 ? <SendIcon /> : null}
          >
            {activeStep === steps.length - 1 ? 'Submit' : 'Next'}
          </Button>
        </Box>
      </Paper>

      <Dialog
        open={confirmDialog}
        onClose={() => setConfirmDialog(false)}
      >
        <DialogTitle>
          Confirm Emergency Ticket
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to submit this emergency ticket? This will notify relevant personnel immediately.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setConfirmDialog(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit}
            color="error"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <WarningIcon />}
          >
            Confirm Emergency
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default EmergencyTicket; 